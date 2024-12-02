from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.users import User
from uuid import uuid4
from datetime import datetime, UTC
import bcrypt


async def create_user(username: str, password: str) -> dict:
    """
    Create a new user with a hashed password and store it in the database.

    This function checks if the username already exists in the database. If not, it hashes the provided password
    using bcrypt, creates a new user object, and inserts it into the 'users' collection in MongoDB.

    Args:
        username (str): The desired username for the new user.
        password (str): The password to be hashed and stored.

    Returns:
        dict: A dictionary containing a success message and the user ID if creation is successful,
              or an error message if the username already exists.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["users"]

    try:
        # Check if the username already exists in the database
        existing_user = await collection.find_one({"username": username})
        if existing_user:
            return {"error": "Username already exists"}

        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Create a new user object with the hashed password and current timestamp
        user = User(
            username=username,
            password=hashed_password.decode("utf-8"),
            myblogs=[],
            created_at=datetime.now(UTC),
        )

        # Insert the new user into the database and return a success message with the user ID
        result = await collection.insert_one(user.dict())
        return {
            "message": "User created successfully",
            "id": str(result.inserted_id)
        }

    finally:
        # Ensure the database client is closed after the operation
        client.close()


async def get_user(username: str) -> dict:
    """
    Retrieve a user's information from the database by their username.

    This function searches the 'users' collection in MongoDB for a document matching the provided username.
    If found, it returns the user's information with the MongoDB ObjectId converted to a string.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        dict: A dictionary containing the user's information if found, or None if the user does not exist.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["users"]

    try:
        # Search for the user in the database by username
        user = await collection.find_one({"username": username})
        if user:
            # Convert the MongoDB ObjectId to a string and remove the original _id field
            user["id"] = str(user["_id"])
            del user["_id"]
            return user
        return None
    finally:
        # Ensure the database client is closed after the operation
        client.close()


async def verify_password(username: str, password: str) -> bool:
    """
    Verify if the provided password matches the stored password for a given username.

    This function retrieves the user's stored password from the database and compares it with the provided password
    using bcrypt's checkpw function.

    Args:
        username (str): The username of the user whose password is to be verified.
        password (str): The password to verify against the stored password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    # Retrieve the user information from the database
    user = await get_user(username)
    if not user:
        return False

    # Compare the provided password with the stored hashed password
    return bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    )


async def add_blog_to_user(username: str, blog_data: dict) -> dict:
    """
    Add a blog entry to a user's 'myblogs' array in the database.

    This function updates the 'myblogs' array of the specified user by appending the provided blog data.
    It returns a success message if the update is successful, or an error message if the user is not found.

    Args:
        username (str): The username of the user to whom the blog will be added.
        blog_data (dict): The blog data to be added to the user's 'myblogs' array.

    Returns:
        dict: A dictionary containing a success message if the blog is added, or an error message if the user is not found.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["users"]

    try:
        # Update the user's 'myblogs' array by appending the new blog data
        result = await collection.update_one(
            {"username": username}, {"$push": {"myblogs": blog_data}}
        )

        # Check if the update was successful and return the appropriate message
        if result.modified_count:
            return {"message": "Blog added successfully"}
        return {"error": "User not found"}
    finally:
        # Ensure the database client is closed after the operation
        client.close()
