from pydantic_settings import BaseSettings
from functools import lru_cache

# That means config.py is the configuration contract, 
# and .env is one way to supply runtime values.
# This file is the single source of truth for all configuration values,
class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    MISTRAL_MODEL: str = "mistral-small-2603"
    HUGGINGFACEHUB_API_TOKEN: str = ""
    MISTRAL_API_KEY: str = ""
    LLM_PROVIDER: str = "groq"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./storage/chroma"

    RETRIEVAL_TOP_K: int = 5
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    APP_NAME: str = "RepoSense"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()