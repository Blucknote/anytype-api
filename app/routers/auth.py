"""Authentication router"""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.http import HTTPAuthorizationCredentials

from ..clients.anytype import AnytypeClient, get_anytype_client
from ..helpers.api import APIError
from ..helpers.schemas import DisplayCodeResponse
from ..main import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/display-code", response_model=DisplayCodeResponse)
async def get_auth_display_code(
    app_name: str = "Anytype API",
    client: AnytypeClient = Depends(get_anytype_client),
) -> DisplayCodeResponse:
    """Get display code for authentication"""
    try:
        return await client.get_auth_display_code(app_name)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/token")
async def get_token(
    code: str,
    challenge_id: Optional[str] = None,
    client: AnytypeClient = Depends(get_anytype_client),
):
    """Get authentication token from display code"""
    try:
        return await client.get_token(code, challenge_id)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/validate")
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    client: AnytypeClient = Depends(get_anytype_client),
) -> Dict[str, bool]:
    """Validate authentication token"""
    try:
        valid = await client.validate_token(credentials.credentials)
        return {"valid": valid}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
