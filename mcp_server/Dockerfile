FROM python:3.13-slim

WORKDIR /app

RUN useradd --no-create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser /app

COPY pyproject.toml .
RUN pip install --no-cache-dir "fastmcp>=2.0" "httpx>=0.27" "uvicorn[standard]>=0.32"

COPY mcp_server/ mcp_server/

USER appuser

EXPOSE 8001

CMD ["python", "-m", "mcp_server.server"]
