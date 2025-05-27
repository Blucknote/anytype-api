"""API helper functions and utilities"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, TypedDict, Union

import httpx
from httpx import URL, Headers, QueryParams, Request, Response, Timeout

from .constants import ENDPOINTS, OBJECT_URL_PATTERN

logger = logging.getLogger(__name__)


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
    base_headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    if headers:
        base_headers.update(headers)

    # Use provided token or fall back to environment variable
    auth_token = token or os.getenv("ANYTYPE_API_KEY")
    if auth_token:
        # Add token to headers for Bearer authentication
        base_headers["Authorization"] = f"Bearer {auth_token}"

    start_time = time.time()
    logger.info(
        "Making API request: %s %s",
        method,
        endpoint,
        extra={
            "method": method,
            "endpoint": endpoint,
            "params": params,
            "has_data": bool(data),
        },
    )
    logger.debug(
        "Request details - Headers: %s, Data: %s, Params: %s",
        base_headers,
        data,
        params,
    )

    try:
        async with httpx.AsyncClient() as client:
            # Remove trailing slash from base_url and leading slash from endpoint to prevent double slashes
            base = base_url.rstrip("/")
            path = endpoint.lstrip("/")
            url = URL(f"{base}/{path}")
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
            duration = time.time() - start_time

            if response.status_code == 401:
                logger.warning(
                    "Unauthorized API request: %s %s",
                    method,
                    endpoint,
                    extra={"status_code": 401},
                )
                logger.warning(f"Response: {response.text}")
                raise APIError(
                    "Unauthorized. Please check your authentication token.", 401
                )

            response.raise_for_status()
            logger.info(
                "API request completed: %s %s - %d (%.2fs)",
                method,
                endpoint,
                response.status_code,
                duration,
                extra={
                    "status_code": response.status_code,
                    "duration": duration,
                },
            )

            try:
                result = response.json()
                logger.debug("API response data: %s", result)
                if isinstance(result, dict):
                    return result
                return {"data": result}
            except json.JSONDecodeError:
                if response.status_code == 204:
                    logger.debug("Empty response (204 No Content)")
                    return {}
                logger.error(
                    "Invalid JSON response from API: %s",
                    response.text[:200],
                    extra={"response_text": response.text},
                )
                raise APIError("Invalid JSON response from API", 500) from None

    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout):
        logger.error(
            "API request timed out: %s %s (%.2fs)",
            method,
            endpoint,
            time.time() - start_time,
            extra={"timeout_type": "request"},
        )
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
        logger.error(
            "API request failed: %s %s - %s (%.2fs)",
            method,
            endpoint,
            error_msg,
            time.time() - start_time,
            extra={
                "error": error_msg,
                "status_code": status_code,
            },
            exc_info=True,
        )
        raise APIError(error_msg, status_code) from None


def construct_object_url(object_id: str, space_id: str) -> str:
    """Construct a URL for an object using the standard pattern"""
    return OBJECT_URL_PATTERN.format(objectId=object_id, spaceId=space_id)


def validate_response(
    response: Union[Dict[str, Any], List[Dict[str, Any]], str],
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Validate and process API response"""
    logger.debug("Validating API response: %s", response)
    if not response:
        logger.error("Empty API response received")
        raise APIError("Empty response from API")

    # Handle string responses
    if isinstance(response, str):
        try:
            response = json.loads(response)
            logger.debug("Parsed string response to JSON: %s", response)
        except json.JSONDecodeError:
            logger.error(
                "Failed to parse string response as JSON: %s",
                response[:200],
                extra={"response": response},
            )
            raise APIError("Invalid JSON string response") from None

    if isinstance(response, dict) and response.get("error"):
        error_message = response["error"]
        logger.error("API error response: %s", error_message)
        raise APIError(error_message)

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
    logger.debug("Getting endpoint: %s with params: %s", name, kwargs)
    endpoint = ENDPOINTS.get(name)
    if not endpoint:
        logger.error("Unknown endpoint requested: %s", name)
        raise APIError(f"Unknown endpoint: {name}")
    try:
        formatted_endpoint = endpoint.format(**kwargs)
        logger.debug("Formatted endpoint: %s", formatted_endpoint)
        return formatted_endpoint
    except KeyError as e:
        logger.error(
            "Missing parameter for endpoint %s: %s",
            name,
            str(e),
            extra={"endpoint": name, "missing_param": str(e)},
        )
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
