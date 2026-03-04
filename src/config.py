from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_model: str = "llama3.2"
    ollama_base_url: str = "http://ollama:11434"
    postgres_url: str = "postgresql+asyncpg://ibge:ibge@postgres:5432/ibge"
    mcp_base_url: str = "http://mcp:8001"
    ibge_base_url: str = "https://servicodados.ibge.gov.br/api"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
