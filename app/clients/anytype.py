"""Anytype API client implementation"""

from typing import Any, Dict, List, Optional
from fastapi import Depends

from ..core.config import settings
from ..helpers.api import (
    APIError,
    make_request,
    get_endpoint,
    prepare_request_data,
    validate_response,
)
from ..helpers.schemas import (
    BaseResponse,
    CreateObjectRequest,
    CreateSpaceRequest,
    DeleteObjectRequest,
    DisplayCodeResponse,
    ExportFormat,
    GetMembersRequest,
    GetObjectsRequest,
    GetTemplatesRequest,
    GetTypesRequest,
    GlobalSearchRequest,
    MemberDetails,
    ObjectDetails,
    SearchRequest,
    SpaceDetails,
    TemplateDetails,
    TypeDetails,
)


class AnytypeClient:
    """Anytype API client with improved dependency injection"""

    def __init__(
        self,
        base_url: str = settings.anytype_api_url,
        session_token: str = settings.anytype_session_token,
        app_key: str = settings.anytype_app_key,
    ):
        self.base_url = base_url
        self.session_token = session_token
        self.app_key = app_key
        self.headers = {"Content-Type": "application/json"}
        self.app_name: Optional[str] = None
        self.challenge_id: Optional[str] = None

    async def validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        return token == self.session_token

    async def get_token(self, code: str, challenge_id: Optional[str] = None) -> Dict[str, Any]:
        """Get authentication token from display code"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        if challenge_id is None:
            challenge_id = self.challenge_id
        if not challenge_id:
            raise APIError("No challenge_id available. Call get_auth_display_code first.")

        data = {"token": self.session_token} if self.session_token else None
        result = await make_request(
            "POST",
            get_endpoint("getToken", challenge_id=challenge_id, code=code),
            str(self.base_url),
            data=data,
            headers=headers,
        )
        response = validate_response(result)
        if isinstance(response, dict) and "token" in response and "session_token" in response["token"]:
            self.session_token = response["token"]["session_token"]
        return response

    async def get_auth_display_code(self, app_name: str = "Anytype API") -> DisplayCodeResponse:
        """Get display code for authentication"""
        self.app_name = app_name
        headers = {**self.headers, "X-App-Name": app_name}
        data = {"app_name": app_name}
        if self.session_token:
            data["token"] = self.session_token

        result = await make_request(
            "POST",
            get_endpoint("displayCode", app_name=app_name),
            str(self.base_url),
            data=data,
            headers=headers,
        )
        response = validate_response(result)
        self.challenge_id = response.get("challenge_id")
        return DisplayCodeResponse(code=response.get("code", ""), challenge_id=self.challenge_id)

    async def create_space(self, request: CreateSpaceRequest) -> SpaceDetails:
        """Create a new space"""
        data = prepare_request_data(request.dict())
        data["token"] = self.session_token
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("createSpace"),
            str(self.base_url),
            data,
            headers,
        )
        return SpaceDetails(**validate_response(result))

    async def get_spaces(self, limit: int = 50, offset: int = 0) -> List[SpaceDetails]:
        """Get list of spaces"""
        headers = self._get_headers()
        params = {"limit": limit, "offset": offset, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getSpaces"),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        response = validate_response(result)
        return [SpaceDetails(**space) for space in response]

    async def get_members(self, request: GetMembersRequest) -> List[MemberDetails]:
        """Get space members"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = self._get_headers()
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getMembers", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        return [MemberDetails(**member) for member in validate_response(result)]

    async def create_object(self, request: CreateObjectRequest) -> ObjectDetails:
        """Create a new object"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        data["token"] = self.session_token
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("createObject", space_id=space_id),
            str(self.base_url),
            data,
            headers,
        )
        return ObjectDetails(**validate_response(result))

    async def get_object(self, space_id: str, object_id: str) -> ObjectDetails:
        """Get object details"""
        headers = self._get_headers()
        params = {"token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getObject", space_id=space_id, object_id=object_id),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        return ObjectDetails(**validate_response(result))

    async def get_objects(self, request: GetObjectsRequest) -> List[ObjectDetails]:
        """Get objects list"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = self._get_headers()
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getObjects", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        return [ObjectDetails(**obj) for obj in validate_response(result)]

    async def delete_object(self, request: DeleteObjectRequest) -> BaseResponse:
        """Delete an object"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        object_id = data.pop("object_id")
        headers = self._get_headers()
        params = {"token": self.session_token}
        result = await make_request(
            "DELETE",
            get_endpoint("deleteObject", space_id=space_id, object_id=object_id),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        return BaseResponse(**validate_response(result))

    async def search_objects(self, request: SearchRequest) -> List[ObjectDetails]:
        """Search for objects"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        data["token"] = self.session_token
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("searchObjects", space_id=space_id),
            str(self.base_url),
            data,
            headers,
        )
        return [ObjectDetails(**obj) for obj in validate_response(result)]

    async def global_search(self, request: GlobalSearchRequest) -> List[ObjectDetails]:
        """Global search across all spaces"""
        data = prepare_request_data(request.dict())
        data["token"] = self.session_token
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("globalSearch"),
            str(self.base_url),
            data,
            headers,
        )
        return [ObjectDetails(**obj) for obj in validate_response(result)]

    async def get_types(self, request: GetTypesRequest) -> List[TypeDetails]:
        """Get object types"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = self._get_headers()
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getTypes", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        return [TypeDetails(**type_) for type_ in validate_response(result)]

    async def get_templates(self, request: GetTemplatesRequest) -> List[TemplateDetails]:
        """Get templates"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        type_id = data.pop("type_id")
        headers = self._get_headers()
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getTemplates", space_id=space_id, type_id=type_id),
            str(self.base_url),
            params=params,
            headers=headers,
        )
        return [TemplateDetails(**template) for template in validate_response(result)]

    async def get_export(self, space_id: str, object_id: str, format: ExportFormat) -> str:
        """Export an object in specified format"""
        headers = self._get_headers()
        data = {"token": self.session_token}
        result = await make_request(
            "POST",
            get_endpoint("getExport", space_id=space_id, object_id=object_id, format=format),
            str(self.base_url),
            data=data,
            headers=headers,
        )
        return validate_response(result).get("content", "")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional app name"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        return headers


# FastAPI dependency
async def get_anytype_client() -> AnytypeClient:
    """Dependency for getting AnytypeClient instance"""
    return AnytypeClient()
