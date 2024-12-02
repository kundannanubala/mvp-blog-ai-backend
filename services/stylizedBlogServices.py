"""
This module handles the generation of stylized blog posts using different writing styles
through the Vertex AI client and LangChain.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from google.cloud import aiplatform
import asyncio
from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import dotenv
from services.articleServices import get_articles_by_ids
from services.imageServices import generate_image_vertexai
from enum import Enum

# Load environment variables
dotenv.load_dotenv()

class BlogStyle(Enum):
    """Enum defining different blog writing styles"""
    ACADEMIC = "academic"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"
    JOURNALISTIC = "journalistic"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    OPINION = "opinion"

def get_style_prompt(style: BlogStyle) -> str:
    """
    Get the specific prompt template for a given blog style.
    
    Args:
        style (BlogStyle): The desired writing style for the blog.
    
    Returns:
        str: The prompt template for the specified style.
    """
    style_prompts = {
        BlogStyle.ACADEMIC: """
            Write in an academic style following these guidelines:
            - Use formal language and technical terminology
            - Include citations and references where appropriate
            - Structure with clear thesis and supporting arguments
            - Maintain objective tone throughout
            - Include methodology and evidence-based conclusions
            
            Context: {context}
        """,
        
        BlogStyle.CONVERSATIONAL: """
            Write in a conversational style following these guidelines:
            - Use casual, friendly language
            - Include personal anecdotes and examples
            - Engage reader with questions and dialogue
            - Use contractions and informal expressions
            - Keep paragraphs short and digestible
            
            Context: {context}
        """,
        
        BlogStyle.TECHNICAL: """
            Write in a technical style following these guidelines:
            - Focus on detailed technical specifications
            - Include code examples or technical diagrams where relevant
            - Use industry-standard terminology
            - Provide step-by-step explanations
            - Include practical applications
            
            Context: {context}
        """,
        
        BlogStyle.STORYTELLING: """
            Write in a storytelling style following these guidelines:
            - Begin with a compelling hook
            - Develop a narrative arc
            - Include character or situation development
            - Use descriptive language and imagery
            - End with a meaningful conclusion
            
            Context: {context}
        """,
        
        BlogStyle.JOURNALISTIC: """
            Write in a journalistic style following these guidelines:
            - Follow inverted pyramid structure
            - Include who, what, when, where, why, and how
            - Use objective reporting language
            - Include relevant quotes and sources
            - Maintain factual accuracy
            
            Context: {context}
        """,
        
        BlogStyle.TUTORIAL: """
            Write in a tutorial style following these guidelines:
            - Start with clear learning objectives
            - Break down into step-by-step instructions
            - Include examples and practical applications
            - Add tips and common pitfalls
            - End with a summary and next steps
            
            Context: {context}
        """,
        
        BlogStyle.REVIEW: """
            Write in a review style following these guidelines:
            - Begin with an overview
            - Include pros and cons analysis
            - Provide detailed evaluation criteria
            - Use comparative analysis where relevant
            - End with a clear recommendation
            
            Context: {context}
        """,
        
        BlogStyle.OPINION: """
            Write in an opinion style following these guidelines:
            - State clear position or thesis
            - Support arguments with evidence
            - Address counter-arguments
            - Use persuasive language
            - Include personal insights
            
            Context: {context}
        """
    }
    
    return style_prompts.get(style, style_prompts[BlogStyle.CONVERSATIONAL])

async def generate_stylized_blog(article_ids: list, style: BlogStyle) -> dict:
    """
    Generate a blog post in a specific style using the provided article IDs as context.
    
    Args:
        article_ids (list): List of article IDs to use as context
        style (BlogStyle): The desired writing style for the blog
        
    Returns:
        dict: Generated blog post content and metadata
    """
    try:
        # Get articles content
        articles_content = await get_articles_by_ids(article_ids)
        combined_content = "\n\n".join(articles_content)
        
        if not combined_content:
            return {"error": "No content found for the provided article IDs"}
            
        # Initialize Vertex AI
        aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT)
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-002",
            temperature=0.7,
            max_output_tokens=8000,
        )
        
        # Get style-specific prompt
        style_prompt = get_style_prompt(style)
        
        # Create chain
        chain = {"context": lambda x: x} | style_prompt | llm | StrOutputParser()
        
        # Generate blog post
        result = await asyncio.to_thread(chain.invoke, combined_content)
        
        # Generate complementary image
        image_path = await generate_image_vertexai(result)
        
        return {
            "content": result,
            "style": style.value,
            "image_path": image_path,
            "source_articles": article_ids
        }
        
    except Exception as e:
        return {"error": str(e)}

async def generate_multi_style_blogs(article_ids: list, styles: list[BlogStyle] = None) -> dict:
    """
    Generate multiple versions of a blog post in different styles.
    
    Args:
        article_ids (list): List of article IDs to use as context
        styles (list[BlogStyle]): List of styles to generate (defaults to all styles if None)
        
    Returns:
        dict: Dictionary containing blog versions in different styles
    """
    try:
        if styles is None:
            styles = list(BlogStyle)
            
        tasks = [generate_stylized_blog(article_ids, style) for style in styles]
        results = await asyncio.gather(*tasks)
        
        return {
            style.value: result 
            for style, result in zip(styles, results)
            if "error" not in result
        }
        
    except Exception as e:
        return {"error": str(e)} 