from fastapi import APIRouter, HTTPException
from app.modules.repo.schema import IngestRequest, IngestResponse, AskRequest, AskResponse
from app.modules.repo.service import ingest_repo, ask_repo

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    try:
        return ingest_repo(req.github_url, req.collection_name, req.github_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    try:
        return ask_repo(req.question, req.collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))