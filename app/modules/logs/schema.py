from pydantic import BaseModel

class LogError(BaseModel):
    type: str
    message: str
    frequency: str
    severity: str
    suggested_fix: str

class LogAnalyzeRequest(BaseModel):
    logs: str

class LogResult(BaseModel):
    summary: str
    error_count: int
    errors: list[LogError]
    patterns: list[str]
    probable_root_causes: list[str]
    recommended_actions: list[str]

class LogAnalyzeResponse(BaseModel):
    result: LogResult