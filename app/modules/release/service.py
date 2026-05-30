import json
from app.core.llm import get_llm
from app.core.prompts import RELEASE_NOTES_PROMPT
from app.modules.release.schema import ReleaseNotesResponse, ReleaseResult
from app.utils.text_utils import clean_llm_response


async def generate_release_notes(commits: list[str], version: str | None) -> ReleaseNotesResponse:
    # 1. join commits into a single string
    commits_text = "\n".join([f"- {commit}" for commit in commits])

    # 2. run through LLM chain
    chain = RELEASE_NOTES_PROMPT | get_llm()
    response = chain.invoke({"commits": commits_text})

    # 3. parse response
    raw = clean_llm_response(response.content)
    parsed = json.loads(raw)

    return ReleaseNotesResponse(
        version=version,
        result=ReleaseResult(**parsed)
    )