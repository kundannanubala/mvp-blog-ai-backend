from fastapi import FastAPI
from api import xml
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
    try:
        yield
    finally:
        # Shutdown logic
        app.mongodb_client.close()
        print("MongoDB connection closed successfully.")

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

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)