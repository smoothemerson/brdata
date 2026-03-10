# ibge-agent

Conversational agent that answers analytical questions about Brazil using real data from the [IBGE public API](https://servicodados.ibge.gov.br). Runs entirely locally via Docker Compose.

## Architecture

```
Client → FastAPI :8000 → LangChain Agent → MCP Server :8001 → IBGE API
                              ↓
                         Ollama :11434
```

## Requirements

- Docker + Docker Compose
- Ollama with `llama3.2` pulled

## Setup

```bash
cp .env.example .env
# Edit .env: set COMPOSE_PROFILES to cpu, gpu-amd, or gpu-nvidia
docker compose up
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `COMPOSE_PROFILES` | `cpu` | Ollama profile: `cpu`, `gpu-amd`, `gpu-nvidia` |
| `OLLAMA_MODEL` | `llama3.2` | Model name to use |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama service URL |
| `MCP_BASE_URL` | `http://mcp:8001/mcp` | MCP server URL |
| `IBGE_BASE_URL` | `https://servicodados.ibge.gov.br/api` | IBGE API base URL |

## API

### POST /chat
```json
// Request
{ "question": "Quais são os estados do Brasil?" }

// Response
{ "answer": "..." }
```

### GET /health
```json
{ "healthy": true }
```

## MCP Tools

| Tool | Description |
|---|---|
| `ibge_get_states` | All 27 Brazilian states with region info |
| `ibge_get_municipalities` | Municipalities for a given state (2-letter UF code) |

## Local Development

```bash
# Terminal 1 — MCP server
uv run python -m mcp_server.server

# Terminal 2 — API
uv run python -m src.main
```

Set `MCP_BASE_URL=http://localhost:8001/mcp` and `OLLAMA_BASE_URL=http://localhost:11434` in `.env` for local runs.
