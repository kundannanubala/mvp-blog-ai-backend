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
from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import dotenv
from services.articleServices import get_articles_by_ids
from services.imageServices import generate_image_vertexai
from services.personaServices import get_user_persona

# Load environment variables from a .env file
dotenv.load_dotenv()

async def generate_blog_post(scrape_result: str, username: str) -> dict:
    """
    Generate a blog post from the given scrape result using Vertex AI and LangChain.

    Args:
        scrape_result (str): The scraped content to be used for generating the blog post.
        username (str): The username of the user.

    Returns:
        dict: A dictionary containing the generated blog post content or an error message.
    """
    try:
        # Get user's persona
        user_persona = await get_user_persona(username)
        
        # Initialize the Vertex AI client
        aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT)
        
        # Initialize the LLM with structured output configuration
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-002",
            temperature=0.2,
            max_output_tokens=4096,
        )
        
        # Update the prompt template to include persona information
        persona_prompt = f"""
        Write in the following style:
        - Writing style: {user_persona.writing_style}
        - Tone: {user_persona.tone}
        - Expertise level: {user_persona.expertise_level}
        - Target audience: {user_persona.target_audience}
        - Language style: {user_persona.language_style}
        
        Content should be formatted according to these preferences:
        {user_persona.formatting_preferences}
        """
        
        # Combine the persona prompt with the original prompt
        combined_prompt = persona_prompt + "\n\n" + blog_prompt_template()
        
        # Create chain with proper context handling
        chain = {"context": lambda x: x} | combined_prompt | llm | StrOutputParser()
        
        # Generate the blog post
        result = await asyncio.to_thread(chain.invoke, scrape_result)
        return result
        
    except Exception as e:
        return {"error": str(e)}

def blog_prompt_template() -> str:
    """
    Generate a prompt template for creating a listicle blog post.

    Returns:
        str: The prompt template string.
    """
    listicle_blog_post_prompt = """
        You are tasked with generating a listicle blog post. Follow the steps below to ensure clarity, accuracy, and coherence. Avoid hallucination by strictly adhering to the provided variables from the context.
        context:{context}

        **Variables:**
        - **Title**: title
        - **Keywords**: keywords
        - **Number of Items**: num_items
        - **Examples**: examples
        - **Media**:media
        - **Internal/External Links**: links

        **Step-by-Step Structure:**
        1. **Title**: Start with a catchy title that includes a number and the central theme, e.g., "10 Best Tools for SEO."
        2. **Introduction**: Introduce the topic with a 2-3 sentence overview. Explain the importance of the list and how it will benefit the reader.
        3. **List Items**: For each item:
        - **H3 Heading for Each Item**: Provide a descriptive heading.
        - **2-3 Sentence Description**: Describe the item and its significance.
        - **Examples**: Include provided examples where relevant.
        - **Media Reference**: If applicable, include where visuals should be.
        4. **Conclusion**: Summarize the key points and restate the value. Include a call to action (CTA).

        Generate the textual content based on the variables provided.
        """

    """
        Generates a prompt for creating a how-to blog post with enhanced structure, chain-of-thought, and task breakdown.
        Args:
        - title: The title of the how-to post.
        - problem_statement: The problem that is being solved.
        - steps: Detailed steps for solving the problem.
        - tips: Optional - Tips or warnings.
        - media: Optional - media references (images, videos).
        - seo_keywords: Optional - SEO keywords to be used.

        Returns:
        - Prompt string for a how-to blog post with structured breakdown.
        """
    return listicle_blog_post_prompt

async def fetch_and_generate_blog_posts(article_ids: list) -> dict:
    """
    Fetch specific articles and generate blog posts using the combined scraped content.

    Args:
        article_ids (list): List of article IDs to process.

    Returns:
        dict: A dictionary containing the generated blog posts and image paths.
    """
    # Get scrape results using the article service
    scrape_results = await get_articles_by_ids(article_ids)

    # Combine all scrape results into a single string
    combined_content = "\n\n".join(scrape_results)

    if combined_content:
        # Generate blog post from combined content
        blog_post = await generate_blog_post(combined_content)

        # Generate image based on the blog post content
        image_path = await generate_image_vertexai(blog_post)

        return {"content": blog_post, "image_path": image_path}

    return {}

# Uncomment the line below to test the function
# print(asyncio.run(fetch_and_generate_blog_posts()))
