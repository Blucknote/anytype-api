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
    ExportFormat,
    Member,
    MemberResponse,
    Object,
    ObjectExportResponse,
    ObjectResponse,
    PaginatedMemberResponse,
    PaginatedObjectResponse,
    PaginatedSpaceResponse,
    PaginatedTemplateResponse,
    PaginatedTypeResponse,
    PaginatedViewResponse,
    SearchRequest,
    SortOptions,
    Space,
    SpaceResponse,
    Template,
    TemplateResponse,
    Type,
    TypeResponse,
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
    request: CreateObjectRequest,
    token: Optional[str] = TOKEN,
) -> ObjectResponse:
    """
    Create a new object in Anytype.

    Args:
        space_id: ID of the space to create the object in (required).
        request: The object creation request body (CreateObjectRequest).
        token: Optional authentication token.

    Returns:
        The created object details (ObjectResponse).
    """
    return await client.create_object(space_id, request, token=token)


@mcp.tool()
async def get_object(
    space_id: str, object_id: str, token: Optional[str] = TOKEN
) -> ObjectResponse:
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
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedObjectResponse:
    """
    Get objects list

    Args:
        space_id: ID of the space to list objects from
        limit: Maximum number of objects to return (1-1000)
        offset: Number of objects to skip
    """
    logger.info("LLM using list objects tool")
    return await client.get_objects(space_id, limit, offset, token=token)


@mcp.tool()
async def delete_object(
    space_id: str, object_id: str, token: Optional[str] = TOKEN
) -> ObjectResponse:
    """
    Delete an object from Anytype

    Args:
        space_id: ID of the space containing the object
        object_id: ID of the object to delete
    """
    return await client.delete_object(space_id, object_id, token=token)


@mcp.tool()
async def search_objects(
    space_id: str, request: SearchRequest, token: Optional[str] = TOKEN
) -> PaginatedObjectResponse:
    """
    Search for objects within a space with advanced filtering and sorting

    Args:
        space_id: ID of the space to search within.
        request: Search parameters including query, filters, sorting, etc.
    """
    return await client.search_objects(space_id, request, token=token)


@mcp.tool()
async def global_search(
    request: SearchRequest, token: Optional[str] = TOKEN
) -> PaginatedObjectResponse:
    """
    Global search across all spaces

    Args:
        request: Global search parameters including query and filters
    """
    return await client.global_search(request, token=token)


@mcp.tool()
async def export_object(
    space_id: str,
    object_id: str,
    format: ExportFormat = ExportFormat.MARKDOWN,
    token: Optional[str] = TOKEN,
) -> ObjectExportResponse:
    """
    Export an object in the specified format

    Args:
        space_id: ID of the space containing the object
        object_id: ID of the object to export
        format: Format to export as (markdown)
    """
    return await client.get_export(space_id, object_id, format, token=token)


@mcp.tool()
async def create_space(
    request: CreateSpaceRequest, token: Optional[str] = TOKEN
) -> SpaceResponse:
    """
    Create a new space in Anytype

    Args:
        request: Space creation details including name, icon, description
    """
    return await client.create_space(request, token=token)


@mcp.tool()
async def list_spaces(
    limit: int = 100,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedSpaceResponse:
    """
    Get list of spaces

    Args:
        limit: Maximum number of spaces to return (1-1000)
        offset: Number of spaces to skip
    """
    return await client.get_spaces(limit, offset, token=token)


@mcp.tool()
async def list_members(
    space_id: str,
    limit: int = 100,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedMemberResponse:
    """
    Get space members

    Args:
        space_id: ID of the space to list members from.
        limit: Maximum number of members to return (1-1000)
        offset: Number of members to skip
    """
    return await client.get_members(space_id, limit, offset, token=token)


@mcp.tool()
async def get_member(
    space_id: str, member_id: str, token: Optional[str] = TOKEN
) -> MemberResponse:
    """
    Get space member details

    Args:
        space_id: ID of the space containing the member.
        member_id: ID or Identity of the member to retrieve.
    """
    return await client.get_member(space_id, member_id, token=token)


@mcp.tool()
async def list_types(
    space_id: str,
    limit: int = 100,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedTypeResponse:
    """
    Get object types

    Args:
        space_id: ID of the space to list types from.
        limit: Maximum number of types to return (1-1000)
        offset: Number of types to skip
    """
    return await client.get_types(space_id, limit, offset, token=token)


@mcp.tool()
async def get_type(
    space_id: str, type_id: str, token: Optional[str] = TOKEN
) -> TypeResponse:
    """
    Get object type details

    Args:
        space_id: ID of the space containing the type.
        type_id: ID of the type to retrieve.
    """
    return await client.get_type(space_id, type_id, token=token)


@mcp.tool()
async def list_templates(
    space_id: str,
    type_id: str,
    limit: int = 100,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedTemplateResponse:
    """
    Get templates

    Args:
        space_id: ID of the space containing the type.
        type_id: ID of the type to list templates for.
        limit: Maximum number of templates to return (1-1000)
        offset: Number of templates to skip
    """
    return await client.get_templates(space_id, type_id, limit, offset, token=token)


@mcp.tool()
async def get_template(
    space_id: str, type_id: str, template_id: str, token: Optional[str] = TOKEN
) -> TemplateResponse:
    """
    Get template details

    Args:
        space_id: ID of the space containing the type.
        type_id: ID of the type containing the template.
        template_id: ID of the template to retrieve.
    """
    return await client.get_template(space_id, type_id, template_id, token=token)


@mcp.tool()
async def get_objects_in_list(
    space_id: str,
    list_id: str,
    view_id: str,
    limit: int = 100,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedObjectResponse:
    """
    Get objects in a list

    Args:
        space_id: ID of the space containing the list.
        list_id: ID of the list (query or collection).
        view_id: ID of the view to filter and sort by.
        limit: Maximum number of objects to return (1-1000)
        offset: Number of objects to skip
    """
    return await client.get_objects_in_list(
        space_id, list_id, view_id, limit, offset, token=token
    )


@mcp.tool()
async def add_objects_to_list(
    space_id: str, list_id: str, object_ids: List[str], token: Optional[str] = TOKEN
) -> str:
    """
    Add objects to a list (collection only)

    Args:
        space_id: ID of the space containing the list.
        list_id: ID of the list (collection only).
        object_ids: List of object IDs to add.
    """
    return await client.add_objects_to_list(space_id, list_id, object_ids, token=token)


@mcp.tool()
async def remove_object_from_list(
    space_id: str, list_id: str, object_id: str, token: Optional[str] = TOKEN
) -> str:
    """
    Remove object from a list (collection only)

    Args:
        space_id: ID of the space containing the list.
        list_id: ID of the list (collection only).
        object_id: ID of the object to remove.
    """
    return await client.remove_object_from_list(
        space_id, list_id, object_id, token=token
    )


@mcp.tool()
async def get_list_views(
    space_id: str,
    list_id: str,
    limit: int = 100,
    offset: int = 0,
    token: Optional[str] = TOKEN,
) -> PaginatedViewResponse:
    """
    Get list views

    Args:
        space_id: ID of the space containing the list.
        list_id: ID of the list (query or collection).
        limit: Maximum number of views to return (1-1000)
        offset: Number of views to skip
    """
    return await client.get_list_views(space_id, list_id, limit, offset, token=token)


if __name__ == "__main__":
    logger.info("Starting Anytype MCP server...")
    mcp.run(transport="sse")
