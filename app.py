from fastapi import FastAPI, Request
from api import xml, article, user, rag, keyword, blog
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from scheduler import init_scheduler
from fastapi.responses import JSONResponse
from pymongo.errors import ServerSelectionTimeoutError
import certifi

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for managing the lifespan of the FastAPI application.

    This function handles the startup and shutdown processes, including:
    - Establishing a connection to the MongoDB database.
    - Initializing a scheduler for background tasks.
    - Ensuring proper cleanup of resources on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    scheduler = None  # Initialize the scheduler variable to None

    # Startup logic
    try:
        # Establish a connection to MongoDB using the provided URI and settings
        app.mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,  # Timeout for server selection
        )
        # Test the MongoDB connection by sending a ping command
        await app.mongodb_client.admin.command("ping")
        app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
        print("Successfully connected to MongoDB")

        # Initialize the scheduler for background tasks
        scheduler = init_scheduler()

        yield  # Yield control back to the application
    except Exception as e:
        # Handle exceptions during startup, such as connection failures
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise
    finally:
        # Shutdown logic
        if hasattr(app, "mongodb_client"):
            # Close the MongoDB client connection
            app.mongodb_client.close()
        if scheduler:
            # Shutdown the scheduler if it was initialized
            scheduler.shutdown()
        print("MongoDB connection closed and scheduler shutdown successfully.")

# Initialize the FastAPI application with a custom lifespan context manager
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow cross-origin requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify allowed frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routers for different modules with specified tags and prefixes
app.include_router(xml.router, tags=["Xml"], prefix="/xml")
app.include_router(article.router, tags=["Article"], prefix="/article")
app.include_router(user.router, tags=["User"], prefix="/user")
app.include_router(rag.router, tags=["RAG"], prefix="/rag")
app.include_router(keyword.router, tags=["Keyword"], prefix="/keyword")
app.include_router(blog.router, tags=["Blog"], prefix="/blog")

@app.exception_handler(ServerSelectionTimeoutError)
async def database_exception_handler(request: Request, exc: ServerSelectionTimeoutError):
    """
    Exception handler for MongoDB server selection timeout errors.

    Returns a JSON response with a 503 status code indicating a database connection error.

    Args:
        request (Request): The incoming request object.
        exc (ServerSelectionTimeoutError): The exception instance.

    Returns:
        JSONResponse: A JSON response with error details.
    """
    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection error. Please try again later."},
    )

# Run the FastAPI application using Uvicorn when executed as the main module
if __name__ == "__main__":
    import uvicorn

    # Start the Uvicorn server with specified host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
