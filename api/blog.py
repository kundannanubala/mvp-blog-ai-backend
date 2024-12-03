from fastapi import APIRouter, HTTPException
from typing import List
from services.blogServices import fetch_and_generate_blog_posts
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI router for handling blog-related endpoints
router = APIRouter()

class BlogGenerationRequest(BaseModel):
    """
    Data model for the request body when generating a blog post.

    Attributes:
        article_ids (List[str]): A list of article IDs to be used for generating the blog post.
    """
    article_ids: List[str]

@router.post("/generate-blog")
async def generate_blog_from_articles(request: BlogGenerationRequest):
    """
    Endpoint to generate a blog post with an image from specified articles.

    This function takes a list of article IDs, fetches the corresponding articles,
    and generates a blog post along with an associated image.

    Args:
        request (BlogGenerationRequest): The request object containing a list of article IDs.

    Returns:
        dict: A dictionary containing the status of the operation, the generated blog post content,
              and the path to the generated image.

    Raises:
        HTTPException: If no content could be generated from the specified articles or if an error occurs
                       during the blog post generation process.
    """
    try:
        logger.info(f"Generating blog from articles: {request.article_ids}")
        result = await fetch_and_generate_blog_posts(request.article_ids)
        
        if "error" in result:
            logger.error(f"Error generating blog: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
        if not result.get("content"):
            logger.error("No content generated")
            raise HTTPException(
                status_code=404,
                detail="No content could be generated from the specified articles"
            )
            
        return {
            "status": "success",
            "blog_post": result.get("content", ""),
            "image_path": result.get("image_path", ""),
            "timestamp": result.get("timestamp")
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error generating blog: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the blog post: {str(e)}"
        )
