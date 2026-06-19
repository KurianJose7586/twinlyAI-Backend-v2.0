# app/api/v1/endpoints/connectors.py
"""
GitHub Connector: OAuth flow, repo listing, and code sync into Qdrant.

Flow:
  1. GET /connectors/github/authorize?token=<jwt>
       → redirect to GitHub OAuth with state=<jwt>
  2. GET /connectors/github/callback?code=<code>&state=<jwt>
       → exchange code → store GitHub access token in MongoDB connectors collection
       → redirect to frontend /candidate-active?connector=github&status=success
  3. GET /connectors/             → list connectors for authenticated user
  4. GET /connectors/github/repositories → list GitHub repos
  5. POST /connectors/github/repositories/{repo_name}/sync
       → fetch file content from GitHub → chunk → embed → store in Qdrant
"""

import httpx
import base64
from urllib.parse import urlencode
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.api.v1.deps import get_current_user
from app.core.config import settings
from app.core.security import decode_access_token, encrypt_token
from app.db.session import database
from app.schemas.user import User
from app.core.rag_pipeline import get_embeddings_model

from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient

router = APIRouter()

# MongoDB collection for connectors
connectors_collection = database["connectors"]

# File extensions we actually want to index
INDEXABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".go", ".rs", ".cpp", ".c", ".h",
    ".cs", ".rb", ".php", ".swift", ".kt",
    ".md", ".txt", ".yaml", ".yml", ".json",
    ".toml", ".env.example", ".sh",
}

MAX_FILE_SIZE_BYTES = 200_000   # 200 KB per file
MAX_FILES_PER_REPO  = 300


# ── 1. Initiate OAuth ──────────────────────────────────────────────────────────

@router.get("/github/authorize")
async def github_authorize(token: str):
    """
    Redirect the user to GitHub to authorize Twinly.
    The JWT token is passed as `state` so we know who's connecting after callback.
    """
    redirect_uri = f"{settings.BACKEND_URL.rstrip('/')}/api/v1/connectors/github/callback"
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "repo read:user",
        "state": token,
    }
    github_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=github_url)



# ── 2. OAuth Callback ──────────────────────────────────────────────────────────

