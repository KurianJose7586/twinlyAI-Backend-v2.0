# app/db/session.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import certifi # <-- Import certifi

# --- THIS IS THE FIX ---
# Only use tlsCAFile for production (Atlas/Cloud) connections, not local Docker
client_kwargs = {}
if "mongodb+srv://" in settings.MONGO_CONNECTION_STRING:
    client_kwargs["tlsCAFile"] = certifi.where()

client = AsyncIOMotorClient(
    settings.MONGO_CONNECTION_STRING,
    **client_kwargs
)
# --- END OF FIX ---

database = client[settings.MONGO_DB_NAME]

# Define collections
users_collection = database["users"]
bots_collection = database["bots"]
api_keys_collection = database["api_keys"]
connectors_collection = database["connectors"]
connector_sources_collection = database["connector_sources"]
connector_documents_collection = database["connector_documents"]
conversations_collection = database["conversations"]
resume_versions_collection = database["resume_versions"]
activity_events_collection = database["activity_events"]