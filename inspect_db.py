import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys

async def main():
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        mongo_uri = os.getenv('MONGO_CONNECTION_STRING', 'mongodb+srv://twinlyai_user:LEKF3HHaONUe0wLi@twinlyai-cluster.rpjpqve.mongodb.net/')
        client = AsyncIOMotorClient(mongo_uri)
        db = client.twinlyai
        users = await db.users.find().to_list(10)
        for user in users:
            print(f"Email: {user.get('email', 'N/A')}")
            print(f"Role: {user.get('role', 'N/A')}")
            print(f"Has password: {'Yes' if user.get('hashed_password') else 'No'}")
            print("---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
