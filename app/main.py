"""FastAPI backend for Anytype integration"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .helpers.api import (
    APIError,
    construct_object_url,
    get_endpoint,
    make_request,
    prepare_request_data,
    validate_response,
)
from .helpers.constants import (
    DEFAULT_PAGE_SIZE,
    ENDPOINTS,
    MAX_PAGE_SIZE,
    SYSTEM_TYPES,
)
from .helpers.schemas import (
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
    PaginationParams,
    SearchRequest,
    SortOrder,
    SpaceDetails,
    TemplateDetails,
    TokenValidationRequest,
    TypeDetails,
    ViewType,
)
from .helpers.strings import (
    format_member_role,
    format_object_name,
    format_snippet,
    format_source_link,
    format_type_name,
    sanitize_query,
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Anytype API",
    description="FastAPI backend for Anytype integration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for token validation
async def validate_token(authorization: str = Header(...)) -> str:
    """Validate the authorization token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    try:
        await anytype_client.validate_token(token)
        return token
    except APIError as e:
        raise HTTPException(status_code=401, detail=str(e))


# Anytype API client
class AnytypeClient:
    def __init__(self):
        self.base_url = os.getenv("ANYTYPE_API_URL")
        self.session_token = os.getenv("ANYTYPE_SESSION_TOKEN")
        self.app_key = os.getenv("ANYTYPE_APP_KEY")

        if not self.base_url:
            raise ValueError("ANYTYPE_API_URL environment variable is required")
        if not self.session_token:
            raise ValueError("ANYTYPE_SESSION_TOKEN environment variable is required")
        if not self.app_key:
            raise ValueError("ANYTYPE_APP_KEY environment variable is required")

        self.headers = {
            "Content-Type": "application/json",
        }
        self.app_name = None
        self.challenge_id = None  # Store challenge_id for token request

    async def validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        return token == self.session_token

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
            self.base_url,
            data=data,
            headers=headers,
        )
        response = validate_response(result)
        # Store the session token for future requests
        if "token" in response and "session_token" in response["token"]:
            self.session_token = response["token"]["session_token"]
        return response

    async def get_auth_display_code(
        self, app_name: str = "Anytype API"
    ) -> DisplayCodeResponse:
        """Get display code for authentication"""
        logger.debug("Input app_name: %s", app_name)
        self.app_name = app_name
        headers = {**self.headers, "X-App-Name": app_name}
        data = {"app_name": app_name}
        if self.session_token:
            data["token"] = self.session_token
        logger.debug("Request headers: %s", headers)
        logger.debug("Request data: %s", data)
        logger.debug("Base URL: %s", self.base_url)
        logger.debug("Endpoint: %s", get_endpoint("displayCode", app_name=app_name))

        result = await make_request(
            "POST",
            get_endpoint("displayCode", app_name=app_name),
            self.base_url,
            data=data,
            headers=headers,
        )
        logger.debug("Raw response: %s", result)
        response = validate_response(result)
        logger.debug("Validated response: %s", response)
        self.challenge_id = response.get("challenge_id")
        return DisplayCodeResponse(
            code=response.get("code", ""), challenge_id=self.challenge_id
        )

    async def create_space(self, request: CreateSpaceRequest) -> SpaceDetails:
        """Create a new space"""
        data = prepare_request_data(request.dict())
        data["name"] = format_object_name(data["name"])
        data["token"] = self.session_token
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        result = await make_request(
            "POST",
            get_endpoint("createSpace"),
            self.base_url,
            data,
            headers,
        )
        return SpaceDetails(**validate_response(result))

    async def get_spaces(
        self, limit: int = DEFAULT_PAGE_SIZE, offset: int = 0
    ) -> List[SpaceDetails]:
        """Get list of spaces"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {"limit": limit, "offset": offset, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getSpaces"),
            self.base_url,
            params=params,
            headers=headers,
        )

        # Log raw response for debugging
        logger.debug("Raw getSpaces response: %s", result)

        # Validate and parse response
        response = validate_response(result)

        # Handle different response formats
        if isinstance(response, dict):
            if "spaces" in response:
                spaces = response["spaces"]
            elif "data" in response:
                spaces = response["data"]
            else:
                spaces = [response]
        elif isinstance(response, list):
            spaces = response
        else:
            raise APIError(f"Unexpected response format: {type(response)}")

        # Validate each space is a dictionary
        valid_spaces = []
        for space in spaces:
            if not isinstance(space, dict):
                logger.warning("Skipping invalid space data: %s", space)
                continue
            valid_spaces.append(space)

        return [SpaceDetails(**space) for space in valid_spaces]

    async def get_members(self, request: GetMembersRequest) -> List[MemberDetails]:
        """Get space members"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getMembers", space_id=space_id),
            self.base_url,
            params=params,
            headers=headers,
        )
        return [MemberDetails(**member) for member in validate_response(result)]

    async def create_object(self, request: CreateObjectRequest) -> ObjectDetails:
        """Create a new object"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        data["name"] = format_object_name(data["name"])
        if data.get("type"):
            data["type"] = format_type_name(data["type"])
        if data.get("source_link"):
            data["source_link"] = format_source_link(data["source_link"])
        data["token"] = self.session_token

        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        result = await make_request(
            "POST",
            get_endpoint("createObject", space_id=space_id),
            self.base_url,
            data,
            headers,
        )
        return ObjectDetails(**validate_response(result))

    async def get_object(self, space_id: str, object_id: str) -> ObjectDetails:
        """Get object details"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {"token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getObject", space_id=space_id, object_id=object_id),
            self.base_url,
            params=params,
            headers=headers,
        )
        return ObjectDetails(**validate_response(result))

    async def get_objects(self, request: GetObjectsRequest) -> List[ObjectDetails]:
        """Get objects list"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getObjects", space_id=space_id),
            self.base_url,
            params=params,
            headers=headers,
        )
        return [ObjectDetails(**obj) for obj in validate_response(result)]

    async def delete_object(self, request: DeleteObjectRequest) -> BaseResponse:
        """Delete an object"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        object_id = data.pop("object_id")
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {"token": self.session_token}
        result = await make_request(
            "DELETE",
            get_endpoint("deleteObject", space_id=space_id, object_id=object_id),
            self.base_url,
            params=params,
            headers=headers,
        )
        return BaseResponse(**validate_response(result))

    async def search_objects(self, request: SearchRequest) -> List[ObjectDetails]:
        """Search for objects"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        data["query"] = sanitize_query(data["query"])
        data["token"] = self.session_token

        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        result = await make_request(
            "POST",
            get_endpoint("searchObjects", space_id=space_id),
            self.base_url,
            data,
            headers,
        )
        return [ObjectDetails(**obj) for obj in validate_response(result)]

    async def global_search(self, request: GlobalSearchRequest) -> List[ObjectDetails]:
        """Global search across all spaces"""
        data = prepare_request_data(request.dict())
        data["query"] = sanitize_query(data["query"])
        data["token"] = self.session_token

        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        result = await make_request(
            "POST",
            get_endpoint("globalSearch"),
            self.base_url,
            data,
            headers,
        )
        return [ObjectDetails(**obj) for obj in validate_response(result)]

    async def get_types(self, request: GetTypesRequest) -> List[TypeDetails]:
        """Get object types"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getTypes", space_id=space_id),
            self.base_url,
            params=params,
            headers=headers,
        )
        return [TypeDetails(**type_) for type_ in validate_response(result)]

    async def get_templates(
        self, request: GetTemplatesRequest
    ) -> List[TemplateDetails]:
        """Get templates"""
        data = prepare_request_data(request.dict())
        space_id = data.pop("space_id")
        type_id = data.pop("type_id")
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        params = {**data, "token": self.session_token}
        result = await make_request(
            "GET",
            get_endpoint("getTemplates", space_id=space_id, type_id=type_id),
            self.base_url,
            params=params,
            headers=headers,
        )
        return [TemplateDetails(**template) for template in validate_response(result)]

    async def get_export(
        self, space_id: str, object_id: str, format: ExportFormat
    ) -> str:
        """Export an object in specified format"""
        headers = {**self.headers}
        if self.app_name:
            headers["X-App-Name"] = self.app_name
        data = {"token": self.session_token}
        result = await make_request(
            "POST",
            get_endpoint(
                "getExport", space_id=space_id, object_id=object_id, format=format
            ),
            self.base_url,
            data=data,
            headers=headers,
        )
        return validate_response(result).get("content", "")


