from models.personas import UserPersona
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from typing import Optional

async def create_user_persona(username: str, persona_data: dict) -> dict:
    """
    Create a persona for a user and update the user's document in the database.

    This function takes a username and persona data, creates a UserPersona instance,
    and updates the corresponding user document in the MongoDB collection with the persona information.

    Args:
        username (str): The username of the user for whom the persona is being created.
        persona_data (dict): A dictionary containing the persona attributes.

    Returns:
        dict: A dictionary containing a success message if the persona is created successfully,
              or an error message if the user is not found.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["users"]
    
    try:
        # Create UserPersona instance from the provided data
        persona = UserPersona(**persona_data)
        
        # Update the user document with the new persona information
        result = await collection.update_one(
            {"username": username},
            {"$set": {"persona": persona.dict()}}
        )
        
        if result.modified_count:
            return {"message": "Persona created successfully"}
        return {"error": "User not found"}
    finally:
        client.close()

async def get_user_persona(username: str) -> Optional[UserPersona]:
    """
    Retrieve the persona associated with a given username from the database.

    This function queries the MongoDB collection to find the user document by username
    and returns the UserPersona instance if found.

    Args:
        username (str): The username of the user whose persona is being retrieved.

    Returns:
        Optional[UserPersona]: A UserPersona instance if the persona is found, otherwise None.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["users"]
    
    try:
        # Find the user document by username
        user = await collection.find_one({"username": username})
        if user and "persona" in user:
            return UserPersona(**user["persona"])
        return None
    finally:
        client.close()