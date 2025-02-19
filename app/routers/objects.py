"""Object management router"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.schemas import (
    BaseResponse,
    CreateObjectRequest,
    DeleteObjectRequest,
    ExportFormat,
    GetObjectsRequest,
    GlobalSearchRequest,
    ObjectDetails,
    SearchRequest,
    SortOptions,
    SortOrder,
)
from app.main import get_validated_token

router = APIRouter(prefix="/object", tags=["objects"])


@router.post("/create", response_model=ObjectDetails)
async def create_object(
    request: CreateObjectRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectDetails:
    """Create a new object in Anytype"""
    try:
        return await client.create_object(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/get/{space_id}/{object_id}", response_model=ObjectDetails)
async def get_object(
    space_id: str,
    object_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> ObjectDetails:
    """Get object details"""
    try:
        return await client.get_object(space_id, object_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/list", response_model=List[ObjectDetails])
async def get_objects(
    space_id: str,
    types: Optional[str] = None,
    limit: Optional[int] = Query(default=50, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    sort: Optional[SortOrder] = Query(default=SortOrder.LAST_MODIFIED_DATE),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[ObjectDetails]:
    """Get objects list"""
    try:
        type_list = types.split(",") if types else None
        sort_options = SortOptions(
            direction="desc", timestamp=sort.value if sort else "last_modified_date"
        )
        request = SearchRequest(
            space_id=space_id,
            query="",
            types=type_list,
            limit=limit,
            offset=offset,
            sort=sort_options,
        )
        return await client.search_objects(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/delete", response_model=BaseResponse)
async def delete_object(
    request: DeleteObjectRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> BaseResponse:
    """Delete an object from Anytype"""
    try:
        return await client.delete_object(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/search", response_model=List[ObjectDetails])
async def search_objects(
    request: SearchRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[ObjectDetails]:
    """Search for objects in Anytype with advanced filtering and sorting"""
    try:
        return await client.search_objects(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.post("/search/global", response_model=List[ObjectDetails])
async def global_search(
    request: GlobalSearchRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[ObjectDetails]:
    """Global search across all spaces"""
    try:
        return await client.global_search(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/export/{space_id}/{object_id}", response_model=Dict[str, str])
async def get_export(
    space_id: str,
    object_id: str,
    export_format: ExportFormat = Query(
        ExportFormat.MARKDOWN, description="Export format"
    ),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> Dict[str, str]:
    """Export an object in the specified format"""
    try:
        content = await client.get_export(
            space_id, object_id, export_format, token=token
        )
        return {"content": content}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
