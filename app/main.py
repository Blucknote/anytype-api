"""FastAPI backend for Anytype integration"""

import logging

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from .clients.anytype import AnytypeClient, get_anytype_client
from .core.config import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings(_env_file=".env")

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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


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
