"""API client implementation"""

import logging
from typing import Optional

from fastapi import Depends

from app.core.auth import get_validated_token
from app.core.config import settings
from app.helpers.api import APIError, make_request, prepare_request_data
from app.helpers.constants import API_ENDPOINTS
from app.helpers.schemas import (
    CreateObjectRequest,
    CreateSpaceRequest,
    CreateSpaceResponse,
    DisplayCodeResponse,
    ExportFormat,
    Member,
    Object,
    ObjectExportResponse,
    ObjectResponse,
    PaginatedResponse,
    SearchRequest,
    Space,
    Template,
    TemplateResponse,
    TokenResponse,
    Type,
    TypeResponse,
)

logger = logging.getLogger(__name__)


class APIClient:
    """API client"""

    def __init__(
        self,
        base_url: str = str(settings.api_url),
        token: Optional[str] = None,
        app_key: Optional[str] = None,
    ):
        self.base_url = base_url
        self.token = token
        self.app_key = app_key
        self.headers = {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        }

    def _get_endpoint(self, category: str, name: str, **kwargs: str) -> str:
        """Get API endpoint with parameter substitution"""
        from app.helpers.constants import BASE_PATH

        endpoint = API_ENDPOINTS[category][name]
        return f"{BASE_PATH}{endpoint.format(**kwargs)}"

    async def get_display_code(self, app_name: str) -> DisplayCodeResponse:
        """Start new challenge"""
        endpoint = self._get_endpoint("auth", "display_code")
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            params={"app_name": app_name},
            headers=self.headers,
        )
        return DisplayCodeResponse(**result)

    async def get_token(self, challenge_id: str, code: str) -> TokenResponse:
        """Retrieve token"""
        endpoint = self._get_endpoint("auth", "token")
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            params={"challenge_id": challenge_id, "code": code},
            headers=self.headers,
        )
        return TokenResponse(**result)

    async def validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        try:
            # Create a temporary client with the token to validate
            temp_client = APIClient(base_url=self.base_url, token=token)
            # Try to list spaces to validate the token
            await temp_client.list_spaces(limit=1)
            return True
        except APIError:
            return False

    async def list_spaces(
        self, limit: int = 100, offset: int = 0
    ) -> PaginatedResponse[Space]:
        """List all spaces"""
        endpoint = self._get_endpoint("spaces", "list")
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Space](**result)

    async def create_space(self, request: CreateSpaceRequest) -> CreateSpaceResponse:
        """Create a new space"""
        endpoint = self._get_endpoint("spaces", "create")
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            data=request.model_dump(),
            headers=self.headers,
        )
        return CreateSpaceResponse(**result)

    async def list_members(
        self, space_id: str, limit: int = 100, offset: int = 0
    ) -> PaginatedResponse[Member]:
        """List space members"""
        endpoint = self._get_endpoint("spaces", "members", space_id=space_id)
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Member](**result)

    async def list_objects(
        self, space_id: str, limit: int = 100, offset: int = 0
    ) -> PaginatedResponse[Object]:
        """List objects within a space"""
        endpoint = self._get_endpoint("objects", "list", space_id=space_id)
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Object](**result)

    async def create_object(
        self, space_id: str, request: CreateObjectRequest
    ) -> ObjectResponse:
        """Create a new object in a space"""
        endpoint = self._get_endpoint("objects", "create", space_id=space_id)
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            data=request.model_dump(),
            headers=self.headers,
        )
        return ObjectResponse(**result)

    async def get_object(self, space_id: str, object_id: str) -> ObjectResponse:
        """Get object details"""
        endpoint = self._get_endpoint(
            "objects", "get", space_id=space_id, object_id=object_id
        )
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            headers=self.headers,
        )
        return ObjectResponse(**result)

    async def delete_object(self, space_id: str, object_id: str) -> ObjectResponse:
        """Delete an object"""
        endpoint = self._get_endpoint(
            "objects", "delete", space_id=space_id, object_id=object_id
        )
        result = await make_request(
            "DELETE",
            endpoint,
            self.base_url,
            headers=self.headers,
        )
        return ObjectResponse(**result)

    async def search_objects(
        self,
        space_id: str,
        request: SearchRequest,
        limit: int = 100,
        offset: int = 0,
    ) -> PaginatedResponse[Object]:
        """Search for objects within a space"""
        endpoint = self._get_endpoint("search", "space", space_id=space_id)
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            data=request.model_dump(),
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Object](**result)

    async def global_search(
        self, request: SearchRequest, limit: int = 100, offset: int = 0
    ) -> PaginatedResponse[Object]:
        """Search for objects across all spaces"""
        endpoint = self._get_endpoint("search", "global")
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            data=request.model_dump(),
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Object](**result)

    async def list_types(
        self, space_id: str, limit: int = 100, offset: int = 0
    ) -> PaginatedResponse[Type]:
        """List types in a space"""
        endpoint = self._get_endpoint("types", "list", space_id=space_id)
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Type](**result)

    async def get_type(self, space_id: str, type_id: str) -> TypeResponse:
        """Get type details"""
        endpoint = self._get_endpoint(
            "types", "get", space_id=space_id, type_id=type_id
        )
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            headers=self.headers,
        )
        return TypeResponse(**result)

    async def list_templates(
        self,
        space_id: str,
        type_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> PaginatedResponse[Template]:
        """List templates for a type"""
        endpoint = self._get_endpoint(
            "types", "templates", space_id=space_id, type_id=type_id
        )
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            params={"limit": limit, "offset": offset},
            headers=self.headers,
        )
        return PaginatedResponse[Template](**result)

    async def get_template(
        self, space_id: str, type_id: str, template_id: str
    ) -> TemplateResponse:
        """Get template details"""
        endpoint = self._get_endpoint(
            "types",
            "template",
            space_id=space_id,
            type_id=type_id,
            template_id=template_id,
        )
        result = await make_request(
            "GET",
            endpoint,
            self.base_url,
            headers=self.headers,
        )
        return TemplateResponse(**result)

    async def export_object(
        self, space_id: str, object_id: str, format: ExportFormat
    ) -> ObjectExportResponse:
        """Export an object in the specified format"""
        endpoint = self._get_endpoint(
            "objects",
            "export",
            space_id=space_id,
            object_id=object_id,
            format=format.value,
        )
        result = await make_request(
            "POST",
            endpoint,
            self.base_url,
            headers=self.headers,
        )
        return ObjectExportResponse(**result)


def get_api_client(token: str = Depends(get_validated_token)) -> APIClient:
    """FastAPI dependency for getting APIClient instance"""
    return APIClient(base_url=str(settings.api_url), token=token)
