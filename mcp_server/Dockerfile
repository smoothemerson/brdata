FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir "fastmcp>=2.0" "httpx>=0.27" "uvicorn[standard]>=0.32"

COPY mcp_server/ mcp_server/

EXPOSE 8001

CMD ["python", "-m", "mcp_server.server"]
