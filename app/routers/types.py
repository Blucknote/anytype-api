"""Type and template management router"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from ..clients.anytype import AnytypeClient, get_anytype_client
from ..helpers.api import APIError
from ..helpers.schemas import (
    GetTemplatesRequest,
    GetTypesRequest,
    TemplateDetails,
    TypeDetails,
)

router = APIRouter(tags=["types"])


@router.get("/type/list", response_model=List[TypeDetails])
async def get_types(
    request: GetTypesRequest = Depends(),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[TypeDetails]:
    """Get object types"""
    try:
        return await client.get_types(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/template/list", response_model=List[TemplateDetails])
async def get_templates(
    request: GetTemplatesRequest = Depends(),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[TemplateDetails]:
    """Get templates"""
    try:
        return await client.get_templates(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
