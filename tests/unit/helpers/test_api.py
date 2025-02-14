"""Tests for API helper functions"""

import pytest
import httpx
from unittest.mock import patch

from app.helpers.api import (
    make_request,
    validate_response,
    prepare_request_data,
    get_endpoint,
    construct_object_url,
    APIError,
)
from app.helpers.constants import ENDPOINTS


@pytest.mark.asyncio
async def test_make_request_success(test_client: httpx.AsyncClient):
    """Test successful API request"""
    with patch.dict("os.environ", {"ANYTYPE_APP_KEY": "test_app_key"}):
        response_data = {"message": "Success"}
        (test_client.get).return_value = httpx.Response(200, json=response_data)
        result = await make_request(
            "GET", "/test", "http://test", headers={"Content-Type": "application/json"}
        )
        assert result == response_data


@pytest.mark.asyncio
async def test_make_request_unauthorized(test_client: httpx.AsyncClient):
    """Test unauthorized API request"""
    with patch.dict("os.environ", {"ANYTYPE_APP_KEY": "test_app_key"}):
        (test_client.get).return_value = httpx.Response(401, json={"message": "Unauthorized"})
        with pytest.raises(APIError) as exc_info:
            await make_request(
                "GET", "/test", "http://test", headers={"Content-Type": "application/json"}
            )
        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_make_request_timeout(test_client: httpx.AsyncClient):
    """Test API request timeout"""
    with patch.dict("os.environ", {"ANYTYPE_APP_KEY": "test_app_key"}):
        (test_client.get).side_effect = httpx.ReadTimeout("Timeout")
        with pytest.raises(APIError) as exc_info:
            await make_request(
                "GET", "/test", "http://test", headers={"Content-Type": "application/json"}
            )
        assert exc_info.value.status_code == 504
        assert "timed out" in str(exc_info.value)


@pytest.mark.asyncio
async def test_make_request_http_error(test_client: httpx.AsyncClient):
    """Test HTTP error during API request"""
    with patch.dict("os.environ", {"ANYTYPE_APP_KEY": "test_app_key"}):
        (test_client.get).side_effect = httpx.HTTPError("HTTP Error")
        with pytest.raises(APIError) as exc_info:
            await make_request(
                "GET", "/test", "http://test", headers={"Content-Type": "application/json"}
            )
        assert exc_info.value.status_code == 500
        assert "HTTP Error" in str(exc_info.value)


def test_validate_response_success():
    """Test successful response validation"""
    response_data = {"message": "Success"}
    result = validate_response(response_data)
    assert result == [response_data]


def test_validate_response_error():
    """Test response validation with error"""
    response_data = {"error": "Error message"}
    with pytest.raises(APIError) as exc_info:
        validate_response(response_data)
    assert "Error message" in str(exc_info.value)


def test_validate_response_empty():
    """Test validation of empty response"""
    with pytest.raises(APIError) as exc_info:
        validate_response(None)
    assert "Empty response" in str(exc_info.value)


def test_prepare_request_data():
    """Test request data preparation"""
    data = {"key1": "value1", "key2": None, "key3": 123}
    result = prepare_request_data(data)
    assert result == {"key1": "value1", "key3": 123}


def test_get_endpoint_success():
    """Test successful endpoint retrieval"""
    endpoint_name = "getSpaces"
    endpoint = ENDPOINTS[endpoint_name]
    result = get_endpoint(endpoint_name)
    assert result == endpoint


def test_get_endpoint_missing_parameter():
    """Test endpoint retrieval with missing parameter"""
    with pytest.raises(APIError) as exc_info:
        get_endpoint("getObject")
    assert "Missing required parameter" in str(exc_info.value)


def test_construct_object_url():
    """Test object URL construction"""
    object_id = "test_object_id"
    space_id = "test_space_id"
    expected_url = f"anytype://objects/{object_id}@space/{space_id}"
    result = construct_object_url(object_id, space_id)
    assert result == expected_url