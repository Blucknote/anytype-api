"""Authentication router"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.http import HTTPAuthorizationCredentials

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.schemas import ChallengeResponse, TokenResponse
from app.main import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/challenge", response_model=ChallengeResponse)
async def create_challenge(
    app_name: str,
    client: AnytypeClient = Depends(get_anytype_client),
) -> ChallengeResponse:
    """Create authentication challenge (step 1 of new auth flow)"""
    try:
        return await client.create_challenge(app_name)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/api_key", response_model=TokenResponse)
async def create_api_key(
    code: str,
    challenge_id: str,
    client: AnytypeClient = Depends(get_anytype_client),
) -> TokenResponse:
    """Create API key using challenge_id and code (step 2 of new auth flow)"""
    try:
        return await client.create_api_key(code, challenge_id)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
