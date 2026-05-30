from functools import lru_cache
from app.config import get_settings
import chromadb
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_chroma import Chroma
from app.core.embeddings import get_embeddings

COLLECTION_REPO = "repo_chunks"
COLLECTION_LOGS = "log_chunks"
COLLECTION_PR = "pr_chunks"

@lru_cache()
def get_chroma_client() -> chromadb.PersistentClient:
    settings = get_settings()
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

def get_vectorstore(collection_name: str) -> Chroma:
    return Chroma(
        client = get_chroma_client(),
        collection_name = collection_name,
        embedding_function = get_embeddings()
    )

# def get_retriever(collection_name: str, top_k: int | None = None) -> VectorStoreRetriever:
#     settings = get_settings()
#     k = top_k or settings.RETRIEVAL_TOP_K

#     return get_vectorstore(collection_name).as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": k},
#     )

def get_retriever(collection_name: str, top_k: int | None = None) -> VectorStoreRetriever:
    settings = get_settings()
    client = get_chroma_client()
    existing = [c.name for c in client.list_collections()]
    if collection_name not in existing:
        raise ValueError(f"Collection '{collection_name}' not found. Please ingest a repo first.")
    
    k = top_k or settings.RETRIEVAL_TOP_K
    return get_vectorstore(collection_name).as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )

# def delete_collection(collection_name: str) -> None:
#     get_chroma_client().delete_collection(name = collection_name)

def delete_collection(collection_name: str) -> None:
    client = get_chroma_client()
    existing = [c.name for c in client.list_collections()]
    if collection_name in existing:
        client.delete_collection(name=collection_name)