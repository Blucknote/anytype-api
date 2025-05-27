"""Anytype API client implementation"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.helpers.api import (
    APIError,
    get_endpoint,
    make_request,
    prepare_request_data,
    validate_response,
)
from app.helpers.schemas import (
    ChallengeResponse,
    CreateObjectRequest,
    CreateSpaceRequest,
    ExportFormat,
    MemberResponse,
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
    SpaceResponse,
    TemplateResponse,
    TokenResponse,
    TypeResponse,
    View,
)

logger = logging.getLogger(__name__)


class AnytypeClient:
    """Anytype API client with improved dependency injection"""

    def __init__(
        self,
        base_url: str = str(settings.anytype_api_url),
        api_key: str = settings.anytype_api_key,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        self.app_name: Optional[str] = None
        self.challenge_id: Optional[str] = None

    async def validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        try:
            # Make a test request to validate the token using search
            # We use an empty search request which is a safe way to validate the token
            await make_request(
                "POST",
                get_endpoint(
                    "searchObjects",
                    space_id="bafyreifpajdyu6t4v3ju236wdwdq32nenfg3lbbqnkszk5uudvfc2zhofa.1o744mt1sh744",
                ),
                str(self.base_url),
                headers=self._get_headers(),
                data={"query": "", "types": [], "sort": SortOptions().dict()},
                token=token,
            )
            return True
        except APIError as e:
            if e.status_code == 401:
                return False
            raise

    async def create_challenge(
        self, app_name: str = "Anytype API"
    ) -> ChallengeResponse:
        """Create authentication challenge (step 1 of new auth flow)"""
        self.app_name = app_name
        headers = {**self.headers}
        data = {"app_name": app_name}
        result = await make_request(
            "POST",
            get_endpoint("createChallenge"),
            str(self.base_url),
            data=data,
            headers=headers,
        )
        # The API returns a ChallengeResponse structure directly
        return ChallengeResponse(**result)

    async def create_api_key(self, code: str, challenge_id: str) -> TokenResponse:
        """Create API key using challenge_id and code (step 2 of new auth flow)"""
        headers = {**self.headers}
        data = {"challenge_id": challenge_id, "code": code}
        result = await make_request(
            "POST",
            get_endpoint("createApiKey"),
            str(self.base_url),
            data=data,
            headers=headers,
        )
        # The API returns a TokenResponse structure directly
        return TokenResponse(**result)

    async def create_space(
        self, request: CreateSpaceRequest, token: Optional[str] = None
    ) -> SpaceResponse:
        """Create a new space"""
        data = prepare_request_data(request.dict())
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("createSpace"),
            str(self.base_url),
            data=data,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a SpaceResponse structure directly
        return SpaceResponse(**result)

    async def get_spaces(
        self, limit: int = 50, offset: int = 0, token: Optional[str] = None
    ) -> PaginatedSpaceResponse:
        """Get list of spaces"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint("getSpaces"),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedSpaceResponse(**result)

    async def get_space(
        self, space_id: str, token: Optional[str] = None
    ) -> SpaceResponse:
        """Get space details"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint("getSpace", space_id=space_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a SpaceResponse structure directly
        return SpaceResponse(**result)

    async def get_members(
        self,
        space_id: str,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedMemberResponse:
        """Get space members"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint("getMembers", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedMemberResponse(**result)

    async def get_member(
        self, space_id: str, member_id: str, token: Optional[str] = None
    ) -> MemberResponse:
        """Get space member details"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint("getMember", space_id=space_id, member_id=member_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a MemberResponse structure directly
        return MemberResponse(**result)

    async def create_object(
        self, space_id: str, request: CreateObjectRequest, token: Optional[str] = None
    ) -> ObjectResponse:
        """Create a new object"""
        data = prepare_request_data(request.dict())
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("createObject", space_id=space_id),
            str(self.base_url),
            data=data,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns an ObjectResponse structure directly
        return ObjectResponse(**result)

    async def get_object(
        self, space_id: str, object_id: str, token: Optional[str] = None
    ) -> ObjectResponse:
        """Get object details"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint("getObject", space_id=space_id, object_id=object_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns an ObjectResponse structure directly
        return ObjectResponse(**result)

    async def get_objects_in_list(
        self,
        space_id: str,
        list_id: str,
        view_id: str,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedObjectResponse:
        """Get objects in a list"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint(
                "getObjectsInList", space_id=space_id, list_id=list_id, view_id=view_id
            ),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedObjectResponse(**result)

    async def add_objects_to_list(
        self,
        space_id: str,
        list_id: str,
        object_ids: List[str],
        token: Optional[str] = None,
    ) -> str:
        """Add objects to a list"""
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("addObjectsToList", space_id=space_id, list_id=list_id),
            str(self.base_url),
            data=object_ids,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a string response directly
        return result

    async def remove_object_from_list(
        self, space_id: str, list_id: str, object_id: str, token: Optional[str] = None
    ) -> str:
        """Remove object from a list"""
        headers = self._get_headers()
        result = await make_request(
            "DELETE",
            get_endpoint(
                "removeObjectFromList",
                space_id=space_id,
                list_id=list_id,
                object_id=object_id,
            ),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a string response directly
        return result

    async def get_list_views(
        self,
        space_id: str,
        list_id: str,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedViewResponse:
        """Get list views"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint("getListView", space_id=space_id, list_id=list_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedViewResponse(**result)

    async def get_objects(
        self,
        space_id: str,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedObjectResponse:
        """Get objects list"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint("getObjects", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedObjectResponse(**result)

    async def delete_object(
        self, space_id: str, object_id: str, token: Optional[str] = None
    ) -> ObjectResponse:
        """Delete an object"""
        headers = self._get_headers()
        result = await make_request(
            "DELETE",
            get_endpoint("deleteObject", space_id=space_id, object_id=object_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns an ObjectResponse structure directly
        return ObjectResponse(**result)

    async def search_objects(
        self,
        space_id: str,
        request: SearchRequest,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedObjectResponse:
        """Search for objects within a space"""
        data = prepare_request_data(request.dict())
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "POST",
            get_endpoint("searchObjects", space_id=space_id),
            str(self.base_url),
            data=data,
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedObjectResponse(**result)

    async def global_search(
        self, request: SearchRequest, token: Optional[str] = None
    ) -> PaginatedObjectResponse:
        """Global search across all spaces"""
        data = prepare_request_data(request.dict())
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("globalSearch"),
            str(self.base_url),
            data=data,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedObjectResponse(**result)

    async def get_types(
        self,
        space_id: str,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedTypeResponse:
        """Get object types"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint("getTypes", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedTypeResponse(**result)

    async def get_type(
        self, space_id: str, type_id: str, token: Optional[str] = None
    ) -> TypeResponse:
        """Get object type details"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint("getType", space_id=space_id, type_id=type_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a TypeResponse structure directly
        return TypeResponse(**result)

    async def get_templates(
        self,
        space_id: str,
        type_id: str,
        limit: int = 50,
        offset: int = 0,
        token: Optional[str] = None,
    ) -> PaginatedTemplateResponse:
        """Get templates"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset}
        result = await make_request(
            "GET",
            get_endpoint("getTemplates", space_id=space_id, type_id=type_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a PaginatedResponse structure directly
        return PaginatedTemplateResponse(**result)

    async def get_template(
        self, space_id: str, type_id: str, template_id: str, token: Optional[str] = None
    ) -> TemplateResponse:
        """Get template details"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint(
                "getTemplate",
                space_id=space_id,
                type_id=type_id,
                template_id=template_id,
            ),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns a TemplateResponse structure directly
        return TemplateResponse(**result)

    async def get_export(
        self,
        space_id: str,
        object_id: str,
        format: ExportFormat,
        token: Optional[str] = None,
    ) -> ObjectExportResponse:
        """Export an object in specified format"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint(
                "getExport",
                space_id=space_id,
                object_id=object_id,
                format=str(format.value),
            ),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        # The API returns an ObjectExportResponse structure directly
        return ObjectExportResponse(**result)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional app name"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        return headers

    def _get_token(self, token: Optional[str] = None) -> str:
        """Get the token to use for requests"""
        return token or self.api_key


# FastAPI dependency
def get_anytype_client() -> AnytypeClient:
    """Dependency for getting AnytypeClient instance"""
    return AnytypeClient()
