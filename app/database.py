from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            # Get MongoDB URL from environment variable
            mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client["payment_app"]
            
            # Test the connection
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed.")
    
    def get_db(self):
        """Get database instance."""
        return self.db
    
    def get_collection(self, collection_name: str):
        """Get a specific collection from the database."""
        if self.db:
            return self.db[collection_name]
        return None

# Create a global database instance
database = Database()

# Convenience functions
async def connect_to_mongo():
    """Connect to MongoDB."""
    return await database.connect()

async def close_mongo_connection():
    """Close MongoDB connection."""
    await database.close()

def get_database():
    """Get database instance."""
    return database.get_db()

def get_collection(collection_name: str):
    """Get a specific collection."""
    return database.get_collection(collection_name) 