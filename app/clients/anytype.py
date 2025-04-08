"""Anytype API client implementation"""

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.helpers.api import (
    APIError,
    get_endpoint,
    make_request,
    prepare_request_data,
    validate_response,
)
from app.helpers.schemas import (
    BaseResponse,
    Block,
    CreateObjectRequest,
    CreateSpaceRequest,
    DeleteObjectRequest,
    DisplayCodeResponse,
    ExportFormat,
    GetMembersRequest,
    GetObjectsRequest,
    GlobalSearchRequest,
    MemberDetails,
    ObjectDetails,
    SearchRequest,
    SortOptions,
    SpaceDetails,
    TemplateDetails,
    TypeDetails,
)

logger = logging.getLogger(__name__)


class AnytypeClient:
    """Anytype API client with improved dependency injection"""

    def __init__(
        self,
        base_url: str = str(settings.anytype_api_url),
        session_token: str = settings.anytype_session_token,
        app_key: str = settings.anytype_app_key,
        bearer_token: Optional[str] = None,
    ):
        self.base_url = base_url
        self.session_token = session_token
        self.app_key = app_key
        self.bearer_token = bearer_token
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

    async def get_token(
        self, code: str, challenge_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get authentication token from display code"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        if challenge_id is None:
            challenge_id = self.challenge_id
        if not challenge_id:
            raise APIError(
                "No challenge_id available. Call get_auth_display_code first."
            )

        data = {"token": self.session_token} if self.session_token else None
        result = await make_request(
            "POST",
            get_endpoint("getToken", challenge_id=challenge_id, code=code),
            str(self.base_url),
            data=data,
            headers=headers,
        )
        responses = validate_response(result)
        if len(responses) > 0:
            response = responses[0]
            if "token" in response and isinstance(response["token"], dict):
                self.session_token = response["token"].get("session_token", "")
            return response
        return {}

    async def get_auth_display_code(
        self, app_name: str = "Anytype API"
    ) -> DisplayCodeResponse:
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
        responses = validate_response(result)
        if len(responses) > 0:
            response = responses[0]
            self.challenge_id = response.get("challenge_id", "")
            return DisplayCodeResponse(
                code=response.get("code", ""), challenge_id=self.challenge_id or ""
            )
        return DisplayCodeResponse(code="", challenge_id="")

    async def create_space(
        self, request: CreateSpaceRequest, token: Optional[str] = None
    ) -> SpaceDetails:
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
        responses = validate_response(result)
        return SpaceDetails(**(responses[0] if responses else {}))

    async def get_spaces(
        self, limit: int = 50, offset: int = 0, token: Optional[str] = None
    ) -> List[SpaceDetails]:
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
        responses = validate_response(result)
        return [SpaceDetails(**space) for space in responses]

    async def get_members(
        self, request: GetMembersRequest, token: Optional[str] = None
    ) -> List[MemberDetails]:
        """Get space members"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint("getMembers", space_id=space_id),
            str(self.base_url),
            params=data,
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        return [MemberDetails(**member) for member in responses]

    async def create_object(
        self, request: CreateObjectRequest, token: Optional[str] = None
    ) -> ObjectDetails:
        """Create a new object"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("createObject", space_id=space_id),
            str(self.base_url),
            data=data,
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        if responses and isinstance(responses[0], dict):
            obj = responses[0]
            # Extract nested 'object' if present
            if "object" in obj and isinstance(obj["object"], dict):
                obj = obj["object"]
            obj.pop("blocks", None)
            obj.pop("details", None)
            return ObjectDetails(**obj)
        return ObjectDetails()

    async def get_object(
        self, space_id: str, object_id: str, token: Optional[str] = None
    ) -> ObjectDetails:
        """Get object details"""
        headers = self._get_headers()
        result = await make_request(
            "GET",
            get_endpoint("getObject", space_id=space_id, object_id=object_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        if responses and isinstance(responses[0], dict):
            obj = responses[0]
            if "object" in obj and isinstance(obj["object"], dict):
                obj = obj["object"]
            blocks_data = obj.get("blocks", [])
            blocks = []
            if isinstance(blocks_data, list):
                for b in blocks_data:
                    try:
                        blocks.append(Block(**b))
                    except Exception:
                        pass
            obj.pop("blocks", None)
            obj.pop("details", None)
            return ObjectDetails(**obj, blocks=blocks)
        return ObjectDetails()

    async def get_objects(
        self, request: GetObjectsRequest, token: Optional[str] = None
    ) -> List[ObjectDetails]:
        """Get objects list"""
        # Convert GetObjectsRequest to SearchRequest
        # Create sort options first to ensure proper validation
        sort_options = SortOptions(
            direction="desc",
            timestamp=request.sort.value if request.sort else "last_modified_date",
        )
        search_request = SearchRequest(
            query="",
            space_id=request.space_id,
            types=request.types,
            limit=request.limit,
            offset=request.offset,
            sort=sort_options,
        )
        return await self.search_objects(search_request, token=token)

    async def delete_object(
        self, request: DeleteObjectRequest, token: Optional[str] = None
    ) -> BaseResponse:
        """Delete an object"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        object_id = data.pop("object_id")
        headers = self._get_headers()
        result = await make_request(
            "DELETE",
            get_endpoint("deleteObject", space_id=space_id, object_id=object_id),
            str(self.base_url),
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        return BaseResponse(**(responses[0] if responses else {}))

    async def search_objects(
        self, request: SearchRequest, token: Optional[str] = None
    ) -> List[ObjectDetails]:
        """Search for objects"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = self._get_headers()
        result = await make_request(
            "POST",
            get_endpoint("searchObjects", space_id=space_id),
            str(self.base_url),
            data=data,
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        # Filter out blocks and details from response objects
        filtered_responses = []
        for obj in responses:
            if isinstance(obj, dict):
                obj.pop("blocks", None)
                obj.pop("details", None)
                filtered_responses.append(obj)
        return [ObjectDetails(**obj) for obj in filtered_responses]

    async def global_search(
        self, request: GlobalSearchRequest, token: Optional[str] = None
    ) -> List[ObjectDetails]:
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
        responses = validate_response(result)
        # Filter out blocks and details from response objects
        filtered_responses = []
        for obj in responses:
            if isinstance(obj, dict):
                obj.pop("blocks", None)
                obj.pop("details", None)
                filtered_responses.append(obj)
        return [ObjectDetails(**obj) for obj in filtered_responses]

    async def get_types(
        self,
        space_id: Optional[str] = None,
        include_system: Optional[bool] = True,
        token: Optional[str] = None,
    ) -> List[TypeDetails]:
        """Get object types"""
        headers = self._get_headers()
        params = {"include_system": include_system}
        if space_id:
            params["space_id"] = space_id
        result = await make_request(
            "GET",
            get_endpoint("getTypes", space_id=space_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        return [TypeDetails(**type_) for type_ in responses]

    async def get_templates(
        self,
        space_id: Optional[str] = None,
        type_id: Optional[str] = None,
        include_system: Optional[bool] = True,
        token: Optional[str] = None,
    ) -> List[TemplateDetails]:
        """Get templates"""
        headers = self._get_headers()
        params = {"include_system": include_system}
        if space_id:
            params["space_id"] = space_id
        if type_id:
            params["type_id"] = type_id
        result = await make_request(
            "GET",
            get_endpoint("getTemplates", space_id=space_id, type_id=type_id),
            str(self.base_url),
            params=params,
            headers=headers,
            token=self._get_token(token),
        )
        responses = validate_response(result)
        return [TemplateDetails(**template) for template in responses]

    async def get_export(
        self,
        space_id: str,
        object_id: str,
        format: ExportFormat,
        token: Optional[str] = None,
    ) -> str:
        """Export an object in specified format"""
        headers = self._get_headers()
        result = await make_request(
            "POST",
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
        responses = validate_response(result)
        if len(responses) > 0:
            content = responses[0].get("content")
            if isinstance(content, str):
                return content
        return ""

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional app name"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        return headers

    def _get_token(self, token: Optional[str] = None) -> Optional[str]:
        """Get the most appropriate token to use"""
        return token or self.bearer_token or self.session_token


# FastAPI dependency
def get_anytype_client() -> AnytypeClient:
    """Dependency for getting AnytypeClient instance"""
    return AnytypeClient()
