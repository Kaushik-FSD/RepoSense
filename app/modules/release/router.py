from fastapi import APIRouter, HTTPException
from app.modules.release.schema import ReleaseNotesRequest, ReleaseNotesResponse
from app.modules.release.service import generate_release_notes

router = APIRouter()

@router.post("/generate", response_model=ReleaseNotesResponse)
async def generate(req: ReleaseNotesRequest):
    try:
        return await generate_release_notes(req.commits, req.version)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))