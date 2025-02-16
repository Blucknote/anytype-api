"""Tests for authentication functionality"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.clients.anytype import AnytypeClient
from app.helpers.api import APIError
from app.main import get_validated_token
from app.routers.auth import get_auth_display_code, get_token, validate_token


@pytest.fixture
def mock_client():
    client = MagicMock(spec=AnytypeClient)
    client.validate_token = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_get_validated_token_valid(mock_client):
    """Test token validation with valid token"""
    test_token = "test_token"
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=test_token)
    mock_client.validate_token.return_value = True

    result = await get_validated_token(credentials, mock_client)

    assert result == test_token
    mock_client.validate_token.assert_called_once_with(test_token)


@pytest.mark.asyncio
async def test_get_validated_token_invalid(mock_client):
    """Test token validation with invalid token"""
    test_token = "invalid_token"
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=test_token)
    mock_client.validate_token.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await get_validated_token(credentials, mock_client)

    assert exc_info.value.status_code == 401
    assert "Invalid authentication token" in str(exc_info.value.detail)
    mock_client.validate_token.assert_called_once_with(test_token)


@pytest.mark.asyncio
async def test_get_validated_token_api_error(mock_client):
    """Test token validation when API raises an error"""
    test_token = "test_token"
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=test_token)
    mock_client.validate_token.side_effect = Exception("API Error")

    with pytest.raises(HTTPException) as exc_info:
        await get_validated_token(credentials, mock_client)

    assert exc_info.value.status_code == 401
    assert "API Error" in str(exc_info.value.detail)
    mock_client.validate_token.assert_called_once_with(test_token)


@pytest.mark.asyncio
async def test_get_auth_display_code_success(mock_client):
    """Test successful display code retrieval"""
    mock_response = {"code": "123456", "challengeId": "abc123"}
    mock_client.get_auth_display_code.return_value = mock_response

    result = await get_auth_display_code("Test App", mock_client)
    assert result == mock_response
    mock_client.get_auth_display_code.assert_called_once_with("Test App")


@pytest.mark.asyncio
async def test_get_auth_display_code_error(mock_client):
    """Test display code retrieval with API error"""
    mock_client.get_auth_display_code.side_effect = APIError("API Error", 500)

    with pytest.raises(HTTPException) as exc_info:
        await get_auth_display_code("Test App", mock_client)

    assert exc_info.value.status_code == 500
    assert "API Error" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_token_success(mock_client):
    """Test successful token retrieval"""
    mock_response = {"token": "test_token", "expiresIn": 3600}
    mock_client.get_token.return_value = mock_response

    result = await get_token("123456", "abc123", mock_client)
    assert result == mock_response
    mock_client.get_token.assert_called_once_with("123456", "abc123")


@pytest.mark.asyncio
async def test_get_token_error(mock_client):
    """Test token retrieval with API error"""
    mock_client.get_token.side_effect = APIError("Invalid code", 400)

    with pytest.raises(HTTPException) as exc_info:
        await get_token("invalid", "abc123", mock_client)

    assert exc_info.value.status_code == 400
    assert "Invalid code" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_validate_token_success(mock_client):
    """Test successful token validation"""
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="test_token"
    )
    mock_client.validate_token.return_value = True

    result = await validate_token(credentials, mock_client)
    assert result == {"valid": True}
    mock_client.validate_token.assert_called_once_with("test_token")


@pytest.mark.asyncio
async def test_validate_token_error(mock_client):
    """Test token validation with API error"""
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="test_token"
    )
    mock_client.validate_token.side_effect = APIError("Invalid token", 401)

    with pytest.raises(HTTPException) as exc_info:
        await validate_token(credentials, mock_client)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail)
