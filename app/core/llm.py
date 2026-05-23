from functools import lru_cache
from app.config import get_settings
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_core.language_models.chat_models import BaseChatModel

@lru_cache()
def get_llm() -> BaseChatModel:
    settings = get_settings()

    if settings.LLM_PROVIDER.lower() == "groq":
        return ChatGroq(
            api_key = settings.GROQ_API_KEY,
            model = settings.GROQ_MODEL,
            temperature = settings.LLM_TEMPERATURE,
            max_tokens = settings.LLM_MAX_TOKENS
        )
    elif settings.LLM_PROVIDER.lower() == "mistral":
        return ChatMistralAI(
            api_key = settings.MISTRAL_API_KEY,
            model = settings.MISTRAL_MODEL,
            temperature = settings.LLM_TEMPERATURE,
            max_tokens = settings.LLM_MAX_TOKENS
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")