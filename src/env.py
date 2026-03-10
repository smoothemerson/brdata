import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL: str = os.environ["OLLAMA_MODEL"]
OLLAMA_BASE_URL: str = os.environ["OLLAMA_BASE_URL"]
MCP_BASE_URL: str = os.environ["MCP_BASE_URL"]
IBGE_BASE_URL: str = os.environ["IBGE_BASE_URL"]
