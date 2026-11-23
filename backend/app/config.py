from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    DATABASE_URL: str = "./data/verigreen.db"
    CHROMA_PATH: str = "./data/chroma"
    DATA_DIR: str = "./data"
    REPORT_DIR: str = "./data/files/reports"
    BADGE_DIR: str = "./data/files/badges"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
