from fastapi import APIRouter, HTTPException
from app.modules.pr.schema import PRAnalyzeRequest, PRAnalyzeResponse
from app.modules.pr.service import analyze_pr

router = APIRouter()

@router.post("/analyze", response_model=PRAnalyzeResponse)
async def analyze(req: PRAnalyzeRequest):
    try:
        return await analyze_pr(req.pr_url, req.collection_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))