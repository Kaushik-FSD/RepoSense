from pydantic import BaseModel

class ReleaseNotesRequest(BaseModel):
    commits: list[str]
    version: str | None = None

class ReleaseResult(BaseModel):
    version_summary: str
    features: list[str]
    bug_fixes: list[str]
    improvements: list[str]
    breaking_changes: list[str]
    chores: list[str]

class ReleaseNotesResponse(BaseModel):
    version: str | None
    result: ReleaseResult