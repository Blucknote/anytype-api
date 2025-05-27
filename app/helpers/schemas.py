"""Data validation schemas and type definitions"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class IconFormat(str, Enum):
    """The type of the icon"""

    EMOJI = "emoji"
    FILE = "file"
    ICON = "icon"
    EMPTY = ""  # Allow empty string


class Icon(BaseModel):
    """The icon of the object"""

    color: Optional[str] = None
    emoji: Optional[str] = None
    file: Optional[str] = None
    format: Optional[IconFormat] = Field(default=None)
    name: Optional[str] = None


class PaginationMeta(BaseModel):
    """The pagination metadata for the response"""

    has_more: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    total: Optional[int] = None


class PaginatedResponse(BaseModel):
    """Base paginated response model"""

    data: List[Any]
    pagination: Optional[PaginationMeta] = None


class ChallengeResponse(BaseModel):
    """Challenge ID"""

    challenge_id: str


class TokenResponse(BaseModel):
    """Authentication token"""

    api_key: str


class ExportFormat(str, Enum):
    """Export format options"""

    MARKDOWN = "markdown"


class ObjectExportResponse(BaseModel):
    """Object exported successfully"""

    markdown: str


class Filter(BaseModel):
    """The filter condition"""

    condition: str
    format: str
    id: str
    property_key: str
    value: str


class Sort(BaseModel):
    """The sort direction"""

    format: str
    id: str
    property_key: str
    sort_type: str


class View(BaseModel):
    """The view properties"""

    filters: Optional[List[Filter]] = None
    id: str
    layout: str
    name: str
    sorts: Optional[List[Sort]] = None


class File(BaseModel):
    """The file of the block, if applicable"""

    added_at: Optional[int] = None
    hash: Optional[str] = None
    mime: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    state: Optional[str] = None
    style: Optional[str] = None
    target_object_id: Optional[str] = None
    type: Optional[str] = None


class Property(BaseModel):
    """The property block, if applicable"""

    checkbox: Optional[bool] = None
    date: Optional[str] = None
    email: Optional[str] = None
    file: Optional[List[str]] = None
    format: str
    id: str
    multi_select: Optional[List[Any]] = None  # TODO: Define Tag schema
    name: str
    number: Optional[float] = None
    object: Optional[List[str]] = None
    phone: Optional[str] = None
    select: Optional[Any] = None  # TODO: Define Tag schema
    text: Optional[str] = None
    url: Optional[str] = None


class Text(BaseModel):
    """The text of the block, if applicable"""

    checked: Optional[bool] = None
    color: Optional[str] = None
    icon: Optional[Icon] = None
    style: Optional[str] = None
    text: Optional[str] = None


class Block(BaseModel):
    """The block properties"""

    align: Optional[str] = None
    background_color: Optional[str] = None
    children_ids: Optional[List[str]] = None
    file: Optional[File] = None
    id: str
    property: Optional[Property] = None
    text: Optional[Text] = None
    vertical_align: Optional[str] = None


class Type(BaseModel):
    """The type of the object"""

    archived: Optional[bool] = None
    icon: Optional[Icon] = None
    id: str
    key: str
    name: str
    object: Optional[str] = None
    recommended_layout: Optional[str] = None


class Object(BaseModel):
    """The object properties"""

    archived: Optional[bool] = None
    blocks: Optional[List[Block]] = None
    icon: Optional[Icon] = None
    id: str
    layout: Optional[str] = None
    name: Optional[str] = None
    object: Optional[str] = None
    properties: Optional[List[Property]] = None
    snippet: Optional[str] = None
    space_id: Optional[str] = None
    type: Optional[Type] = None


class ObjectResponse(BaseModel):
    """The requested object"""

    object: Object


class SearchRequest(BaseModel):
    """Search parameters"""

    query: str
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
    sort: Optional[Dict[str, Any]] = None  # TODO: Define SortOptions schema
    types: Optional[List[str]] = None


class SortDirection(str, Enum):
    """The direction to sort the search results"""

    ASC = "asc"
    DESC = "desc"


class SortProperty(str, Enum):
    """The property to sort the search results by"""

    CREATED_DATE = "created_date"
    LAST_MODIFIED_DATE = "last_modified_date"
    LAST_OPENED_DATE = "last_opened_date"
    NAME = "name"


class SortOptions(BaseModel):
    """The sorting criteria and direction for the search results"""

    direction: Optional[SortDirection] = SortDirection.DESC
    property: Optional[SortProperty] = SortProperty.LAST_MODIFIED_DATE


class CreateSpaceRequest(BaseModel):
    """Space to create"""

    description: Optional[str] = None
    name: str


class Space(BaseModel):
    """The space properties"""

    description: Optional[str] = None
    gateway_url: Optional[str] = None
    icon: Optional[Icon] = None
    id: str
    name: str
    network_id: Optional[str] = None
    object: Optional[str] = None


class SpaceResponse(BaseModel):
    """Space created successfully"""

    space: Space


class Member(BaseModel):
    """The member properties"""

    global_name: Optional[str] = None
    icon: Optional[Icon] = None
    id: str
    identity: Optional[str] = None
    name: str
    object: Optional[str] = None
    role: Optional[str] = None  # TODO: Define MemberRole enum
    status: Optional[str] = None  # TODO: Define MemberStatus enum


class MemberResponse(BaseModel):
    """Member"""

    member: Member


class Template(BaseModel):
    """The template properties"""

    archived: Optional[bool] = None
    icon: Optional[Icon] = None
    id: str
    name: str
    object: Optional[str] = None
    type: Optional[str] = None


class TemplateResponse(BaseModel):
    """The requested template"""

    template: Template


class TypeResponse(BaseModel):
    """The requested type"""

    type: Type


class CreateObjectRequest(BaseModel):
    """The object to create"""

    body: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[Icon] = None
    name: str
    source: Optional[str] = None
    template_id: Optional[str] = None
    type_key: str


class PaginatedObjectResponse(PaginatedResponse):
    data: List[Object]


class PaginatedSpaceResponse(PaginatedResponse):
    data: List[Space]


class PaginatedMemberResponse(PaginatedResponse):
    data: List[Member]


class PaginatedTypeResponse(PaginatedResponse):
    data: List[Type]


class PaginatedTemplateResponse(PaginatedResponse):
    data: List[Template]


class PaginatedViewResponse(PaginatedResponse):
    data: List[View]


# Error Schemas
class ErrorDetail(BaseModel):
    message: str


class ForbiddenError(BaseModel):
    error: ErrorDetail


class GoneError(BaseModel):
    error: ErrorDetail


class NotFoundError(BaseModel):
    error: ErrorDetail


class RateLimitError(BaseModel):
    error: ErrorDetail


class ServerError(BaseModel):
    error: ErrorDetail


class UnauthorizedError(BaseModel):
    error: ErrorDetail


class ValidationError(BaseModel):
    error: ErrorDetail
