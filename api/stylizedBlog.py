from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from services.stylizedBlogServices import BlogStyle, generate_stylized_blog
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

router = APIRouter()

class StylizedBlogRequest(BaseModel):
    """
    Data model for stylized blog generation request.

    Attributes:
        article_ids (List[str]): A list of article IDs to be used as context for generating the blog.
        style (str): The desired writing style for the blog post.
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
    Endpoint to generate a blog post in a specific style from provided articles.

    Args:
        request (StylizedBlogRequest): The request body containing article IDs and the desired style.

    Returns:
        dict: A dictionary containing the status, timestamp, and generated blog post content.

    Raises:
        HTTPException: If any validation fails or an error occurs during blog generation.
    """
    try:
        # Initialize MongoDB client and access the articles collection
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        collection = db["articles"]
        
        # Validate that all provided article IDs exist in the database
        existing_articles = await collection.count_documents({"ID": {"$in": request.article_ids}})
        if existing_articles != len(request.article_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more article IDs do not exist in the database"
            )
            
        # Validate the requested style against available styles
        try:
            style_key = request.style.upper().strip()
            available_styles = [style.value for style in BlogStyle]
            
            if style_key not in [s.upper() for s in available_styles]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid style. Available styles: {available_styles}"
                )
                
            style = BlogStyle[style_key]
            
        except (KeyError, AttributeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style format. Available styles: {[s.value for s in BlogStyle]}"
            )
            
        # Generate the blog post using the specified style and article IDs
        result = await generate_stylized_blog(request.article_ids, style)
        
        # Check for errors in the result and raise an HTTPException if any
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        # Return the successful response with the generated blog post
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