import json
import httpx
from app.core.vectorstore import get_retriever
from app.core.llm import get_llm
from app.core.prompts import PR_SUMMARY_PROMPT
from app.modules.pr.schema import PRAnalyzeResponse, PRResult, KeyChange


def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    # https://github.com/owner/repo/pull/123
    parts = pr_url.rstrip("/").split("/")
    owner = parts[-4]
    repo = parts[-3]
    pr_number = int(parts[-1])
    return owner, repo, pr_number


async def fetch_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3.diff"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch PR: {response.status_code}")
        return response.text

def extract_filenames_from_diff(diff: str) -> str:
    """extract changed filenames from diff to use as retrieval query"""
    filenames = []
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            # line looks like: diff --git a/src/auth/middleware.ts b/src/auth/middleware.ts
            parts = line.split(" ")
            filename = parts[-1].replace("b/", "")
            filenames.append(filename)
    return " ".join(filenames)

async def analyze_pr(pr_url: str, collection_name: str) -> PRAnalyzeResponse:
    # 1. parse url and fetch diff
    owner, repo, pr_number = parse_pr_url(pr_url)
    diff = await fetch_pr_diff(owner, repo, pr_number)

    # 2. retrieve related code context from vectorstore
    retriever = get_retriever(collection_name)
    query = extract_filenames_from_diff(diff)
    # docs = retriever.invoke(diff[:500])  # use first 500 chars of diff as query
    docs = retriever.invoke(query)
    context = "\n\n".join([
        f"# {doc.metadata.get('filename', 'unknown')}\n{doc.page_content}"
        for doc in docs
    ])

    # 3. run through LLM chain
    chain = PR_SUMMARY_PROMPT | get_llm()
    response = chain.invoke({"diff": diff, "context": context})

    # 4. parse response
    parsed = json.loads(response.content.strip())
    key_changes = [KeyChange(**kc) for kc in parsed.get("key_changes", [])]

    return PRAnalyzeResponse(
        pr_url=pr_url,
        result=PRResult(
            summary=parsed["summary"],
            changed_modules=parsed["changed_modules"],
            change_type=parsed["change_type"],
            risk_level=parsed["risk_level"],
            risk_reasons=parsed["risk_reasons"],
            key_changes=key_changes,
            review_suggestions=parsed["review_suggestions"],
        )
    )

"""
FLOW OF THHIS MODULE/FUNCTIONALITY:

GitHub API
    │
    └──→ fetch full PR diff
              │
              ├──→ extract filenames from diff
              │         │
              │         └──→ ChromaDB search
              │                   │
              │                   └──→ returns related code chunks (context)
              │
              └──→ LLM gets both:
                    - full diff      (what changed)
                    - related chunks (what exists in repo)
                          │
                          └──→ structured response
"""