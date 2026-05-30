import shutil
import os
from fastapi import APIRouter
from app.core.vectorstore import delete_all_collections

router = APIRouter()

@router.delete("/cleanup")
async def cleanup():
    # 1. delete all chroma collections
    delete_all_collections()

    # 2. wipe chroma storage folder
    if os.path.exists("./storage/chroma"):
        shutil.rmtree("./storage/chroma")
        os.makedirs("./storage/chroma")

    # 3. wipe uploads folder
    if os.path.exists("./storage/uploads"):
        shutil.rmtree("./storage/uploads")
        os.makedirs("./storage/uploads")

    return {
        "status": "success",
        "message": "Cleared all collections, chroma storage and uploads."
    }