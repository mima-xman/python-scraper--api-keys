"""
MongoDB Database Manager for Bytez API Key Scraper
Handles all database operations for storing and retrieving API keys
"""

from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import settings


class MongoDBManager:
    """
    Manages MongoDB connections and operations for API key storage.
    """

    def __init__(self):
        """Initialize MongoDB connection."""
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """
        Establish connection to MongoDB.
        
        Raises:
            ConnectionFailure: If unable to connect to MongoDB
        """
        try:
            self.client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[settings.MONGODB_DATABASE]
            self.collection = self.db[settings.MONGODB_COLLECTION]
            
            print(f"✓ Connected to MongoDB: {settings.MONGODB_DATABASE}.{settings.MONGODB_COLLECTION}")
            
        except ConnectionFailure as e:
            raise ConnectionFailure(
                f"Failed to connect to MongoDB at {settings.MONGODB_URL}: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Unexpected error connecting to MongoDB: {str(e)}")

    def save_api_key(self, account: Dict[str, str]) -> bool:
        """
        Save API key to MongoDB with the required schema.
        
        Args:
            account: Dictionary containing email, password, api_key, and scraped_at
            
        Returns:
            bool: True if save was successful
            
        Raises:
            Exception: If save operation fails
        """
        try:
            # Get current timestamp
            current_time = datetime.now()
            
            # Prepare document with all required fields
            document = {
                "email": account.get("email"),
                "password": account.get("password"),
                "api_key": account.get("api_key"),
                "scraped_at": account.get("scraped_at"),
                "scraped_by": None,
                "in_use": False,
                "locked_at": None,
                "used_by": None,
                "models_status": {},
                "created_at": current_time,
                "updated_at": current_time
            }
            
            # Insert document
            result = self.collection.insert_one(document)
            
            if result.inserted_id:
                print(f"✓ API key saved to MongoDB with ID: {result.inserted_id}")
                return True
            else:
                raise Exception("Failed to insert document - no ID returned")
                
        except OperationFailure as e:
            raise Exception(f"MongoDB operation failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to save API key to MongoDB: {str(e)}")

    def get_all_api_keys(self) -> List[Dict]:
        """
        Retrieve all API keys from MongoDB.
        
        Returns:
            List of API key documents
            
        Raises:
            Exception: If retrieval fails
        """
        try:
            # Fetch all documents
            documents = list(self.collection.find())
            return documents
            
        except Exception as e:
            raise Exception(f"Failed to retrieve API keys from MongoDB: {str(e)}")

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
