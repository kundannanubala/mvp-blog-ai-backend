from fastapi import APIRouter, HTTPException
from typing import List
from services.blogServices import fetch_and_generate_blog_posts
from pydantic import BaseModel

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
        # Fetch and generate the blog post content and image using the provided article IDs
        result = await fetch_and_generate_blog_posts(request.article_ids)

        # Check if the result is empty, indicating no content was generated
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No content could be generated from the specified articles",
            )

        # Return the successful result with the blog post content and image path
        return {
            "status": "success",
            "blog_post": result.get("content", ""),
            "image_path": result.get("image_path", ""),
        }

    except Exception as e:
        # Handle any exceptions that occur during the process and raise an HTTPException
        raise HTTPException(
            status_code=500, detail=f"Error generating blog post: {str(e)}"
        )
