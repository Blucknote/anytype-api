"""Type and template management router"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.anytype import AnytypeClient, get_anytype_client
from app.helpers.api import APIError
from app.helpers.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.helpers.schemas import (
    PaginatedTemplateResponse,
    PaginatedTypeResponse,
    TemplateResponse,
    TypeResponse,
)
from app.main import get_validated_token

router = APIRouter(prefix="/spaces/{space_id}/types", tags=["types"])


@router.get("", response_model=PaginatedTypeResponse, summary="List types")
async def list_types(
    space_id: str,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedTypeResponse:
    """Retrieves a paginated list of object types available within the specified space."""
    try:
        return await client.get_types(space_id, limit, offset, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get("/{type_id}", response_model=TypeResponse, summary="Get type")
async def get_type(
    space_id: str,
    type_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> TypeResponse:
    """Fetches detailed information about one specific object type by its ID."""
    try:
        return await client.get_type(space_id, type_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get(
    "/{type_id}/templates",
    response_model=PaginatedTemplateResponse,
    summary="List templates",
)
async def list_templates(
    space_id: str,
    type_id: str,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> PaginatedTemplateResponse:
    """Returns a paginated list of templates that are associated with a specific object type within a space."""
    try:
        return await client.get_templates(space_id, type_id, limit, offset, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e


@router.get(
    "/{type_id}/templates/{template_id}",
    response_model=TemplateResponse,
    summary="Get template",
)
async def get_template(
    space_id: str,
    type_id: str,
    template_id: str,
    token: str = Depends(get_validated_token),
    client: AnytypeClient = Depends(get_anytype_client),
) -> TemplateResponse:
    """Fetches full details for one template associated with a particular object type in a space."""
    try:
        return await client.get_template(space_id, type_id, template_id, token=token)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
