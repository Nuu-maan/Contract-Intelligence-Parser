"""Database connection and configuration for MongoDB."""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager."""
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_mongo():
    """Create database connection."""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes for better performance
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create database indexes for optimal performance."""
    try:
        # Index for contracts collection
        contracts_collection = db.database.contracts
        await contracts_collection.create_index("upload_date")
        await contracts_collection.create_index("status")
        await contracts_collection.create_index("content_hash")
        
        # Index for contract_data collection
        contract_data_collection = db.database.contract_data
        await contracts_collection.create_index("contract_id")
        await contract_data_collection.create_index("processing_date")
        await contract_data_collection.create_index("confidence_score")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db.database
