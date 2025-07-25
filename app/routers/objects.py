"""Object management router"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.helpers.schemas import (
    CreateObjectRequest,
    ExportFormat,
    ObjectExportResponse,
    ObjectResponse,
    PaginatedObjectResponse,
    SearchRequest,
)
from app.main import get_validated_token

router = APIRouter(prefix="/spaces/{space_id}/objects", tags=["objects"])


@router.get("", response_model=PaginatedObjectResponse, summary="List objects")
async def list_objects(
    space_id: str,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedObjectResponse:
    """Retrieves a paginated list of objects in the given space."""
    try:
        return await client.get_objects(space_id, limit, offset, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("", response_model=ObjectResponse, summary="Create object")
async def create_object(
    space_id: str,
    request: CreateObjectRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectResponse:
    """Creates a new object in the specified space using a JSON payload."""
    try:
        return await client.create_object(space_id, request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/{object_id}", response_model=ObjectResponse, summary="Get object")
async def get_object(
    space_id: str,
    object_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectResponse:
    """Fetches the full details of a single object identified by the object ID within the specified space."""
    try:
        return await client.get_object(space_id, object_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.delete("/{object_id}", response_model=ObjectResponse, summary="Delete object")
async def delete_object(
    space_id: str,
    object_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectResponse:
    """This endpoint “deletes” an object by marking it as archived."""
    try:
        return await client.delete_object(space_id, object_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get(
    "/{object_id}/{format}",
    response_model=ObjectExportResponse,
    summary="Export object",
)
async def export_object(
    space_id: str,
    object_id: str,
    format: ExportFormat,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectExportResponse:
    """This endpoint exports a single object from the specified space into a desired format."""
    try:
        return await client.get_export(space_id, object_id, format, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post(
    "/search",
    response_model=PaginatedObjectResponse,
    summary="Search objects within a space",
)
async def search_objects(
    space_id: str,
    request: SearchRequest,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedObjectResponse:
    """This endpoint performs a focused search within a single space."""
    try:
        return await client.search_objects(
            space_id, request, limit, offset, token=token
        )
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
