# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.endpoints import auth, bots, api_keys, users, oauth, recruiter, webhooks, connectors
from app.core.rate_limit import setup_rate_limiting
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
import logging
from contextlib import asynccontextmanager
from app.db.session import (
    users_collection,
    bots_collection,
    api_keys_collection,
    connectors_collection,
    conversations_collection,
    activity_events_collection,
    resume_versions_collection,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create indexes on startup for performance-critical queries
    index_defs = [
        # users
        (users_collection, [("email", 1)], True),
        # bots — looked up by user_id on every bot operation
        (bots_collection, [("user_id", 1)], False),
        # api_keys — hashed_key is checked on every API-key-authenticated request
        (api_keys_collection, [("hashed_key", 1)], True),
        (api_keys_collection, [("user_id", 1)], False),
        # connectors — looked up by user_email + connector_type
        (connectors_collection, [("user_email", 1), ("connector_type", 1)], True),
        # conversations — queried by bot_id with sort on started_at
        (conversations_collection, [("bot_id", 1), ("started_at", -1)], False),
        # activity_events — queried by user_id with sort on created_at
        (activity_events_collection, [("user_id", 1), ("created_at", -1)], False),
        # resume_versions — queried by bot_id + user_id
        (resume_versions_collection, [("bot_id", 1), ("user_id", 1)], False),
    ]
    for collection, keys, unique in index_defs:
        try:
            await collection.create_index(keys, unique=unique, background=True)
        except Exception as e:
            logging.warning("Failed to create index on %s: %s", collection.name, type(e).__name__)
    logging.info("Database indexes ensured.")
    yield

app = FastAPI(
    title="TwinlyAI API",
    description="API for the TwinlyAI SaaS application.",
    version="0.1.0",
    lifespan=lifespan
)

# --- Production Error Masking ---
if settings.ENV != "dev":
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logging.error("Unhandled error: %s", type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please contact support."}
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error("Validation error details: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

setup_rate_limiting(app)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY
)

# --- CORS Middleware ---
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://twinlyai.app",
    "https://www.twinlyai.app",
]

if settings.FRONTEND_URL:
    # Strip trailing slash to ensure exact Origin header match
    clean_url = settings.FRONTEND_URL.rstrip("/")
    if clean_url and clean_url not in origins:
        origins.append(clean_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Tighten to allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# --- Include Routers ---
# Note: oauth prefix changed to /oauth to avoid collision with auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"]) 
app.include_router(bots.router, prefix="/api/v1/bots", tags=["bots"])
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["api_keys"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(recruiter.router, prefix="/api/v1/recruiter", tags=["recruiter"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["connectors"])

@app.get("/api/health")
async def health_check():
    """Public health check — returns only status, no internal details."""
    health_status = {"status": "ok", "checks": {}}

    # 1. Check MongoDB
    try:
        from app.db.session import client
        await client.admin.command("ping")
        health_status["checks"]["mongodb"] = "connected"
    except Exception:
        health_status["status"] = "error"
        health_status["checks"]["mongodb"] = "unavailable"

    # 2. Check MongoDB Vector Store
    try:
        from app.core.config import settings
        from app.core.rag_pipeline import get_sync_mongo_client
        mongo_client = get_sync_mongo_client()
        db = mongo_client[settings.MONGO_DB_NAME]
        bot_v_count = db["vector_store_bots"].count_documents({})
        global_v_count = db["vector_store_global"].count_documents({})
        health_status["checks"]["vector_store"] = "connected"
    except Exception:
        health_status["status"] = "error"
        health_status["checks"]["vector_store"] = "unavailable"

    return health_status


@app.get("/api/health/detailed")
async def health_check_detailed():
    """Detailed health check — requires admin API key via X-Admin-Key header."""
    from fastapi import Header, HTTPException, status

    admin_key = Header(None, alias="X-Admin-Key")
    if not admin_key or admin_key != settings.HEALTH_CHECK_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing admin key",
        )

    health_status = {"status": "ok", "checks": {}, "env_debug": {}}

    # 1. Check MongoDB
    try:
        from app.db.session import client
        await client.admin.command("ping")
        health_status["checks"]["mongodb"] = "connected"
    except Exception as e:
        health_status["status"] = "error"
        health_status["checks"]["mongodb"] = f"failed: {str(e)}"

    # 2. Check MongoDB Vector Store (Diagnostic)
    try:
        from app.core.config import settings
        from app.core.rag_pipeline import get_sync_mongo_client
        mongo_client = get_sync_mongo_client()
        db = mongo_client[settings.MONGO_DB_NAME]
        bot_v_count = db["vector_store_bots"].count_documents({})
        global_v_count = db["vector_store_global"].count_documents({})
        health_status["checks"]["vector_store"] = f"connected (bots: {bot_v_count}, global: {global_v_count})"
        try:
            indexes = list(db["vector_store_bots"].list_search_indexes())
            health_status["checks"]["vector_search_indexes"] = f"found {len(indexes)}"
        except Exception:
            health_status["checks"]["vector_search_indexes"] = "unable to list"
    except Exception as e:
        health_status["status"] = "error"
        health_status["checks"]["vector_store"] = f"failed: {str(e)}"

    # 3. Environment debug (only for authenticated internal use)
    health_status["env_debug"] = {
        "MONGO_URI": f"{settings.MONGO_CONNECTION_STRING[:15]}...",
        "QDRANT_URL": settings.QDRANT_URL,
        "ENV": settings.ENV,
        "FRONTEND_URL": settings.FRONTEND_URL,
    }

    return health_status

@app.get("/")
async def root():
    return {"message": "Welcome to TwinlyAI API"}