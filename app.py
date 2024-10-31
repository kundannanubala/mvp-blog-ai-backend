from fastapi import FastAPI
from api import xml, article
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from scheduler import init_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
    
    # Initialize the scheduler
    scheduler = init_scheduler()
    
    try:
        yield
    finally:
        # Shutdown logic
        scheduler.shutdown()
        app.mongodb_client.close()
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

# Include XML router
app.include_router(xml.router, tags=["Xml"], prefix="/xml")

# Include Article router
app.include_router(article.router, tags=["Article"], prefix="/article")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)