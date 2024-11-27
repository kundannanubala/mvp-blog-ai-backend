from fastapi import APIRouter, HTTPException
from typing import List
from services.blogServices import fetch_and_generate_blog_posts
from pydantic import BaseModel

router = APIRouter()

class BlogGenerationRequest(BaseModel):
    article_ids: List[str]

@router.post("/generate-blog")
async def generate_blog_from_articles(request: BlogGenerationRequest):
    """
    Generate a blog post with an image from specified articles
    
    Args:
        request: BlogGenerationRequest containing list of article IDs
        
    Returns:
        dict: Generated blog post content and image path
    """
    try:
        result = await fetch_and_generate_blog_posts(request.article_ids)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No content could be generated from the specified articles"
            )
            
        return {
            "status": "success",
            "blog_post": result.get("content", ""),
            "image_path": result.get("image_path", "")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating blog post: {str(e)}"
        )
