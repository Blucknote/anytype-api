"""Type and template management router"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.schemas import (
    TemplateDetails,
    TypeDetails,
)
from app.main import get_validated_token

router = APIRouter(tags=["types"])


@router.get("/type/list", response_model=List[TypeDetails])
async def get_types(
    space_id: Optional[str] = Query(None),
    include_system: Optional[bool] = Query(True),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[TypeDetails]:
    """Get object types"""
    try:
        return await client.get_types(
            space_id=space_id, include_system=include_system, token=token
        )
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/template/list", response_model=List[TemplateDetails])
async def get_templates(
    space_id: Optional[str] = Query(None),
    type_id: Optional[str] = Query(None),
    include_system: Optional[bool] = Query(True),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> List[TemplateDetails]:
    """Get templates"""
    try:
        return await client.get_templates(
            space_id=space_id,
            type_id=type_id,
            include_system=include_system,
            token=token,
        )
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
