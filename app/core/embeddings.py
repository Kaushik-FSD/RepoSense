from functools import lru_cache
from app.config import get_settings
from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache()
def get_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()

    return HuggingFaceEmbeddings(
        model = settings.EMBEDDING_MODEL,
        model_kwargs = {
            "device": "cpu"
        },
        encode_kwargs = {
            "normalize_embeddings": True
        }
    )