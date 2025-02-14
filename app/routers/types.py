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
from ..main import get_validated_token

router = APIRouter(tags=["types"])


@router.get("/type/list", response_model=List[TypeDetails])
async def get_types(
    request: GetTypesRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[TypeDetails]:
    """Get object types"""
    try:
        return await client.get_types(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/template/list", response_model=List[TemplateDetails])
async def get_templates(
    request: GetTemplatesRequest,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[TemplateDetails]:
    """Get templates"""
    try:
        return await client.get_templates(request, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
