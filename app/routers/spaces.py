"""Space management router"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.helpers.schemas import (
    CreateSpaceRequest,
    MemberResponse,
    PaginatedMemberResponse,
    PaginatedSpaceResponse,
    SpaceResponse,
)
from app.main import get_validated_token

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("", response_model=PaginatedSpaceResponse, summary="List spaces")
async def list_spaces(
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedSpaceResponse:
    """Retrieves a paginated list of all spaces that are accessible by the authenticated user."""
    try:
        return await client.get_spaces(limit, offset, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("", response_model=SpaceResponse, summary="Create space")
async def create_space(
    request: CreateSpaceRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> SpaceResponse:
    """Creates a new workspace (or space) based on a supplied name in the JSON request body."""
    try:
        return await client.create_space(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/{space_id}", response_model=SpaceResponse, summary="Get space")
async def get_space(
    space_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> SpaceResponse:
    """Fetches full details about a single space identified by its space ID."""
    try:
        return await client.get_space(space_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get(
    "/{space_id}/members",
    response_model=PaginatedMemberResponse,
    summary="List members",
)
async def list_members(
    space_id: str,
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedMemberResponse:
    """Returns a paginated list of members belonging to the specified space."""
    try:
        return await client.get_members(space_id, limit, offset, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get(
    "/{space_id}/members/{member_id}",
    response_model=MemberResponse,
    summary="Get member",
)
async def get_member(
    space_id: str,
    member_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> MemberResponse:
    """Fetches detailed information about a single member within a space."""
    try:
        return await client.get_member(space_id, member_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
