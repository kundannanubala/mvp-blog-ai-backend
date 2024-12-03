"""
This module handles the generation of blog posts using the Vertex AI client and LangChain.
It includes functions to generate blog posts from scraped content and fetch specific articles.
"""

# Importing the necessary modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from google.cloud import aiplatform
import os
import asyncio
from datetime import datetime
from core.config import settings
from services.articleServices import get_articles_by_ids
from services.imageServices import generate_image_vertexai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_blog_post(scrape_result: str) -> dict:
    """Generate a blog post with enhanced error handling."""
    try:
        # Validate input
        if not scrape_result or len(scrape_result.strip()) < 100:
            logger.error("Insufficient content for blog generation")
            return {"error": "Insufficient content for blog generation"}

        # Initialize Vertex AI
        aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT)
        
        # Configure LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-002",
            temperature=0.2,
            max_output_tokens=4096,
            top_p=0.95,
            top_k=40
        )

        # Create prompt template
        prompt = ChatPromptTemplate.from_template("""
            Create a professional blog post based on the following content:
            {context}
            
            Make sure to:
            1. Use a clear and engaging writing style
            2. Include relevant headings and subheadings
            3. Maintain professional tone
            4. Add a compelling conclusion
            """)

        # Create chain
        chain = (
            {"context": lambda x: scrape_result}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Generate content
        logger.info("Generating blog content...")
        result = await asyncio.to_thread(chain.invoke, {"context": scrape_result})
        
        if not result:
            logger.error("Failed to generate blog content")
            return {"error": "Failed to generate blog content"}

        # Generate image
        logger.info("Generating blog image...")
        image_path = await generate_image_vertexai(result[:1000])  # Use first 1000 chars for image context

        return {
            "content": str(result),
            "image_path": image_path,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Blog generation error: {str(e)}")
        return {"error": f"Blog generation failed: {str(e)}"}

async def fetch_and_generate_blog_posts(article_ids: list) -> dict:
    """Fetch articles and generate blog post with image."""
    try:
        # Get articles content
        articles = await get_articles_by_ids(article_ids)
        if not articles:
            logger.error("No articles found with provided IDs")
            return {"error": "No articles found"}

        # Combine article content
        combined_content = "\n\n".join(articles)
        
        # Generate blog post
        result = await generate_blog_post(combined_content)
        
        return result

    except Exception as e:
        logger.error(f"Error in fetch_and_generate_blog_posts: {str(e)}")
        return {"error": str(e)}
