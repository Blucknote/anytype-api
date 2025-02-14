"""Space management router"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from ..clients.anytype import AnytypeClient, get_anytype_client
from ..core.config import settings
from ..helpers.api import APIError
from ..helpers.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ..helpers.schemas import (
    CreateSpaceRequest,
    GetMembersRequest,
    MemberDetails,
    SpaceDetails,
)

router = APIRouter(prefix="/space", tags=["spaces"])


@router.post("/create", response_model=SpaceDetails)
async def create_space(
    request: CreateSpaceRequest,
    client: AnytypeClient = Depends(get_anytype_client),
) -> SpaceDetails:
    """Create a new space in Anytype"""
    try:
        return await client.create_space(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/list", response_model=List[SpaceDetails])
async def get_spaces(
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[SpaceDetails]:
    """Get list of spaces"""
    try:
        return await client.get_spaces(limit, offset)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/members", response_model=List[MemberDetails])
async def get_members(
    request: GetMembersRequest = Depends(),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[MemberDetails]:
    """Get space members"""
    try:
        return await client.get_members(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
