# PRD: IBGE Conversational Agent

## Overview

A conversational agent that answers analytical questions about Brazil in natural language. The agent connects to the IBGE public API via a custom MCP Server, uses Ollama (llama3.2) as the local LLM, persists all queries and tool calls in PostgreSQL, and exposes a REST API via FastAPI.

The project uses the **Ralph Loop** pattern: `ralph.sh` drives an autonomous Claude agent that reads `PRD.md` for requirements and `features.json` for the task backlog, implements one task at a time, commits, and marks each feature as `passes: true`.

## Goals

- Answer natural-language questions about Brazilian geography, demographics, and statistics
- Use only real data from the official IBGE API — never hallucinate statistics
- Persist every interaction (question, answer, tools used, latency) for auditability
- Keep all services local: no external LLM APIs, no paid services
- Fully containerized via Docker Compose; one command to start everything

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User / Client                         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI  (api:8000)                         │
│                                                             │
│   POST /chat   GET /history   GET /health                   │
│        │                                                    │
│   ┌────▼──────────────────────────────┐                    │
│   │       LangGraph ReAct Agent        │                    │
│   │  START → assistant → tools_cond   │                    │
│   │           ↑              │        │                    │
│   │           └── tools ◄────┘        │                    │
│   │        ChatOllama (llama3.2)       │                    │
│   └────────────────┬──────────────────┘                    │
│                    │ MCP over HTTP                          │
└────────────────────┼────────────────────────────────────────┘
                     │
        ┌────────────▼───────────┐
        │   MCP Server (mcp:8001) │
        │   FastMCP + 6 tools     │
        │                        │
        │  get_states             │
        │  get_municipalities     │
        │  get_population         │
        │  search_aggregates      │
        │  get_aggregate_data     │
        │  get_name_frequency     │
        └────────────┬───────────┘
                     │ HTTPS
                     ▼
        ┌────────────────────────┐
        │   IBGE Public API      │
        │ servicodados.ibge.gov.br│
        └────────────────────────┘

