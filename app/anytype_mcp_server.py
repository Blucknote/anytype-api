#!/usr/bin/env python3
import logging
import os
from typing import List, Optional

from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from mcp.server.fastmcp import FastMCP

from app.clients.anytype import AnytypeClient
from app.helpers.schemas import (
    CreateObjectRequest,
    CreateSpaceRequest,
    DeleteObjectRequest,
    ExportFormat,
    GetMembersRequest,
    GlobalSearchRequest,
    MemberDetails,
    ObjectDetails,
    SearchRequest,
    SortOrder,
    SpaceDetails,
    TemplateDetails,
    TypeDetails,
)

logger = logging.getLogger("anytype_mcp_server")

mcp = FastMCP("anytype-api")

API_URL = os.environ.get("ANYTYPE_API_URL", "")
SESSION_TOKEN = os.environ.get("ANYTYPE_SESSION_TOKEN", "")
APP_KEY = os.environ.get("ANYTYPE_APP_KEY", "")
TOKEN = APP_KEY

client = AnytypeClient(
    base_url=API_URL,
    session_token=SESSION_TOKEN,
    app_key=APP_KEY,
)


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract Bearer token from Authorization header in the incoming request.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    scheme, param = get_authorization_scheme_param(auth_header)
    if scheme.lower() != "bearer" or not param:
        return None
    return param


@mcp.tool()
async def create_object(
    space_id: str,
    name: str,
    body: str,
    object_type_unique_key: str,
    template_id: Optional[str] = "",
    description: Optional[str] = None,
    icon: Optional[str] = None,
    source: Optional[str] = None,
    token: Optional[str] = TOKEN,
) -> ObjectDetails:
    """
    Create a new object in Anytype.

    Args:
        space_id: ID of the space to create the object in (required).
        name: Name of the object (required).
        object_type_unique_key: Unique key of the object type (required).
        template_id: Template ID to use for the object. Preferred to be "" (empty string) if not using a template.
        body: content for the object body, Markdown supported
        description: Description of the object (optional).
        icon: Icon for the object (optional).
        source: Source for the object (optional).
        token: Optional authentication token.

    Returns:
        The created object details.
    """
    payload = {
        "space_id": space_id,
        "name": name,
        "object_type_unique_key": object_type_unique_key,
        "template_id": template_id if template_id is not None else "",
        "body": body,
        "description": description,
        "icon": icon,
        "source": source,
    }
    # Remove keys with value None to avoid sending them unnecessarily
    payload = {k: v for k, v in payload.items() if v is not None}
    # Use the OpenAPI-compliant client method
    response = await client.create_object_in_space(space_id, payload, token=token)
    return (
        ObjectDetails(**response["object"]) if "object" in response else ObjectDetails()
    )


@mcp.tool()
async def get_object(
    space_id: str, object_id: str, token: Optional[str] = TOKEN
) -> ObjectDetails:
    """
    Get object details

    Args:
        space_id: ID of the space containing the object
        object_id: ID of the object to retrieve
    """
    return await client.get_object(space_id, object_id, token=token)


@mcp.tool()
async def list_objects(
    space_id: str,
    types: Optional[List[str]] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    sort: Optional[SortOrder] = SortOrder.LAST_MODIFIED_DATE,
    token: Optional[str] = TOKEN,
) -> List[ObjectDetails]:
    """
    Get objects list

    Args:
        space_id: ID of the space to list objects from
        types: Optional list of object types to filter by
        limit: Maximum number of objects to return (1-100)
        offset: Number of objects to skip
        sort: Sort order for the results
    """
    request_obj = SearchRequest(
        space_id=space_id, query="", types=types, limit=limit, offset=offset, sort=sort
    )
    return await client.search_objects(request_obj, token=token)


@mcp.tool()
async def delete_object(
    request: DeleteObjectRequest, token: Optional[str] = TOKEN
) -> bool:
    """
    Delete an object from Anytype

    Args:
        request: Delete request containing space_id and object_id
    """
    result = await client.delete_object(request, token=token)
    return result.success


@mcp.tool()
async def search_objects(
    request: SearchRequest, token: Optional[str] = TOKEN
) -> List[ObjectDetails]:
    """
    Search for objects with advanced filtering and sorting

    Args:
        request: Search parameters including query, filters, sorting, etc.
    """
    logger.info("LLM using search objects tool")
    return await client.search_objects(request, token=token)


@mcp.tool()
async def global_search(
    request: GlobalSearchRequest, token: Optional[str] = TOKEN
) -> List[ObjectDetails]:
    """
    Global search across all spaces

    Args:
        request: Global search parameters including query and filters
    """
    logger.info("LLM using global search tool")
    return await client.global_search(request, token=token)


@mcp.tool()
async def export_object(
    space_id: str,
    object_id: str,
    export_format: ExportFormat = ExportFormat.MARKDOWN,
    token: Optional[str] = TOKEN,
) -> str:
    """
    Export an object in the specified format

    Args:
        space_id: ID of the space containing the object
        object_id: ID of the object to export
        export_format: Format to export as (markdown, html, pdf)
    """
    return await client.get_export(space_id, object_id, export_format, token=token)


@mcp.tool()
async def create_space(
    request: CreateSpaceRequest, token: Optional[str] = TOKEN
) -> SpaceDetails:
    """
    Create a new space in Anytype

    Args:
        request: Space creation details including name, icon, description
    """
    return await client.create_space(request, token=token)


@mcp.tool()
async def list_spaces(
    limit: int = 50,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> List[SpaceDetails]:
    """
    Get list of spaces

    Args:
        limit: Maximum number of spaces to return
        offset: Number of spaces to skip
    """
    logger.info("LLM using list spaces tool")
    return await client.get_spaces(limit, offset, token=token)


@mcp.tool()
async def get_space_members(
    request: GetMembersRequest,
    token: Optional[str] = TOKEN,
) -> List[MemberDetails]:
    """
    Get space members

    Args:
        request: Request containing space_id and pagination params
    """
    return await client.get_members(request, token=token)


@mcp.tool()
async def list_types(
    space_id: Optional[str] = None,
    include_system: bool = True,
    token: Optional[str] = TOKEN,
) -> List[TypeDetails]:
    """
    Get object types

    Args:
        space_id: Optional space ID to filter types
        include_system: Whether to include system types
    """
    return await client.get_types(space_id, include_system, token=token)


@mcp.tool()
async def list_templates(
    space_id: Optional[str] = None,
    type_id: Optional[str] = None,
    include_system: bool = True,
    token: Optional[str] = TOKEN,
) -> List[TemplateDetails]:
    """
    Get templates

    Args:
        space_id: Optional space ID to filter templates
        type_id: Optional type ID to filter templates
        include_system: Whether to include system templates
    """
    return await client.get_templates(space_id, type_id, include_system, token=token)


if __name__ == "__main__":
    logger.info("Starting Anytype MCP server...")
    mcp.run(transport="sse")
