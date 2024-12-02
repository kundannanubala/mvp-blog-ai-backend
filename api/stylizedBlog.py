from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from services.stylizedBlogServices import BlogStyle, generate_stylized_blog, generate_multi_style_blogs
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

router = APIRouter()

class StylizedBlogRequest(BaseModel):
    """
    Data model for stylized blog generation request.
    """
    article_ids: List[str]
    style: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "article_ids": ["af074638c3b443e3bd629b20c2ccd552"],  # Example using the 'ID' field
                "style": "conversational"
            }
        }

@router.post("/generate-stylized")
async def generate_stylized_blog_post(request: StylizedBlogRequest):
    """
    Generate a blog post in a specific style from provided articles.
    """
    try:
        # First, validate that article IDs exist in database
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        collection = db["articles"]
        
        # Check if articles exist using the 'ID' field
        existing_articles = await collection.count_documents({"ID": {"$in": request.article_ids}})
        if existing_articles != len(request.article_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more article IDs do not exist in the database"
            )
            
        # Validate style
        try:
            style_key = request.style.upper().strip()
            available_styles = [style.value for style in BlogStyle]
            
            if style_key not in [s.upper() for s in available_styles]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid style. Available styles: {available_styles}"
                )
                
            style = BlogStyle[style_key]
            
        except (KeyError, AttributeError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style format. Available styles: {[s.value for s in BlogStyle]}"
            )
            
        # Generate the blog post
        result = await generate_stylized_blog(request.article_ids, style)
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "blog_post": result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error generating stylized blog: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the blog post: {str(e)}"
        )
    finally:
        if 'client' in locals():
            client.close()