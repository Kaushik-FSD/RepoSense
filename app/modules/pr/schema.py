from pydantic import BaseModel

class KeyChange(BaseModel):
    file: str
    change: str

class PRAnalyzeRequest(BaseModel):
    pr_url: str
    collection_name: str = "repo_chunks"

class PRResult(BaseModel):
    summary: str
    changed_modules: list[str]
    change_type: str
    risk_level: str
    risk_reasons: list[str]
    key_changes: list[KeyChange]
    review_suggestions: list[str]

class PRAnalyzeResponse(BaseModel):
    pr_url: str
    result: PRResult