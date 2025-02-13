"""Data validation schemas and type definitions"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ViewType(str, Enum):
    """Object view types"""

    NOTE = "note"
    TASK = "task"
    SET = "set"
    BOOKMARK = "bookmark"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"
    CANVAS = "canvas"


class ExportFormat(str, Enum):
    """Export format options"""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class SortOrder(str, Enum):
    """Sort order options"""

    CREATED_DATE = "created_date"
    LAST_MODIFIED_DATE = "last_modified_date"
    LAST_OPENED_DATE = "last_opened_date"
    NAME = "name"
    TYPE = "type"


class MemberRole(str, Enum):
    """Member role options"""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class BaseResponse(BaseModel):
    """Base response model"""

    success: bool = True
    error: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""

    limit: Optional[int] = Field(default=50, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)


class ObjectDetails(BaseModel):
    """Object details model"""

    id: str
    space_id: str
    type: str
    name: str
    layout: Optional[ViewType] = None
    snippet: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    done: Optional[bool] = None
    archived: Optional[bool] = None
    favorite: Optional[bool] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    last_opened_date: Optional[datetime] = None
    source_link: Optional[str] = None
    source: Optional[str] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    tags: Optional[List[str]] = None
    relations: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class TypeDetails(BaseModel):
    """Type details model"""

    id: str
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    is_system: bool = False
    fields: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class TemplateDetails(BaseModel):
    """Template details model"""

    id: str
    name: str
    type: str
    icon: Optional[str] = None
    description: Optional[str] = None
    snippet: Optional[str] = None
    is_system: bool = False

    class Config:
        use_enum_values = True


class MemberDetails(BaseModel):
    """Member details model"""

    id: str
    name: str
    role: MemberRole
    icon: Optional[str] = None
    email: Optional[str] = None
    joined_date: Optional[datetime] = None

    class Config:
        use_enum_values = True


class CreateObjectRequest(BaseModel):
    """Create object request model"""

    space_id: str
    type: str
    name: str
    layout: Optional[ViewType] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    done: Optional[bool] = None
    archived: Optional[bool] = None
    favorite: Optional[bool] = None
    source_link: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    relations: Optional[Dict[str, Any]] = None
    is_draft: Optional[bool] = None

    class Config:
        use_enum_values = True


class DeleteObjectRequest(BaseModel):
    """Delete object request model"""

    space_id: str
    object_id: str


class SearchRequest(BaseModel):
    """Search request model"""

    query: str
    space_id: Optional[str] = None
    types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    limit: Optional[int] = Field(default=50, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)
    sort: Optional[SortOrder] = Field(default=SortOrder.LAST_MODIFIED_DATE)
    include_archived: Optional[bool] = False
    include_favorites: Optional[bool] = None

    class Config:
        use_enum_values = True


class GlobalSearchRequest(BaseModel):
    """Global search request model"""

    query: str
    types: Optional[List[str]] = None
    limit: Optional[int] = Field(default=50, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)
    sort: Optional[SortOrder] = Field(default=SortOrder.LAST_MODIFIED_DATE)

    class Config:
        use_enum_values = True


class CreateSpaceRequest(BaseModel):
    """Create space request model"""

    name: str
    icon: Optional[str] = None
    description: Optional[str] = None


class SpaceDetails(BaseModel):
    """Space details model"""

    id: str
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    member_count: Optional[int] = None
    object_count: Optional[int] = None
    is_personal: bool = False

    class Config:
        use_enum_values = True


class ExportRequest(BaseModel):
    """Export request model"""

    space_id: str
    object_id: str
    format: ExportFormat = ExportFormat.MARKDOWN

    class Config:
        use_enum_values = True


class DisplayCodeResponse(BaseModel):
    """Display code response model"""

    code: str
    challenge_id: str


class TokenValidationRequest(BaseModel):
    """Token validation request model"""

    token: str


class GetObjectsRequest(BaseModel):
    """Get objects request model"""

    space_id: str
    types: Optional[List[str]] = None
    limit: Optional[int] = Field(default=50, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)
    sort: Optional[SortOrder] = Field(default=SortOrder.LAST_MODIFIED_DATE)

    class Config:
        use_enum_values = True


class GetMembersRequest(BaseModel):
    """Get members request model"""

    space_id: str
    limit: Optional[int] = Field(default=50, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)

    class Config:
        use_enum_values = True


class GetTypesRequest(BaseModel):
    """Get types request model"""

    space_id: Optional[str] = None
    include_system: Optional[bool] = True

    class Config:
        use_enum_values = True


class GetTemplatesRequest(BaseModel):
    """Get templates request model"""

    space_id: Optional[str] = None
    type_id: Optional[str] = None
    include_system: Optional[bool] = True

    class Config:
        use_enum_values = True
