from pydantic import BaseModel
from typing import Optional

# --- Requests ---

class IngestRequest(BaseModel):
    github_url: Optional[str] = None      # public github repo URL
    collection_name: Optional[str] = "repo_chunks"  # allow custom collection
    github_token: str | None = None  # optional token for private repos or higher rate limits

class AskRequest(BaseModel):
    question: str
    collection_name: Optional[str] = "repo_chunks"

# --- Responses ---

class IngestResponse(BaseModel):
    status: str
    chunks_stored: int
    collection_name: str
    message: str

class RepoAnswer(BaseModel):
    answer: str
    relevant_files: list[str]
    confidence: str
    follow_up_suggestions: list[str]

class AskResponse(BaseModel):
    question: str
    result: RepoAnswer