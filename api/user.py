from fastapi import APIRouter, HTTPException
from models.users import User
from services.userServices import create_user, verify_password, add_blog_to_user
from pydantic import BaseModel
from datetime import datetime, UTC

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str

@router.post("/")
async def create_new_user(user_data: UserCreate):
    return await create_user(user_data.username, user_data.password)

class UserVerify(BaseModel):
    username: str
    password: str

@router.post("/verify")
async def verify_user(user_data: UserVerify):
    is_valid = await verify_password(user_data.username, user_data.password)
    if is_valid:
        return {"message": "User verified successfully"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

class BlogData(BaseModel):
    title: str
    content: str

@router.post("/{username}/add-blog")
async def add_blog(username: str, blog_data: BlogData):
    blog_info = {
        "title": blog_data.title,
        "content": blog_data.content,
        "created_at": datetime.now(UTC)  # Add any other fields you want
    }
    return await add_blog_to_user(username, blog_info)

