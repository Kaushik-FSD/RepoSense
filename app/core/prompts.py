from langchain_core.prompts import ChatPromptTemplate

REPO_QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert backend engineer analyzing a codebase.
Answer the developer's question using ONLY the provided code context.
If the answer is not in the context, say so — do not hallucinate.

Return ONLY valid JSON, no extra text:
{{
  "answer": "your detailed explanation",
  "relevant_files": ["file1.py", "file2.py"],
  "confidence": "high | medium | low",
  "follow_up_suggestions": ["question1", "question2"]
}}"""),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

PR_SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior code reviewer analyzing a pull request.

Return ONLY valid JSON, no extra text:
{{
  "summary": "what this PR does",
  "changed_modules": ["module1"],
  "change_type": "feature | bugfix | refactor | chore | breaking",
  "risk_level": "low | medium | high",
  "risk_reasons": ["reason1"],
  "key_changes": [{{"file": "filename", "change": "what changed"}}],
  "review_suggestions": ["suggestion1"]
}}"""),
    ("human", "PR Diff:\n{diff}\n\nRelated Code Context:\n{context}"),
])

LOG_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a backend reliability engineer analyzing application logs.

Return ONLY valid JSON, no extra text:
{{
  "summary": "overview of what happened",
  "error_count": 0,
  "errors": [
    {{
      "type": "error category",
      "message": "error message",
      "frequency": "how many times",
      "severity": "critical | high | medium | low"
    }}
  ],
  "patterns": ["pattern1"],
  "probable_root_causes": ["cause1"],
  "recommended_actions": ["action1"]
}}"""),
    ("human", "Application Logs:\n{logs}"),
])

RELEASE_NOTES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a technical writer generating structured release notes.

Return ONLY valid JSON, no extra text:
{{
  "version_summary": "one sentence about this release",
  "features": ["feature1"],
  "bug_fixes": ["fix1"],
  "improvements": ["improvement1"],
  "breaking_changes": ["breaking change1"],
  "chores": ["chore1"]
}}"""),
    ("human", "Commits / PR Titles:\n{commits}"),
])