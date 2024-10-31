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
dotenv.load_dotenv()
async def generate_blog_post(scrape_result: str) -> str:
    # Initialize the Vertex AI client
    aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT)

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-002", temperature=0.2, max_output_tokens=4096, top_p=0.95, top_k=40)

    # Setting up the prompt template
    prompt = ChatPromptTemplate.from_template(blog_prompt_template())

    try:
        context = {"context": lambda x: scrape_result}
        chain = (
            context
            | prompt
            | llm
            | StrOutputParser()
        )
        # Directly invoke the chain and await the result
        result = await asyncio.to_thread(chain.invoke, context)
        return str(result)
    except Exception as e:
        return f"An error occurred: {str(e)}"

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

async def fetch_and_generate_blog_posts() -> list:
    """
    Fetch articles from MongoDB and generate blog posts using the scraped content.

    Returns:
        list: A list of generated blog posts.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['articles']

    try:
        articles = await collection.find().to_list(length=None)
        generated_blog_posts = []

        for article in articles:
            scraped_content = article.get('scrape_result')
            if scraped_content:
                blog_post = await generate_blog_post(scraped_content)
                generated_blog_posts.append(blog_post+'\n***********************************')

        return generated_blog_posts
    finally:
        client.close()

# print(asyncio.run(fetch_and_generate_blog_posts()))