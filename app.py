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
    scheduler = None  # Initialize scheduler variable
    
    # Startup logic
    try:
        # Add MongoDB connection with correct settings
        app.mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        # Test the connection
        await app.mongodb_client.admin.command('ping')
        app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
        print("Successfully connected to MongoDB")
        
        # Initialize the scheduler
        scheduler = init_scheduler()
        
        yield
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise
    finally:
        # Shutdown logic
        if hasattr(app, 'mongodb_client'):
            app.mongodb_client.close()
        if scheduler:
            scheduler.shutdown()
        print("MongoDB connection closed and scheduler shutdown successfully.")

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(xml.router, tags=["Xml"], prefix="/xml")
app.include_router(article.router, tags=["Article"], prefix="/article")
app.include_router(user.router, tags=["User"], prefix="/user")
app.include_router(rag.router, tags=["RAG"], prefix="/rag")
app.include_router(keyword.router, tags=["Keyword"], prefix="/keyword")
app.include_router(blog.router, tags=["Blog"], prefix="/blog")

@app.exception_handler(ServerSelectionTimeoutError)
async def database_exception_handler(request: Request, exc: ServerSelectionTimeoutError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection error. Please try again later."}
    )

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)