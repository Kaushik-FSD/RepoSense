# RepoSense

> An AI-powered backend engineering assistant that understands your codebase, analyzes pull requests, diagnoses logs, and generates release notes — built with FastAPI, LangChain, RAG pipelines, and free LLM APIs.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![LangChain](https://img.shields.io/badge/LangChain-0.3-white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20Mistral-purple)

---

## What is RepoSense?

RepoSense is an AI assistant built specifically for backend engineers. It solves a common problem — understanding an unfamiliar codebase, reviewing a large PR, diagnosing production logs, or writing release notes — tasks that take hours of manual effort.

Instead of reading every file yourself, you point RepoSense at your repository and ask questions. It understands the code, retrieves the right context, and gives you structured, actionable answers powered by LLMs.

---

## What Problem It Solves

Backend engineers spend significant time on tasks that don't require writing new code:

- **"How does authentication work in this repo?"** — Instead of tracing through 10 files, ask RepoSense directly
- **"What does this PR change and is it risky?"** — Instead of reading every diff line, get a structured risk analysis
- **"Why is production throwing these errors?"** — Instead of manually scanning logs, get root cause suggestions
- **"Write release notes for this sprint"** — Instead of going through git log, generate structured changelogs instantly

RepoSense handles all of these through a single API.

---

## High-Level Architecture

RepoSense is built as a **modular monolith** with FastAPI. Each feature lives as a self-contained module with its own router, service, and schemas. Shared infrastructure (LLM, embeddings, vector store) lives in `core/` and is reused across all modules.

```
API Client
    │
    ▼
┌─────────────────────────────────────────┐
│           FastAPI Application           │
│                                         │
│   /repo    /pr    /logs    /release     │
│         /health   /admin                │
└──────────┬──────────────────┬───────────┘
           │                  │
┌──────────▼──────────┐  ┌────▼────────────────────┐
│  ChromaDB (local)   │  │     Groq / Mistral       │
│                     │  │                          │
│  repo_chunks        │  │  Llama 3.3 70B           │
│  log_chunks         │  │  Mistral Small (fallback)│
│  pr_chunks          │  └──────────────────────────┘
└─────────────────────┘
           │
┌──────────▼──────────┐
│  HuggingFace (local)│
│  all-MiniLM-L6-v2   │
│  (embeddings)       │
└─────────────────────┘
```

---

## Key Technical Deep Dives

### 1. RAG Pipeline — Retrieval Augmented Generation

RepoSense doesn't just pass your question to the LLM directly. It first retrieves the most relevant code chunks from ChromaDB, then injects them as context into the prompt. This means the LLM answers based on your actual codebase — not generic knowledge.

```
Repository Files
    │
    ├── Parse supported file types (.py, .ts, .java, .go, .md ...)
    ├── Skip noise files (package-lock.json, yarn.lock, .git ...)
    ├── Chunk into 512-token pieces with 64-token overlap
    ├── Embed each chunk with all-MiniLM-L6-v2 (local, free)
    └── Store in ChromaDB with metadata (filename, language)

User Question
    │
    ├── Embed question with same model
    ├── Semantic search → top 5 most relevant chunks
    ├── Inject chunks as context into prompt
    └── LLM generates structured JSON response
```

### 2. Structured Outputs — No Raw Strings

Every LLM response in RepoSense is a structured Pydantic model — never a raw string. Each prompt instructs the LLM to return JSON in a specific shape. Services parse that JSON and validate it through Pydantic before returning to the API consumer.

This means the API always returns predictable, typed responses that can be filtered, stored, or displayed by any frontend or CLI tool.

### 3. Code-Aware Chunking

Code files are split using `RecursiveCharacterTextSplitter` which tries to split on logical boundaries (functions, classes, blocks) before splitting mid-line. Each chunk carries metadata — `filename`, `filepath`, `language` — so retrieval can surface not just the content but which file it came from.

Lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock` etc.) are explicitly excluded — they are auto-generated noise that pollutes retrieval results.

### 4. PR Analysis with GitHub API

PR analysis doesn't require manually copying diffs. RepoSense fetches the PR diff directly from GitHub's API using the PR URL. It then extracts changed filenames from the diff to query ChromaDB for related existing code — giving the LLM both what changed and what the surrounding codebase looks like.

```
PR URL → GitHub API → full diff
    │
    ├── extract changed filenames from diff
    ├── query ChromaDB with filenames → related code context
    └── LLM gets: full diff + related context → structured analysis
```

### 5. Provider-Agnostic LLM Client

The LLM client is completely provider-agnostic. Switching between Groq and Mistral is a single `.env` change — `LLM_PROVIDER=groq` or `LLM_PROVIDER=mistral`. Both use the same LangChain `BaseChatModel` interface so no other code changes are needed.

### 6. Local Embeddings — Zero Cost

Embeddings run entirely on your machine using HuggingFace's `all-MiniLM-L6-v2`. No API calls, no rate limits, no cost. The model weights are downloaded once and cached. On Apple Silicon, this runs fast enough for real-time use.

---

## Tech Stack

| Technology | Role | Why |
|---|---|---|
| **FastAPI** | API Framework | Async-native, Pydantic-first, automatic OpenAPI docs |
| **LangChain** | AI Orchestration | Chains, retrievers, prompt templates — targeted use only |
| **Groq API** | Primary LLM | Free tier, Llama 3.3 70B, extremely fast inference |
| **Mistral API** | Fallback LLM | Free tier, Mistral Small, good structured output |
| **HuggingFace** | Embeddings | all-MiniLM-L6-v2, runs locally, no API key needed |
| **ChromaDB** | Vector Database | Local persistent storage, simple setup for MVP |
| **Pydantic Settings** | Config Management | Type-safe .env parsing, singleton pattern |
| **httpx** | HTTP Client | Async GitHub API calls for PR diff fetching |
| **subprocess** | Process Management | Safe git clone with timeout, replaces os.system |

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- pip
- git

### 1. Clone the repository

```bash
git clone https://github.com/Kaushik-FSD/RepoSense.git
cd RepoSense
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> First run will download `all-MiniLM-L6-v2` model weights (~90MB). Cached after that.

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=your_groq_api_key_here      # free at console.groq.com
LLM_PROVIDER=groq
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./storage/chroma
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

```bash
streamlit run ui/app.py
```

Ui starts at `http://localhost:8501`

---

## API Endpoints

> RepoSense is a backend project — all interaction is via REST API through Swagger UI or any HTTP client.

### Repository Assistant

```
POST /repo/ingest
```
Clones a GitHub repo, chunks all code files, stores embeddings in ChromaDB.

```json
{
  "github_url": "https://github.com/user/repo",
  "collection_name": "my-repo",
  "github_token": "ghp_xxx"   // optional, for private repos
}
```

```
POST /repo/ask
```
Ask any question about the ingested repository.

```json
{
  "question": "how does authentication work in this repo?",
  "collection_name": "my-repo"
}
```

### PR Summarizer

```
POST /pr/analyze
```
Fetches PR diff from GitHub and returns structured risk analysis.

```json
{
  "pr_url": "https://github.com/user/repo/pull/42",
  "collection_name": "my-repo"
}
```

### Log Analyzer

```
POST /logs/analyze
```
Analyzes application logs and returns error patterns with root causes.

```json
{
  "logs": "2024-01-15 ERROR Database connection timeout...\n..."
}
```

### Release Notes Generator

```
POST /release/generate
```
Generates structured release notes from commit messages.

```json
{
  "version": "v1.2.0",
  "commits": [
    "add JWT authentication middleware",
    "fix user session expiry bug"
  ]
}
```

### Admin

```
DELETE /admin/cleanup
```
Clears all ChromaDB collections, chroma storage, and uploaded files.

---

## Project Structure

```
RepoSense/
├── app/
│   ├── main.py                  # FastAPI app, router registration
│   ├── config.py                # Pydantic Settings + .env
│   ├── core/
│   │   ├── llm.py               # Groq/Mistral LangChain client
│   │   ├── embeddings.py        # HuggingFace embeddings setup
│   │   ├── vectorstore.py       # ChromaDB client + collection management
│   │   └── prompts.py           # All LLM prompt templates
│   ├── modules/
│   │   ├── repo/                # Repository Assistant
│   │   │   ├── schemas.py
│   │   │   ├── chunker.py       # File parsing + code-aware chunking
│   │   │   ├── service.py       # Ingest + RAG Q&A logic
│   │   │   └── router.py
│   │   ├── pr/                  # PR Summarizer
│   │   │   ├── schemas.py
│   │   │   ├── service.py       # GitHub API + retrieval + analysis
│   │   │   └── router.py
│   │   ├── logs/                # Log Analyzer
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── release/             # Release Notes Generator
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   └── admin/               # Admin utilities
│   │       └── router.py
│   └── utils/
│       └── text_utils.py        # LLM response cleaning helpers
├── storage/
│   ├── chroma/                  # ChromaDB persistent data
│   └── uploads/                 # Cloned repo temporary storage
├── .env.example
├── requirements.txt
└── README.md
```

---

## Production Roadmap

**Retrieval**
- [ ] Metadata filtering — query only specific file types or modules
- [ ] Hybrid search — combine semantic + keyword search for better accuracy
- [ ] Re-ranking — rerank retrieved chunks before passing to LLM

**Features**
- [ ] GitHub App integration — auto-analyze PRs on open via webhook
- [ ] Multi-repo support — ingest and query multiple repos simultaneously
- [ ] Private repo support via GitHub App (no token passing)

**Infrastructure**
- [ ] Cron job to clean orphaned ChromaDB segment folders
- [ ] Switch to Qdrant for production-grade vector storage
- [ ] Docker setup for one-command local run
- [ ] Deploy to Railway / Render

---

## Author

Built by [Kaushik](https://github.com/Kaushik-FSD) as a portfolio project demonstrating Applied AI engineering — RAG pipelines, vector retrieval, structured LLM outputs, and production backend patterns.