# Initialize Anytype client
anytype_client = AnytypeClient()


# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Anytype API"}


# Authentication endpoints
@app.post("/auth/display-code", response_model=DisplayCodeResponse)
async def get_auth_display_code(app_name: str = "Anytype API"):
    """Get display code for authentication"""
    try:
        logger.info("Requesting display code with app_name: %s", app_name)
        result = await anytype_client.get_auth_display_code(app_name)
        logger.debug("Response: %s", result)
        return result
    except APIError as e:
        logger.error("Error getting display code: %s", str(e))
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.post("/auth/token")
async def get_token(code: str, challenge_id: Optional[str] = None):
    """Get authentication token from display code"""
    try:
        response = await anytype_client.get_token(code, challenge_id)
        return response
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/auth/validate")
async def validate_token(token: str):
    """Validate authentication token"""
    try:
        valid = await anytype_client.validate_token(token)
        return {"valid": valid}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


# Space endpoints
@app.post("/space/create", response_model=SpaceDetails)
async def create_space(
    request: CreateSpaceRequest, token: str = Depends(validate_token)
):
    """Create a new space in Anytype"""
    try:
        anytype_client.session_token = token
        return await anytype_client.create_space(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/space/list", response_model=List[SpaceDetails])
async def get_spaces(
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    token: str = Depends(validate_token),
):
    """Get list of spaces"""
    try:
        anytype_client.session_token = token
        return await anytype_client.get_spaces(limit, offset)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/space/members", response_model=List[MemberDetails])
async def get_members(
    request: GetMembersRequest = Depends(), token: str = Depends(validate_token)
):
    """Get space members"""
    try:
        anytype_client.session_token = token
        return await anytype_client.get_members(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


# Object endpoints
@app.post("/object/create", response_model=ObjectDetails)
async def create_object(
    request: CreateObjectRequest, token: str = Depends(validate_token)
):
    """Create a new object in Anytype"""
    try:
        anytype_client.session_token = token
        return await anytype_client.create_object(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/object/get/{space_id}/{object_id}", response_model=ObjectDetails)
async def get_object(
    space_id: str, object_id: str, token: str = Depends(validate_token)
):
    """Get object details"""
    try:
        anytype_client.session_token = token
        return await anytype_client.get_object(space_id, object_id)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/object/list", response_model=List[ObjectDetails])
async def get_objects(
    request: GetObjectsRequest = Depends(), token: str = Depends(validate_token)
):
    """Get objects list"""
    try:
        anytype_client.session_token = token
        return await anytype_client.get_objects(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.post("/object/delete", response_model=BaseResponse)
async def delete_object(
    request: DeleteObjectRequest, token: str = Depends(validate_token)
):
    """Delete an object from Anytype"""
    try:
        anytype_client.session_token = token
        return await anytype_client.delete_object(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.post("/object/search", response_model=List[ObjectDetails])
async def search_objects(request: SearchRequest, token: str = Depends(validate_token)):
    """Search for objects in Anytype with advanced filtering and sorting"""
    try:
        anytype_client.session_token = token
        return await anytype_client.search_objects(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.post("/object/search/global", response_model=List[ObjectDetails])
async def global_search(
    request: GlobalSearchRequest, token: str = Depends(validate_token)
):
    """Global search across all spaces"""
    try:
        anytype_client.session_token = token
        return await anytype_client.global_search(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.post("/object/export/{space_id}/{object_id}")
async def get_export(
    space_id: str,
    object_id: str,
    format: ExportFormat = Query(ExportFormat.MARKDOWN, description="Export format"),
    token: str = Depends(validate_token),
):
    """Export an object in the specified format"""
    try:
        anytype_client.session_token = token
        content = await anytype_client.get_export(space_id, object_id, format)
        return {"content": content}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/object/code/{space_id}/{object_id}")
async def get_display_code(
    space_id: str, object_id: str, token: str = Depends(validate_token)
):
    """Get the display code for an object"""
    try:
        anytype_client.session_token = token
        code = await anytype_client.get_display_code(space_id, object_id)
        return {"code": code}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


# Type endpoints
@app.get("/type/list", response_model=List[TypeDetails])
async def get_types(
    request: GetTypesRequest = Depends(), token: str = Depends(validate_token)
):
    """Get object types"""
    try:
        anytype_client.session_token = token
        return await anytype_client.get_types(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@app.get("/template/list", response_model=List[TemplateDetails])
async def get_templates(
    request: GetTemplatesRequest = Depends(), token: str = Depends(validate_token)
):
    """Get templates"""
    try:
        anytype_client.session_token = token
        return await anytype_client.get_templates(request)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
