"""API helper functions and utilities"""

import json
import os
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import HTTPException

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
) -> Any:
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
    if headers is None:
        headers = {"Content-Type": "application/json"}

    # Use provided token or fall back to environment variable
    auth_token = token or os.getenv("ANYTYPE_APP_KEY")
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        async with httpx.AsyncClient() as client:
            request_params = {
                "method": method,
                "url": f"{base_url}{endpoint}",
                "headers": headers,
                "timeout": 30.0,
            }

            # Always include query parameters if provided
            if params:
                request_params["params"] = params

            # Always include body if provided (httpx will handle it appropriately)
            if data:
                request_params["json"] = data

            response = await client.request(**request_params)

            if response.status_code == 401:
                raise APIError(
                    "Unauthorized. Please check your authentication token.", 401
                )

            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                if response.status_code == 204:
                    return {}
                raise APIError("Invalid JSON response from API", 500)

    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout):
        raise APIError("Request timed out. Please try again.", 504)
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
        raise APIError(error_msg, status_code)


def construct_object_url(object_id: str, space_id: str) -> str:
    """Construct a URL for an object using the standard pattern"""
    return OBJECT_URL_PATTERN.format(objectId=object_id, spaceId=space_id)


def validate_response(
    response: Union[Dict[str, Any], List[Dict[str, Any]], str],
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Validate and process API response"""
    if not response:
        raise APIError("Empty response from API")

    # Handle string responses
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            raise APIError("Invalid JSON string response")

    if isinstance(response, dict) and response.get("error"):
        raise APIError(response["error"])

    # Ensure we always return a list of dictionaries
    if isinstance(response, dict):
        if "types" in response:
            types = response["types"]
            if not isinstance(types, list):
                types = [types]
            return [t if isinstance(t, dict) else {"id": str(t)} for t in types]
        if "data" in response:
            data = response["data"]
            if not isinstance(data, list):
                data = [data]
            return [d if isinstance(d, dict) else {"id": str(d)} for d in data]
        if "spaces" in response:
            spaces = response["spaces"]
            if not isinstance(spaces, list):
                spaces = [spaces]
            return [s if isinstance(s, dict) else {"id": str(s)} for s in spaces]
        if "members" in response:
            members = response["members"]
            if not isinstance(members, list):
                members = [members]
            return [m if isinstance(m, dict) else {"id": str(m)} for m in members]
        if "templates" in response:
            templates = response["templates"]
            if not isinstance(templates, list):
                templates = [templates]
            return [t if isinstance(t, dict) else {"id": str(t)} for t in templates]
        if "objects" in response:
            objects = response["objects"]
            if not isinstance(objects, list):
                objects = [objects]
            return [o if isinstance(o, dict) else {"id": str(o)} for o in objects]
        # If no specific key found, convert the whole dict to a list
        return [response]

    if isinstance(response, list):
        return [r if isinstance(r, dict) else {"id": str(r)} for r in response]

    # If we get here, convert whatever we have to a basic dict
    return [{"id": str(response)}]


def prepare_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare request data by removing None values and formatting"""
    return {k: v for k, v in data.items() if v is not None}


def get_endpoint(name: str, **kwargs) -> str:
    """Get API endpoint by name with parameter substitution"""
    endpoint = ENDPOINTS.get(name)
    if not endpoint:
        raise APIError(f"Unknown endpoint: {name}")
    try:
        return endpoint.format(**kwargs) if kwargs else endpoint
    except KeyError as e:
        raise APIError(f"Missing required parameter for endpoint {name}: {e}")


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
