"""
MongoDB Database Manager for Bytez API Key Scraper
Handles all database operations for storing and retrieving API keys
"""

from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import settings


class MongoDBManager:
    """
    Manages MongoDB connections and operations for API key storage.
    """

    def __init__(self, scraper_id: Optional[str] = None):
        """Initialize MongoDB connection.
        
        Args:
            scraper_id: Optional scraper ID to use. If not provided, will be initialized later.
        """
        self.client = None
        self.db = None
        self.collection = None
        self.scrapers_collection = None
        self.scraper_id = scraper_id
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
            self.scrapers_collection = self.db["scrapers"]
            
            print(f"✓ Connected to MongoDB: {settings.MONGODB_DATABASE}")
            print(f"  - Collections: scrapers, {settings.MONGODB_COLLECTION}")
            
        except ConnectionFailure as e:
            raise ConnectionFailure(
                f"Failed to connect to MongoDB at {settings.MONGODB_URL}: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Unexpected error connecting to MongoDB: {str(e)}")

    def get_or_create_scraper(self, scraper_name: str = None, scraper_id: str = None) -> ObjectId:
        """
        Get existing scraper or create a new one.
        
        Args:
            scraper_name: Name for the scraper (defaults to settings.SCRAPER_NAME)
            scraper_id: Optional scraper ID to reuse existing scraper
            
        Returns:
            ObjectId: The scraper's _id
            
        Raises:
            Exception: If scraper operations fail
        """
        try:
            scraper_name = scraper_name or settings.SCRAPER_NAME
            scraper_id = scraper_id or settings.SCRAPER_ID
            
            # If scraper_id is provided, try to find it
            if scraper_id:
                try:
                    scraper = self.scrapers_collection.find_one({"_id": ObjectId(scraper_id)})
                    if scraper:
                        print(f"✓ Using existing scraper: {scraper['name']} (ID: {scraper_id})")
                        return ObjectId(scraper_id)
                    else:
                        print(f"⚠ Scraper ID {scraper_id} not found, creating new scraper...")
                except Exception as e:
                    print(f"⚠ Invalid scraper ID format: {scraper_id}, creating new scraper...")
            
            # Create new scraper
            current_time = datetime.now()
            scraper_doc = {
                "name": scraper_name,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            result = self.scrapers_collection.insert_one(scraper_doc)
            print(f"✓ Created new scraper: {scraper_name} (ID: {result.inserted_id})")
            return result.inserted_id
            
        except Exception as e:
            raise Exception(f"Failed to get or create scraper: {str(e)}")

    def save_api_key(self, account: Dict[str, str], scraper_id: ObjectId) -> bool:
        """
        Save API key to MongoDB with the required schema.
        
        Args:
            account: Dictionary containing email, password, and api_key
            scraper_id: ObjectId of the scraper that generated this key
            
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
                "scraper_id": scraper_id,
                "email": account.get("email"),
                "password": account.get("password"),
                "api_key": account.get("api_key"),
                "in_use": False,
                "locked_at": None,
                "used_by": None,
                "models_expirations": {},
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
