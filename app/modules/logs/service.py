from curses import raw
import json
from app.core.llm import get_llm
from app.core.prompts import LOG_ANALYSIS_PROMPT
from app.modules.logs.schema import LogAnalyzeResponse, LogResult, LogError
from app.utils.text_utils import clean_llm_response

async def analyze_logs(logs: str) -> LogAnalyzeResponse:
    chain = LOG_ANALYSIS_PROMPT | get_llm()
    response = chain.invoke({"logs": logs})

    raw = response.content.strip()

    if not raw:
        raise ValueError("LLM returned empty response. Try again.")

    raw = clean_llm_response(response.content)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON: {raw[:200]}")

    errors = [LogError(**e) for e in parsed.get("errors", [])]

    return LogAnalyzeResponse(
        result=LogResult(
            summary=parsed["summary"],
            error_count=parsed["error_count"],
            errors=errors,
            patterns=parsed["patterns"],
            probable_root_causes=parsed["probable_root_causes"],
            recommended_actions=parsed["recommended_actions"],
        )
    )