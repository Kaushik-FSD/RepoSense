from fastapi import APIRouter, HTTPException
from app.modules.logs.schema import LogAnalyzeRequest, LogAnalyzeResponse
from app.modules.logs.service import analyze_logs

router = APIRouter()

@router.post("/analyze", response_model=LogAnalyzeResponse)
async def analyze(req: LogAnalyzeRequest):
    try:
        return await analyze_logs(req.logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))