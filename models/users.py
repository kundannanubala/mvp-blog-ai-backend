from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, UTC
from models.personas import UserPersona

class User(BaseModel):
    """
    Data model for representing a user.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
        myblogs (List[dict]): A list of blogs associated with the user, defaulting to an empty list.
        created_at (datetime): The timestamp when the user was created, defaulting to the current UTC time.
        persona (Optional[UserPersona]): The persona of the user, defaulting to None.
    """
    username: str  # The username of the user
    password: str  # The password of the user
    myblogs: List[dict] = []  # A list to store the user's blogs
    created_at: datetime = datetime.now(UTC)  # The creation timestamp of the user, set to the current UTC time by default
    persona: Optional[UserPersona] = None
