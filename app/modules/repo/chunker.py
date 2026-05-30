import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import get_settings

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".cs", ".rb", ".php", ".html", ".css", ".tsx", ".jsx",
    ".md", ".txt", ".yaml", ".yml", ".json", ".env.example", ".sh"
}

EXCLUDED_FILES = {
    # JS/TS
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    # Python
    "poetry.lock", "Pipfile.lock",
    # Java
    "gradle.lockfile",
    # Ruby
    "Gemfile.lock",
    # Rust
    "Cargo.lock",
}

def get_language(ext: str) -> str:
    mapping = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".java": "java", ".go": "go", ".rs": "rust", ".cpp": "cpp", ".c": "c", ".h": "c", ".cs": "csharp",
        ".rb": "ruby", ".php": "php", ".html": "html", ".css": "css", ".tsx": "typescriptreact", ".jsx": "javascriptreact",
        ".md": "markdown", ".txt": "text", ".yaml": "yaml", ".yml": "yaml",
        ".json": "json", ".sh": "shell"
    }
    return mapping.get(ext, "unknown")

# This method is seperate from load_documents_from_repo because we want to treat repo-level metadata files differently.
# We wont mix it with code files when chunking, and can also use the metadata tag to give it more weight during retrieval.
def load_repo_metadata(repo_path: str) -> list[Document]:
    metadata_files = ["README.md", "package.json", "pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "Pipfile.lock", "Gemfile", "Gemfile.lock", "go.mod", "Cargo.toml", "Cargo.lock", ".env", ".env.example", "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "Makefile", "build.gradle", "pom.xml"]
    docs = []

    for filename in metadata_files:
        filepath = os.path.join(repo_path, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if content.strip():
            docs.append(Document(
                page_content=content,
                metadata={
                    "filename": filename,
                    "filepath": filepath,
                    "language": "markdown",
                    "type": "repo_metadata"      # tag it differently
                }
            ))
    return docs

def load_documents_from_repo(repo_path: str) -> list[Document]:
    documents = []
    for root, _, files in os.walk(repo_path):
        # get all parts of current path
        parts = Path(root).parts  
        # e.g. ('storage', 'uploads', 'repo', 'node_modules', 'some-lib')
        
        # check if any part is a folder we want to skip
        should_skip = False
        for part in parts:
            if part.startswith(".") or part in {"node_modules", "__pycache__", "venv"}:
                should_skip = True
                break
        
        if should_skip:
            continue

        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue
            if file in EXCLUDED_FILES: # skip common non-code files that add noise
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if not content.strip():
                    continue

                documents.append(Document(
                    page_content=content,
                    metadata={
                        "filename": file,
                        "filepath": filepath,
                        "language": get_language(ext),
                    }
                ))
            except Exception:
                continue

    return documents

def chunk_documents(documents: list[Document]) -> list[Document]:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)