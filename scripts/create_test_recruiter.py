import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    # Use the same credentials as in .env
    client = AsyncIOMotorClient("mongodb://admin:password@localhost:27017/twinlyai_db?authSource=admin")
    db = client["twinlyai_db"]
    users_collection = db["users"]
    
    email = "test-recruiter@twinly.ai"
    password = "Password123!"
    hashed_password = pwd_context.hash(password)
    
    # Remove existing
    await users_collection.delete_one({"email": email})
    
    user_doc = {
        "email": email,
        "hashed_password": hashed_password,
        "role": "recruiter",
        "subscription_tier": "pro",
        "onboarding_complete": False
    }
    
    await users_collection.insert_one(user_doc)
    print(f"Created test recruiter: {email} / {password}")

if __name__ == "__main__":
    asyncio.run(create_test_user())
