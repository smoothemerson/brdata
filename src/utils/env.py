import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://mcp:8001")
IBGE_BASE_URL = os.getenv("IBGE_BASE_URL", "https://servicodados.ibge.gov.br/api")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
