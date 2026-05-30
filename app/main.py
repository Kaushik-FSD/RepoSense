from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

from app.modules.repo.router import router as repo_router
from app.modules.pr.router import router as pr_router
from app.modules.logs.router import router as logs_router
from app.modules.release.router import router as release_router
from app.modules.admin.router import router as admin_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
    }

# Admin cleanup router
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


app.include_router(repo_router, prefix="/repo", tags=["Repo Assistant"])
app.include_router(pr_router, prefix="/pr", tags=["PR Summarizer"])
app.include_router(logs_router, prefix="/logs", tags=["Log Analyzer"])
app.include_router(release_router, prefix="/release", tags=["Release Notes"])