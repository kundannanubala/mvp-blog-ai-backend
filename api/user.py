from fastapi import APIRouter, HTTPException
from models.users import User
from services.userServices import create_user, verify_password, add_blog_to_user
from pydantic import BaseModel
from datetime import datetime, UTC

# Initialize the FastAPI router for handling user-related endpoints
router = APIRouter()

class UserCreate(BaseModel):
    """
    Data model for creating a new user.

    Attributes:
        username (str): The desired username for the new user.
        password (str): The password for the new user.
    """
    username: str
    password: str

@router.post("/")
async def create_new_user(user_data: UserCreate):
    """
    Endpoint to create a new user.

    This function takes user data, including a username and password, and creates a new user in the system.

    Args:
        user_data (UserCreate): The user data containing the username and password.

    Returns:
        dict: A dictionary containing the result of the user creation process.
    """
    # Call the service to create a new user with the provided username and password
    return await create_user(user_data.username, user_data.password)

class UserVerify(BaseModel):
    """
    Data model for verifying a user's credentials.

    Attributes:
        username (str): The username of the user to verify.
        password (str): The password of the user to verify.
    """
    username: str
    password: str

@router.post("/verify")
async def verify_user(user_data: UserVerify):
    """
    Endpoint to verify a user's credentials.

    This function checks if the provided username and password match an existing user.

    Args:
        user_data (UserVerify): The user data containing the username and password.

    Returns:
        dict: A dictionary containing a success message if the user is verified.

    Raises:
        HTTPException: If the username or password is invalid, a 401 status code is returned.
    """
    # Verify the user's credentials using the provided username and password
    is_valid = await verify_password(user_data.username, user_data.password)
    if is_valid:
        return {"message": "User verified successfully"}
    else:
        # Raise an HTTPException if the credentials are invalid
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password")

class BlogData(BaseModel):
    """
    Data model for blog data to be added to a user.

    Attributes:
        title (str): The title of the blog post.
        content (str): The content of the blog post.
    """
    title: str
    content: str

@router.post("/{username}/add-blog")
async def add_blog(username: str, blog_data: BlogData):
    """
    Endpoint to add a blog post to a user's account.

    This function takes a username and blog data, then adds the blog post to the specified user's account.

    Args:
        username (str): The username of the user to add the blog post to.
        blog_data (BlogData): The blog data containing the title and content.

    Returns:
        dict: A dictionary containing the result of the blog addition process.
    """
    # Prepare the blog information with the current timestamp
    blog_info = {
        "title": blog_data.title,
        "content": blog_data.content,
        "created_at": datetime.now(UTC),  # Record the creation time of the blog post
    }
    # Call the service to add the blog to the user's account
    return await add_blog_to_user(username, blog_info)
