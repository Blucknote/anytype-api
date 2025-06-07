"""FastAPI backend for Anytype integration"""

import logging
from typing import Any, Dict, List, cast

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from .clients.anytype import AnytypeClient, get_anytype_client
from .core.config import Settings
from .core.logging import setup_logging

# Initialize settings and logging
settings = Settings(_env_file=".env")
setup_logging()
logger = logging.getLogger(__name__)

# Log application startup
logger.info("Starting Anytype API application")
logger.debug("Using settings: %s", settings.model_dump_json())

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


# Security scheme
oauth2_scheme = HTTPBearer(
    scheme_name="Bearer", description="Bearer token authentication", auto_error=True
)


async def get_validated_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    client: AnytypeClient = Depends(get_anytype_client),
) -> str:
    """Validate the bearer token and return it if valid"""
    token = credentials.credentials
    try:
        is_valid = await client.validate_token(token)
        if not is_valid:
            logger.warning("Invalid authentication token attempt")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug("Token validation successful")
        return token
    except Exception as e:
        logger.error("Token validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Include routers
from .routers import auth, objects, spaces, tags, types

# Include routers
routers: List[APIRouter] = [
    cast(APIRouter, auth.router),
    cast(APIRouter, spaces.router),
    cast(APIRouter, objects.router),
    cast(APIRouter, types.router),
    cast(APIRouter, tags.router),
]

for router in routers:
    app.include_router(router)
    logger.debug("Registered router: %s", router.prefix if router.prefix else "/")


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint"""
    logger.debug("Handling request to root endpoint")
    return {"message": "Welcome to Anytype API"}


@app.on_event("startup")
async def startup_event() -> None:
    """Handle application startup events"""
    logger.info("Application startup complete")
    logger.info("CORS origins: %s", settings.cors_origins)
    logger.debug("All routers initialized and ready")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Handle application shutdown events"""
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
