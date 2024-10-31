from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.users import User
from uuid import uuid4
from datetime import datetime, UTC
import bcrypt

async def create_user(username: str, password: str) -> dict:
    """
    Create a new user with hashed password
    
    Args:
        username (str): Username for new user
        password (str): Password to be hashed
        
    Returns:
        dict: Created user information
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['users']
    
    try:
        # Check if username already exists
        existing_user = await collection.find_one({"username": username})
        if existing_user:
            return {"error": "Username already exists"}
        
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Create new user
        user = User(
            username=username,
            password=hashed_password.decode('utf-8'),
            myblogs=[],
            created_at=datetime.now(UTC)
        )
        
        result = await collection.insert_one(user.dict())
        return {"message": "User created successfully", "id": str(result.inserted_id)}
        
    finally:
        client.close()

async def get_user(username: str) -> dict:
    """
    Retrieve user by username
    
    Args:
        username (str): Username to search for
        
    Returns:
        dict: User information if found
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['users']
    
    try:
        user = await collection.find_one({"username": username})
        if user:
            user['id'] = str(user['_id'])
            del user['_id']
            return user
        return None
    finally:
        client.close()

async def verify_password(username: str, password: str) -> bool:
    """
    Verify user password
    
    Args:
        username (str): Username to verify
        password (str): Password to check
        
    Returns:
        bool: True if password matches
    """
    user = await get_user(username)
    if not user:
        return False
    
    return bcrypt.checkpw(
        password.encode('utf-8'),
        user['password'].encode('utf-8')
    )

async def add_blog_to_user(username: str, blog_data: dict) -> dict:
    """
    Add a blog to user's myblogs array
    
    Args:
        username (str): Username to add blog to
        blog_data (dict): Blog data to add
        
    Returns:
        dict: Updated user information
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['users']
    
    try:
        result = await collection.update_one(
            {"username": username},
            {"$push": {"myblogs": blog_data}}
        )
        
        if result.modified_count:
            return {"message": "Blog added successfully"}
        return {"error": "User not found"}
    finally:
        client.close()
