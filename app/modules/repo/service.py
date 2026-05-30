import os
import subprocess
import json
import shutil
from langchain_core.documents import Document
from app.core.vectorstore import get_vectorstore, get_retriever, delete_collection, COLLECTION_REPO
from app.core.llm import get_llm
from app.core.prompts import REPO_QA_PROMPT
from app.modules.repo.chunker import load_documents_from_repo, chunk_documents, load_repo_metadata
from app.modules.repo.schema import IngestResponse, AskResponse, RepoAnswer


CLONE_DIR = "./storage/uploads/repo"

def build_clone_url(github_url: str, token: str | None) -> str:
    if token:
        return github_url.replace("https://", f"https://{token}@")
    return github_url

def clone_repo(clone_url: str, clone_dir: str) -> int:
    result = subprocess.run(
        ["git", "clone", clone_url, clone_dir],
        timeout=30,  # 30 seconds max
        capture_output=True,
        text=True
    )
    return result.returncode

def ingest_repo(github_url: str, collection_name: str, github_token: str | None = None) -> IngestResponse:
    # 1. clean previous clone if exists
    if os.path.exists(CLONE_DIR):
        shutil.rmtree(CLONE_DIR)

    # 2. clone the repo
    clone_url = build_clone_url(github_url, github_token)

    # Note: subprocess.run with timeout will raise TimeoutExpired if it exceeds the time limit, which we catch and convert to a ValueError for consistent error handling in the API layer.
    try:
        exit_code = clone_repo(clone_url, CLONE_DIR)
    except subprocess.TimeoutExpired:
        raise ValueError("Cloning timed out. Check the URL or token and try again.")


    if exit_code != 0:
        if github_token is None:
            raise ValueError("Failed to clone repo. If this is a private repo, please provide a github_token.")
        else:
            raise ValueError("Failed to clone repo. Please check if the token has correct permissions.")

    # 3. load files into Documents
    documents = load_documents_from_repo(CLONE_DIR)
    metadata_docs = load_repo_metadata(CLONE_DIR)
    if not documents and not metadata_docs:
        raise ValueError("No supported files found in the repository.")

    # 4. chunk documents
    all_documents = metadata_docs + documents
    chunks = chunk_documents(all_documents)

    # 5. wipe old collection and store fresh chunks
    delete_collection(collection_name)
    vectorstore = get_vectorstore(collection_name)
    # wipes data but keeps same collection UUID
    # vectorstore.reset_collection()
    vectorstore.add_documents(chunks)

    return IngestResponse(
        status="success",
        chunks_stored=len(chunks),
        collection_name=collection_name,
        message=f"Ingested {len(documents)} files into {len(chunks)} chunks."
    )


def ask_repo(question: str, collection_name: str) -> AskResponse:
    # 1. retrieve relevant chunks
    retriever = get_retriever(collection_name)
    docs: list[Document] = retriever.invoke(question)

    # 2. build context string from retrieved chunks
    context = "\n\n".join([
        f"# {doc.metadata.get('filename', 'unknown')}\n{doc.page_content}"
        for doc in docs
    ])

    # 3. run through LLM chain
    chain = REPO_QA_PROMPT | get_llm()
    response = chain.invoke({"context": context, "question": question})

    # 4. parse JSON response into Pydantic model
    raw = response.content.strip()
    parsed = json.loads(raw)

    return AskResponse(
        question=question,
        result=RepoAnswer(**parsed)
    )