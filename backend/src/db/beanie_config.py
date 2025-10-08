"""
Beanie ODM Configuration and Database Setup
"""

import os
from typing import Optional
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration for Beanie ODM"""
    
    def __init__(self):
        self.mongodb_url: str = os.getenv("project_db_url")
        self.database_name: str = os.getenv("project_db_name")
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
    
    async def connect_to_mongo(self):
        """Create database connection"""
        try:
            self.client = AsyncIOMotorClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=5000
            )
            self.database = self.client[self.database_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.database_name}")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise e
    
    async def close_mongo_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")

# Global database config instance
db_config = DatabaseConfig()

async def init_database():
    """Initialize Beanie with all document models"""
    try:
        # First ensure database connection is established
        if db_config.database is None:
            await db_config.connect_to_mongo()
        
        # Import document models after they're converted to Beanie
        from src.model.song import Song
        from src.model.user import User
        
        # Initialize Beanie with error handling for index conflicts
        try:
            await init_beanie(
                database=db_config.database,
                document_models=[Song, User]
            )
            print("✅ Beanie ODM initialized successfully")
        except Exception as index_error:
            # Handle index conflicts gracefully
            if "IndexKeySpecsConflict" in str(index_error) or "existing index" in str(index_error).lower():
                print("⚠️  Index conflict detected, but continuing with existing indexes...")
                print("✅ Beanie ODM initialized with existing indexes")
            else:
                raise index_error
        
    except Exception as e:
        print(f"❌ Failed to initialize Beanie: {e}")
        raise e

async def get_database():
    """Get the database instance"""
    if db_config.database is None:
        await db_config.connect_to_mongo()
    return db_config.database
