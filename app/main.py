"""FastAPI backend for Anytype integration"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
from .routers import auth, objects, spaces, types

app.include_router(auth.router)
app.include_router(spaces.router)
app.include_router(objects.router)
app.include_router(types.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Anytype API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
