# PRD: IBGE Conversational Agent

## Overview

A conversational agent that answers analytical questions about Brazil in natural language. The agent connects to the IBGE public API via a custom MCP Server, uses Ollama (llama3.2) as the local LLM, and exposes a REST API via FastAPI.

The project uses the **Ralph Loop** pattern: `ralph.sh` drives an autonomous Claude agent that reads `PRD.md` for requirements and `features.json` for the task backlog, implements one task at a time, commits, and marks each feature as `passes: true`.

## Goals

- Answer natural-language questions about Brazilian geography, demographics, and statistics
- Use only real data from the official IBGE API — never hallucinate statistics
- Keep all services local: no external LLM APIs, no paid services
- Fully containerized via Docker Compose; one command to start everything

---

## Architecture

```
Client → FastAPI :8000 → LangChain Agent → MCP Server :8001 → IBGE API
                              ↓
                         Ollama :11434
```

---

## Services

| Service  | Image / Build       | Port | Health Check |
|----------|---------------------|------|--------------|
| api      | ./Dockerfile        | 8000 | GET /health → 200 |
| mcp      | ./mcp_server/Dockerfile | 8001 | GET /health → 200 |
| ollama   | ollama/ollama:latest | 11434 | GET /api/tags → llama3.2 present |

`api` depends_on `mcp` and `ollama` with `condition: service_healthy`.

---

## IBGE API Tools

| Tool | IBGE Endpoint | Description |
|------|---------------|-------------|
| `ibge_get_states` | `GET /v1/localidades/estados` | All 27 Brazilian states with region info |
| `ibge_get_municipalities` | `GET /v1/localidades/estados/{uf}/municipios` | Municipalities for a given state (2-letter UF code) |

---

## FastAPI Endpoints

### POST /chat
**Request:**
```json
{
  "question": "Qual é a população do Brasil?"
}
```
**Response:**
```json
{
  "answer": "De acordo com os dados do IBGE..."
}
```

### GET /health
**Response:**
```json
{
  "healthy": true
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COMPOSE_PROFILES` | `cpu` | Ollama profile: `cpu`, `gpu-amd`, `gpu-nvidia` |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama service URL |
| `MCP_BASE_URL` | `http://mcp:8001/mcp` | MCP server URL |
| `IBGE_BASE_URL` | `https://servicodados.ibge.gov.br/api` | IBGE API base URL |

---

## Project Directory Structure

```
brdata/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── pyproject.toml
├── requirements.txt
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
│   ├── env.py                         # Environment config
│   └── tools/
│       ├── __init__.py
│       └── location.py                # ibge_get_states, ibge_get_municipalities
└── src/
    ├── main.py                        # FastAPI app with lifespan
    ├── env.py                         # Environment config
    ├── agent/
    │   ├── __init__.py
    │   ├── agent.py                   # create_agent() + agent_call()
    │   └── prompt.py                  # System prompt
    ├── mcp/
    │   ├── __init__.py
    │   └── client.py                  # langchain-mcp-adapters, load_mcp_tools()
    └── routes/
        ├── __init__.py
        ├── chat.py                    # POST /chat
        ├── health.py                  # GET /health
        └── responses.py               # Pydantic request/response models
```

---

## CI Pipeline

One GitHub Actions job triggered on push/PR to `main`:

1. **lint** — `ruff check src/ mcp_server/`

---

## Non-Goals

- Streaming responses (WebSocket or SSE) — `/chat` is synchronous
- Authentication / API keys — open access
- Fine-tuning or RAG — agent uses tools only, no vector store
- Production hardening (rate limiting, circuit breakers, metrics)
- Support for LLM providers other than Ollama
- Persistence / query history

---

## Implementation Order

| ID  | Title | Category |
|-----|-------|----------|
| F01 | Docker Compose Skeleton | infrastructure |
| F03 | MCP Service Dockerfile and Requirements | infrastructure |
| F04 | API Service Dockerfile and Requirements | infrastructure |
| F05 | MCP Tool: ibge_get_states | mcp |
| F06 | MCP Tool: ibge_get_municipalities | mcp |
| F11 | LangChain Agent (create_agent) | agent |
| F12 | MCP Client Bootstrap in Agent | agent |
| F14 | POST /chat Endpoint | api |
| F16 | GET /health Endpoint | api |
| F17 | GitHub Actions CI Pipeline | ci |
