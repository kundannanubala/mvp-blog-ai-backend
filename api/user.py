from fastapi import APIRouter, HTTPException
from models.users import User
from services.userServices import create_user, verify_password, add_blog_to_user
from services.personaServices import create_user_persona, get_user_persona
from pydantic import BaseModel
from datetime import datetime, UTC
from typing import List, Optional

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
    It utilizes the `create_user` service to handle the actual creation logic.

    Args:
        user_data (UserCreate): The user data containing the username and password.

    Returns:
        dict: A dictionary containing the result of the user creation process, typically including a success message
              or an error message if the creation fails.
    """
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

    This function checks if the provided username and password match an existing user in the system.
    It calls the `verify_password` service to perform the verification.

    Args:
        user_data (UserVerify): The user data containing the username and password.

    Returns:
        dict: A dictionary containing a success message if the user is verified.

    Raises:
        HTTPException: If the username or password is invalid, a 401 status code is returned with an error message.
    """
    is_valid = await verify_password(user_data.username, user_data.password)
    if is_valid:
        return {"message": "User verified successfully"}
    else:
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
    It uses the `add_blog_to_user` service to handle the addition of the blog post.

    Args:
        username (str): The username of the user to add the blog post to.
        blog_data (BlogData): The blog data containing the title and content.

    Returns:
        dict: A dictionary containing the result of the blog addition process, including a success message or error details.
    """
    blog_info = {
        "title": blog_data.title,
        "content": blog_data.content,
        "created_at": datetime.now(UTC),
    }
    return await add_blog_to_user(username, blog_info)

class PersonaCreate(BaseModel):
    """
    Data model for creating a user persona.

    Attributes:
        writing_style (str): The preferred writing style of the user.
        tone (str): The tone the user prefers in their content.
        expertise_level (str): The level of expertise the user wants to convey.
        target_audience (str): The intended audience for the user's content.
        preferred_content_types (List[str]): Types of content the user prefers.
        industry_focus (List[str]): Industries the user is focused on.
        content_length_preference (str): Preferred length of the content.
        key_interests (List[str]): Key interests of the user.
        language_style (str): The language style the user prefers.
        formatting_preferences (Optional[dict]): Any specific formatting preferences the user has.
    """
    writing_style: str
    tone: str
    expertise_level: str
    target_audience: str
    preferred_content_types: List[str]
    industry_focus: List[str]
    content_length_preference: str
    key_interests: List[str]
    language_style: str
    formatting_preferences: Optional[dict] = {}

@router.post("/{username}/create-persona")
async def create_persona(username: str, persona_data: PersonaCreate):
    """
    Endpoint to create a persona for a user.

    This function takes a username and persona data, then creates a persona for the specified user.
    It calls the `create_user_persona` service to handle the persona creation.

    Args:
        username (str): The username of the user for whom the persona is being created.
        persona_data (PersonaCreate): The persona data containing various attributes of the user's persona.

    Returns:
        dict: A dictionary containing the result of the persona creation process.
    """
    return await create_user_persona(username, persona_data.dict())

@router.get("/{username}/persona")
async def get_persona(username: str):
    """
    Endpoint to retrieve a user's persona.

    This function fetches the persona associated with the specified username.
    It uses the `get_user_persona` service to retrieve the persona data.

    Args:
        username (str): The username of the user whose persona is being retrieved.

    Returns:
        dict: A dictionary containing the user's persona data if found.

    Raises:
        HTTPException: If the persona is not found, a 404 status code is returned with an error message.
    """
    persona = await get_user_persona(username)
    if persona:
        return persona
    raise HTTPException(status_code=404, detail="Persona not found")
