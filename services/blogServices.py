'''Import necessary libraries
Setting up the Vertex AI client
Setting up the LLM using langchain and Vertex AI client
Setting up the prompt template
chain will be defined in the /retrieve-vectors endpoint
'''
#Importing the necessary modules
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
dotenv.load_dotenv()
async def generate_blog_post(scrape_result: str) -> dict:
    # Initialize the Vertex AI client
    aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT)

    # Initialize the LLM with structured output configuration
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-002",
        temperature=0.2,
        max_output_tokens=4096,
        top_p=0.95,
        top_k=40,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "introduction": {"type": "string"},
                    "list_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "heading": {"type": "string"},
                                "description": {"type": "string"},
                                "examples": {"type": "array", "items": {"type": "string"}},
                                "media_reference": {"type": "string", "nullable": True}
                            },
                            "required": ["heading", "description", "examples"]
                        }
                    },
                    "conclusion": {"type": "string"},
                    "cta": {"type": "string"}
                },
                "required": ["title", "introduction", "list_items", "conclusion", "cta"]
            }
        }
    )

    # Update the prompt template to match expected variables
    prompt = ChatPromptTemplate.from_template("""
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
    """)

    try:
        # Create chain with proper context handling
        chain = (
            {"context": lambda x: x}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Invoke the chain with the scrape result
        result = await asyncio.to_thread(chain.invoke, scrape_result)
        return result
    except Exception as e:
        return {"error": str(e)}

def blog_prompt_template():

    listicle_blog_post_prompt="""
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
        article_ids: List of article IDs to process

    Returns:
        dict: A dictionary of generated blog posts
    """
    # Get scrape results using the article service
    scrape_results = await get_articles_by_ids(article_ids)
    
    # Combine all scrape results
    combined_content = "\n\n".join(scrape_results)
    
    if combined_content:
        # Generate blog post from combined content
        blog_post = await generate_blog_post(combined_content)
        
        # Generate image based on the blog post content
        image_path = await generate_image_vertexai(blog_post)
        
        return {
            "content": blog_post,
            "image_path": image_path
        }
    
    return {}

# print(asyncio.run(fetch_and_generate_blog_posts()))