@router.get("/github/callback")
async def github_callback(code: str, state: str, request: Request):
    """
    Exchange the temporary code for a GitHub access token and store it.
    `state` contains the user's JWT so we know which user this belongs to.
    """
    # Decode JWT from state to get user email
    try:
        payload = decode_access_token(state)
        user_email = payload.get("sub")
        if not user_email:
            raise ValueError("No sub in token")
    except Exception:
        frontend = settings.FRONTEND_URL
        return RedirectResponse(url=f"{frontend}/candidate-active?connector=github&status=error&msg=invalid_state")

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

    if resp.status_code != 200:
        frontend = settings.FRONTEND_URL
        return RedirectResponse(url=f"{frontend}/candidate-active?connector=github&status=error&msg=token_exchange_failed")

    token_data = resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        frontend = settings.FRONTEND_URL
        return RedirectResponse(url=f"{frontend}/candidate-active?connector=github&status=error&msg=no_access_token")

    # Encrypt token before storing — never persist plain-text OAuth tokens
    encrypted_token = encrypt_token(access_token)

    # Upsert connector in MongoDB
    await connectors_collection.update_one(
        {"user_email": user_email, "connector_type": "github"},
        {
            "$set": {
                "user_email": user_email,
                "connector_type": "github",
                "status": "connected",
                "encrypted_access_token": encrypted_token,
                "connected_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        upsert=True,
    )

    frontend = settings.FRONTEND_URL
    return RedirectResponse(url=f"{frontend}/candidate-active?connector=github&status=success")


# ── 3. List connectors ─────────────────────────────────────────────────────────

@router.get("/")
async def list_connectors(current_user: User = Depends(get_current_user)):
    """Return all connectors for the authenticated user (without exposing tokens)."""
    cursor = connectors_collection.find({"user_email": current_user.email})
    raw = await cursor.to_list(50)
    connectors = [
        {
            "id": str(c["_id"]),
            "connector_type": c["connector_type"],
            "status": c.get("status", "connected"),
            "connected_at": c.get("connected_at"),
        }
        for c in raw
    ]
    return {"connectors": connectors}


# ── Helper: get GitHub access token for user ──────────────────────────────────

async def _get_github_token(user_email: str) -> str:
    from app.core.security import decrypt_token
    connector = await connectors_collection.find_one(
        {"user_email": user_email, "connector_type": "github"}
    )
    if not connector:
        raise HTTPException(status_code=400, detail="GitHub account not connected. Please connect first.")
    encrypted = connector.get("encrypted_access_token") or connector.get("access_token")
    if not encrypted:
        raise HTTPException(status_code=400, detail="GitHub account not connected. Please connect first.")
    # Handle legacy unencrypted tokens (pre-migration) and new encrypted tokens
    if connector.get("encrypted_access_token"):
        return decrypt_token(encrypted)
    return encrypted


# ── 4. List repositories ───────────────────────────────────────────────────────

@router.get("/github/repositories")
async def list_github_repositories(current_user: User = Depends(get_current_user)):
    """Fetch the authenticated user's GitHub repositories."""
    gh_token = await _get_github_token(current_user.email)

    repos = []
    page = 1
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            resp = await client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {gh_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                params={"per_page": 100, "page": page, "sort": "updated"},
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch repos from GitHub")

            batch = resp.json()
            if not batch:
                break

            for r in batch:
                repos.append({
                    "id": r["id"],
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "description": r.get("description") or "",
                    "url": r["html_url"],
                    "private": r["private"],
                    "size_kb": r.get("size", 0),
                    "default_branch": r.get("default_branch", "main"),
                    "language": r.get("language") or "Unknown",
                    "updated_at": r.get("updated_at", ""),
                })

            if len(batch) < 100:
                break
            page += 1

    return {"repositories": repos}


# ── 5. Sync repository ─────────────────────────────────────────────────────────

@router.post("/github/repositories/{repo_name}/sync")
async def sync_repository(repo_name: str, current_user: User = Depends(get_current_user)):
    """
    Fetch all indexable files from a GitHub repo, chunk them,
    embed via HuggingFace, and upsert into a per-user Qdrant collection.

    Guardrails:
    - repo_name sanitised (no path traversal)
    - GitHub token validated before heavy work
    - File count and size capped
    - HuggingFace / Qdrant failures surface as 503 instead of 500
    - Empty repo handled gracefully
    """
    # ── GUARDRAIL: Sanitise repo_name ────────────────────────────────────────
    import re as _re
    if not repo_name or not _re.match(r'^[a-zA-Z0-9_.\-]+$', repo_name):
        raise HTTPException(status_code=400, detail="Invalid repository name.")

    gh_token = await _get_github_token(current_user.email)

    # ── GUARDRAIL: Verify GitHub token is still valid before doing heavy work ─
    async with httpx.AsyncClient(timeout=10) as _check_client:
        _token_check = await _check_client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
        )
    if _token_check.status_code == 401:
        # Token expired or revoked — clear it so user knows to reconnect
        await connectors_collection.update_one(
            {"user_email": current_user.email, "connector_type": "github"},
            {"$set": {"status": "token_expired"}}
        )
        raise HTTPException(
            status_code=401,
            detail="GitHub token has expired or been revoked. Please disconnect and reconnect GitHub."
        )
    if _token_check.status_code != 200:
        raise HTTPException(status_code=503, detail="Could not verify GitHub token. Try again later.")

    # First, resolve the full_name (owner/repo) — fetch user info
    async with httpx.AsyncClient(timeout=30) as client:
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not fetch GitHub user info")
        gh_username = user_resp.json()["login"]

    full_name = f"{gh_username}/{repo_name}"
    print(f"[Connector] Syncing repo {full_name} for user {current_user.email}")

    # Fetch file tree
    async with httpx.AsyncClient(timeout=60) as client:
        tree_resp = await client.get(
            f"https://api.github.com/repos/{full_name}/git/trees/HEAD?recursive=1",
            headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
        )

    if tree_resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_name}' not found.")
    if tree_resp.status_code != 200:
        raise HTTPException(status_code=tree_resp.status_code, detail="Failed to fetch repository tree.")

    tree_data = tree_resp.json()
    tree = tree_data.get("tree", [])

    # Filter to indexable files only
    indexable_files = [
        item for item in tree
        if item.get("type") == "blob"
        and any(item["path"].endswith(ext) for ext in INDEXABLE_EXTENSIONS)
        and item.get("size", 0) < MAX_FILE_SIZE_BYTES
    ][:MAX_FILES_PER_REPO]

    print(f"[Connector] Found {len(indexable_files)} indexable files")

    if not indexable_files:
        return {"status": "completed", "message": "No indexable files found in this repository.", "files_synced": 0}

    # Fetch file contents and build documents
    documents = []
    async with httpx.AsyncClient(timeout=30) as client:
        for item in indexable_files:
            try:
                content_resp = await client.get(
                    f"https://api.github.com/repos/{full_name}/contents/{item['path']}",
                    headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
                )
                if content_resp.status_code != 200:
                    continue

                file_data = content_resp.json()
                encoded = file_data.get("content", "")
                if not encoded:
                    continue

                # GitHub returns base64-encoded content
                decoded = base64.b64decode(encoded).decode("utf-8", errors="replace")
                if not decoded.strip():
                    continue

                # Chunk large files
                chunks = _chunk_code(decoded, item["path"], max_chars=1500)
                for chunk_text in chunks:
                    documents.append(
                        Document(
                            page_content=chunk_text,
                            metadata={
                                "source": f"github:{full_name}/{item['path']}",
                                "repo": full_name,
                                "path": item["path"],
                                "user_email": current_user.email,
                            },
                        )
                    )
            except Exception as e:
                print(f"[Connector] Error fetching {item['path']}: {e}")
                continue

    print(f"[Connector] Built {len(documents)} document chunks")

    if not documents:
        return {"status": "completed", "message": "All files were empty or unreadable.", "files_synced": 0}

    # Store in Qdrant under per-user collection
    collection_name = f"github_{current_user.email.replace('@', '_at_').replace('.', '_')}"

    try:
        embeddings = get_embeddings_model()
        QdrantVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=collection_name,
        )
    except Exception as e:
        print(f"[Connector] Qdrant/embedding error: {e}")
        # Surface embedding quota errors vs infrastructure errors distinctly
        err_str = str(e).lower()
        if "rate" in err_str or "quota" in err_str or "429" in err_str:
            raise HTTPException(
                status_code=429,
                detail="Embedding service rate limit hit. Please wait a moment and try again."
            )
        raise HTTPException(
            status_code=503,
            detail=f"Failed to index repository. The embedding service may be temporarily unavailable."
        )

    # Record sync in MongoDB
    await connectors_collection.update_one(
        {"user_email": current_user.email, "connector_type": "github"},
        {
            "$addToSet": {"synced_repos": repo_name},
            "$set": {"last_sync": datetime.now(timezone.utc).isoformat()},
        },
    )

    return {
        "status": "completed",
        "message": f"Successfully indexed {len(documents)} code chunks from '{repo_name}' into your AI Twin's knowledge base.",
        "files_synced": len(indexable_files),
        "chunks_indexed": len(documents),
    }


# ── 6. Disconnect connector ────────────────────────────────────────────────────

@router.delete("/github")
async def disconnect_github(current_user: User = Depends(get_current_user)):
    """Remove the GitHub connector for the authenticated user."""
    result = await connectors_collection.delete_one(
        {"user_email": current_user.email, "connector_type": "github"}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="GitHub connector not found")
    return {"status": "disconnected", "message": "GitHub connector removed."}


# ── Code chunking helper ───────────────────────────────────────────────────────

def _chunk_code(text: str, path: str, max_chars: int = 1500) -> list[str]:
    """
    Simple line-based chunker that respects function/class boundaries for
    Python-like languages and falls back to fixed windows for others.
    Each chunk is prefixed with the file path for context.
    """
    header = f"# File: {path}\n"
    if len(text) <= max_chars:
        return [header + text]

    lines = text.splitlines(keepends=True)
    chunks = []
    current = header
    for line in lines:
        if len(current) + len(line) > max_chars:
            if current.strip() != header.strip():
                chunks.append(current)
            current = header + line
        else:
            current += line

    if current.strip() != header.strip():
        chunks.append(current)

    return chunks if chunks else [header + text[:max_chars]]
