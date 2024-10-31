from pydantic import BaseModel
from typing import List
from datetime import datetime, UTC

class User(BaseModel):
    username: str
    password: str
    myblogs: List[dict] = []
    created_at: datetime = datetime.now(UTC)
