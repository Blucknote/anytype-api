"""Object management router"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ..clients.anytype import AnytypeClient, get_anytype_client
from ..helpers.api import APIError
from ..helpers.schemas import (
    BaseResponse,
    CreateObjectRequest,
    DeleteObjectRequest,
    ExportFormat,
    GetObjectsRequest,
    GlobalSearchRequest,
    ObjectDetails,
    SearchRequest,
    SortOrder,
)

router = APIRouter(prefix="/object", tags=["objects"])


@router.post("/create", response_model=ObjectDetails)
async def create_object(
    request: CreateObjectRequest,
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectDetails:
    """Create a new object in Anytype"""
    try:
        return await client.create_object(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/get/{space_id}/{object_id}", response_model=ObjectDetails)
async def get_object(
    space_id: str,
    object_id: str,
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectDetails:
    """Get object details"""
    try:
        return await client.get_object(space_id, object_id)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/list", response_model=List[ObjectDetails])
async def get_objects(
    space_id: str,
    types: Optional[str] = None,
    limit: Optional[int] = Query(default=50, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    sort: Optional[SortOrder] = Query(default=SortOrder.LAST_MODIFIED_DATE),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[ObjectDetails]:
    """Get objects list"""
    try:
        type_list = types.split(",") if types else None
        request = GetObjectsRequest(
            space_id=space_id,
            types=type_list,
            limit=limit,
            offset=offset,
            sort=sort,
        )
        return await client.get_objects(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/delete", response_model=BaseResponse)
async def delete_object(
    request: DeleteObjectRequest,
    client: AnytypeClient = Depends(get_anytype_client),
) -> BaseResponse:
    """Delete an object from Anytype"""
    try:
        return await client.delete_object(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/search", response_model=List[ObjectDetails])
async def search_objects(
    request: SearchRequest,
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[ObjectDetails]:
    """Search for objects in Anytype with advanced filtering and sorting"""
    try:
        return await client.search_objects(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/search/global", response_model=List[ObjectDetails])
async def global_search(
    request: GlobalSearchRequest,
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[ObjectDetails]:
    """Global search across all spaces"""
    try:
        return await client.global_search(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/export/{space_id}/{object_id}")
async def get_export(
    space_id: str,
    object_id: str,
    format: ExportFormat = Query(ExportFormat.MARKDOWN, description="Export format"),
    client: AnytypeClient = Depends(get_anytype_client),
) -> dict:
    """Export an object in the specified format"""
    try:
        content = await client.get_export(space_id, object_id, format)
        return {"content": content}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
