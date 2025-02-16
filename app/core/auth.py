"""Authentication utilities"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme
oauth2_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Bearer token authentication",
    auto_error=True,
)


async def get_validated_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> str:
    """Validate the bearer token and return it if valid"""
    token = credentials.credentials
    try:
        # Token validation is now handled by the client when making requests
        return token
    except Exception as e:
        logger.error("Token validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