┌─────────────────────┐      ┌─────────────────────┐
│  PostgreSQL (5432)  │      │   Ollama (11434)     │
│  queries table      │      │   llama3.2 model     │
│  tool_calls table   │      │                     │
└─────────────────────┘      └─────────────────────┘
```

---

## Services

| Service  | Image / Build       | Port | Health Check |
|----------|---------------------|------|--------------|
| api      | ./Dockerfile        | 8000 | GET /health → 200 |
| mcp      | ./mcp_server/Dockerfile | 8001 | GET /health → 200 |
| postgres | postgres:16         | 5432 | pg_isready |
| ollama   | ollama/ollama:latest | 11434 | GET /api/tags → llama3.2 present |

`api` depends_on `postgres`, `mcp`, `ollama` with `condition: service_healthy`.

---

## IBGE API Tools

| Tool | IBGE Endpoint | Description |
|------|---------------|-------------|
| `get_states` | `GET /v1/localidades/estados` | All Brazilian states with region info |
| `get_municipalities` | `GET /v1/localidades/estados/{uf}/municipios` | Municipalities for a given state (2-letter UF code) |
| `get_population` | `GET /v3/agregados/1705/periodos/-1/variaveis/614?localidades=N3[all]` | Population by state, most recent census |
| `search_aggregates` | `GET /v3/agregados?pesquisa={keyword}` | Search IBGE aggregate tables by keyword |
| `get_aggregate_data` | `GET /v3/agregados/{id}/periodos/{period}/variaveis/{variable}` | Fetch specific aggregate data |
| `get_name_frequency` | `GET /v2/censos/nomes/{name}` | Name frequency across census decades |

---

## FastAPI Endpoints

### POST /chat
**Request:**
```json
{
  "question": "Qual é a população do Brasil?",
  "session_id": "optional-uuid"
}
```
**Response:**
```json
{
  "answer": "De acordo com os dados do IBGE...",
  "tools_used": [{"tool_name": "get_population", "params": {}, "result": {...}}],
  "latency_ms": 4200,
  "query_id": "uuid"
}
```

### GET /history
**Query params:** `session_id` (optional), `limit` (default 20)
**Response:** Array of query records with question, answer, tools_used, latency_ms, created_at

### GET /health
**Response:**
```json
{
  "healthy": true,
  "services": [
    {"name": "postgres", "ok": true, "detail": null},
    {"name": "mcp", "ok": true, "detail": null},
    {"name": "ollama", "ok": true, "detail": null},
    {"name": "ibge", "ok": true, "detail": null}
  ]
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama service URL |
| `POSTGRES_URL` | `postgresql+asyncpg://user:pass@postgres:5432/ibge` | Async DB connection string |
| `MCP_BASE_URL` | `http://mcp:8001` | MCP server base URL |
| `IBGE_BASE_URL` | `https://servicodados.ibge.gov.br/api` | IBGE API base URL |
| `POSTGRES_USER` | `ibge` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `ibge` | PostgreSQL password |
| `POSTGRES_DB` | `ibge` | PostgreSQL database name |

---

## Database Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS queries (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID,
    question    TEXT        NOT NULL,
    answer      TEXT,
    tools_used  JSONB,
    latency_ms  INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_queries_session_id ON queries (session_id);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries (created_at DESC);

CREATE TABLE IF NOT EXISTS tool_calls (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id    UUID        NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    tool_name   TEXT        NOT NULL,
    params      JSONB       NOT NULL DEFAULT '{}',
    result      JSONB,
    error       TEXT,
    called_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_query_id ON tool_calls (query_id);
```

---

## Project Directory Structure

```
ralph_loop_rocketseat/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── pyproject.toml
├── PRD.md
├── features.json
├── ralph.sh
├── Dockerfile                         # api service
├── .github/
│   └── workflows/
│       └── ci.yml
├── mcp_server/
│   ├── Dockerfile
│   ├── __init__.py
│   ├── server.py                      # FastMCP entrypoint, port 8001
│   ├── ibge_client.py                 # httpx async client wrapper
│   └── tools/
│       ├── __init__.py
│       ├── localidades.py             # get_states, get_municipalities
│       ├── agregados.py               # search_aggregates, get_aggregate_data, get_population
│       └── nomes.py                   # get_name_frequency
├── src/
│   ├── main.py                        # FastAPI app with lifespan
│   ├── config.py                      # pydantic-settings BaseSettings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── schemas.py                 # Pydantic request/response models
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── chat.py                # POST /chat
│   │       ├── history.py             # GET /history
│   │       └── health.py              # GET /health
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                   # LangGraph StateGraph (ReAct pattern)
│   │   ├── nodes.py                   # agent_node, tool_node_with_tracking
│   │   ├── state.py                   # AgentState TypedDict
│   │   └── prompts.py                 # System prompt
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── client.py                  # langchain-mcp-adapters, load_mcp_tools()
│   └── db/
│       ├── __init__.py
│       ├── connection.py              # async engine + session factory
│       ├── models.py                  # SQLAlchemy ORM models
│       └── repository.py              # save_query(), get_history()
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_tools_localidades.py
    │   ├── test_tools_agregados.py
    │   └── test_tools_nomes.py
    └── integration/
        ├── __init__.py
        └── test_health.py
```

---

## CI Pipeline

Three GitHub Actions jobs triggered on push/PR to `main`:

1. **lint** — `ruff check src/ mcp_server/ tests/`
2. **unit-tests** — `pytest tests/unit/ -v` (no Docker, mocked httpx)
3. **integration-test** — `pytest tests/integration/ -v` (mocked downstream calls, no Docker)

`unit-tests` and `integration-test` both `needs: lint`.

---

## Non-Goals

- Streaming responses (WebSocket or SSE) — `/chat` is synchronous
- Authentication / API keys — open access
- Multi-tenant isolation — session_id is advisory only
- Fine-tuning or RAG — agent uses tools only, no vector store
- Production hardening (rate limiting, circuit breakers, metrics)
- Support for LLM providers other than Ollama

---

## Implementation Order

| ID  | Title | Category |
|-----|-------|----------|
| F01 | Docker Compose Skeleton | infrastructure |
| F02 | PostgreSQL Schema Initialization | infrastructure |
| F03 | MCP Service Dockerfile and Requirements | infrastructure |
| F04 | API Service Dockerfile and Requirements | infrastructure |
| F05 | MCP Tool: get_states | mcp |
| F06 | MCP Tool: get_municipalities | mcp |
| F07 | MCP Tool: get_population | mcp |
| F08 | MCP Tool: search_aggregates | mcp |
| F09 | MCP Tool: get_aggregate_data | mcp |
| F10 | MCP Tool: get_name_frequency | mcp |
| F11 | LangGraph Agent State and Graph Definition | agent |
| F12 | MCP Client Bootstrap in Agent | agent |
| F13 | Tool Call Interception and Persistence | agent |
| F14 | POST /chat Endpoint | api |
| F15 | GET /history Endpoint | api |
| F16 | GET /health Endpoint | api |
| F17 | GitHub Actions CI Pipeline | ci |
