"""Tag management router"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.helpers.schemas import (
    CreateTagRequest,
    PaginatedTagResponse,
    TagResponse,
    UpdateTagRequest,
)
from app.main import get_validated_token

router = APIRouter(
    prefix="/spaces/{space_id}/properties/{property_id}/tags", tags=["tags"]
)


@router.get("", response_model=PaginatedTagResponse, summary="List tags")
async def list_tags(
    space_id: str,
    property_id: str,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedTagResponse:
    """Retrieves a paginated list of tags available for a specific property within a space."""
    try:
        return await client.get_tags(space_id, property_id, limit, offset, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("", response_model=TagResponse, summary="Create tag")
async def create_tag(
    space_id: str,
    property_id: str,
    request: CreateTagRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> TagResponse:
    """Creates a new tag for a given property id in a space."""
    try:
        return await client.create_tag(space_id, property_id, request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/{tag_id}", response_model=TagResponse, summary="Get tag")
async def get_tag(
    space_id: str,
    property_id: str,
    tag_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> TagResponse:
    """Retrieves a tag for a given property id with details like ID, name, and color."""
    try:
        return await client.get_tag(space_id, property_id, tag_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.patch("/{tag_id}", response_model=TagResponse, summary="Update tag")
async def update_tag(
    space_id: str,
    property_id: str,
    tag_id: str,
    request: UpdateTagRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> TagResponse:
    """Updates a tag for a given property id in a space."""
    try:
        return await client.update_tag(space_id, property_id, tag_id, request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.delete("/{tag_id}", response_model=TagResponse, summary="Delete tag")
async def delete_tag(
    space_id: str,
    property_id: str,
    tag_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> TagResponse:
    """Deletes a tag by marking it as archived."""
    try:
        return await client.delete_tag(space_id, property_id, tag_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e