from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_provider: str = "openai"  # openai | huggingface
    openai_api_key: str | None = None
    huggingface_api_key: str | None = None
    model_llm: str = "gpt-4.1"
    model_embeddings: str = "text-embedding-3-large"
    base_dir_saida: str = "./saida"
    base_dir_conversas: str = "./data/conversas"
    git_auto_commit: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
