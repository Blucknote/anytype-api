"""API helper functions and utilities"""

import json
import os
from typing import Any, Dict, List, Optional, TypedDict, Union

import httpx
from httpx import URL, Headers, QueryParams, Request, Response, Timeout

from .constants import ENDPOINTS, OBJECT_URL_PATTERN


class APIError(Exception):
    """Custom exception for API errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def make_request(
    method: str,
    endpoint: str,
    base_url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """Make an HTTP request to the Anytype API

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        base_url: Base URL of the API
        data: Request body data
        headers: Additional headers
        params: Query parameters
        token: Optional Bearer token for authentication
    """
    base_headers = {"Content-Type": "application/json"}
    if headers:
        base_headers.update(headers)

    # Use provided token or fall back to environment variable
    auth_token = token or os.getenv("ANYTYPE_APP_KEY")
    if auth_token:
        # Add token to headers for Bearer authentication
        base_headers["Authorization"] = f"Bearer {auth_token}"

    try:
        async with httpx.AsyncClient() as client:
            url = URL(f"{base_url}{endpoint}")
            timeout = Timeout(30.0)
            request_headers = Headers(base_headers)

            request_params = {
                "method": method,
                "url": url,
                "headers": request_headers,
                "timeout": timeout,
            }
            if params:
                request_params["params"] = params
            if data:
                request_params["json"] = data

            response: Response = await client.request(**request_params)

            if response.status_code == 401:
                raise APIError(
                    "Unauthorized. Please check your authentication token.", 401
                )

            response.raise_for_status()

            try:
                result = response.json()
                if isinstance(result, dict):
                    return result
                return {"data": result}
            except json.JSONDecodeError:
                if response.status_code == 204:
                    return {}
                raise APIError("Invalid JSON response from API", 500) from None

    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout):
        raise APIError("Request timed out. Please try again.", 504) from None
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        error_msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict):
                    error_msg = error_data.get("error", error_msg)
            except json.JSONDecodeError:
                pass
        raise APIError(error_msg, status_code) from None


def construct_object_url(object_id: str, space_id: str) -> str:
    """Construct a URL for an object using the standard pattern"""
    return OBJECT_URL_PATTERN.format(objectId=object_id, spaceId=space_id)


def validate_response(
    response: Union[Dict[str, Any], List[Dict[str, Any]], str],
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Validate and process API response"""
    if not response:
        raise APIError("Empty response from API")

    # Handle string responses
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise APIError("Invalid JSON string response") from None

    if isinstance(response, dict) and response.get("error"):
        raise APIError(response["error"])

    # Handle nested data structures
    if isinstance(response, dict):
        if "data" in response:
            data = response["data"]
            if isinstance(data, list):
                return data
            return [data]
        return [response]
    elif isinstance(response, list):
        return [r if isinstance(r, dict) else {"id": str(r)} for r in response]
    else:
        return [{"value": str(response)}]


class RequestData(TypedDict, total=False):
    """Type for request data"""

    space_id: str
    object_id: str
    type_id: str
    token: str
    app_name: str
    code: str
    challenge_id: str
    limit: int
    offset: int
    sort: str
    types: List[str]
    include_system: bool
    include_archived: bool
    include_favorites: bool
    query: str


def prepare_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare request data by removing None values and formatting"""
    return {k: v for k, v in data.items() if v is not None}


def get_endpoint(name: str, **kwargs: Any) -> str:
    """Get API endpoint by name with parameter substitution"""
    endpoint = ENDPOINTS.get(name)
    if not endpoint:
        raise APIError(f"Unknown endpoint: {name}")
    try:
        formatted_endpoint = endpoint.format(**kwargs)
        return formatted_endpoint
    except KeyError as e:
        raise APIError(f"Missing required parameter for endpoint {name}: {e}") from e


async def get_auth_display_code(
    base_url: str, app_name: str, token: Optional[str] = None
) -> Dict[str, Any]:
    """Request a display code for authentication

    Args:
        base_url: Base URL of the Anytype API
        app_name: Name of the application requesting authentication
        token: Optional Bearer token for authentication

    Returns:
        Dictionary containing the display code response
    """
    endpoint = get_endpoint("displayCode", app_name=app_name)
    return await make_request(
        method="POST",
        endpoint=endpoint,
        base_url=base_url,
        headers={"Content-Type": "application/json"},
        token=token,
    )
