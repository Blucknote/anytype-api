"""Authentication router"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.http import HTTPAuthorizationCredentials

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.schemas import DisplayCodeResponse, TokenResponse
from app.main import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/display_code", response_model=DisplayCodeResponse)
async def get_auth_display_code(
    app_name: str,
    client: AnytypeClient = Depends(get_anytype_client),
) -> DisplayCodeResponse:
    """Start new challenge"""
    try:
        return await client.get_auth_display_code(app_name)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/token", response_model=TokenResponse)
async def get_token(
    code: str,
    challenge_id: str,
    client: AnytypeClient = Depends(get_anytype_client),
) -> TokenResponse:
    """Retrieve token"""
    try:
        return await client.get_token(code, challenge_id)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
