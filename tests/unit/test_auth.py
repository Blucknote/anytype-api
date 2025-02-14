"""Tests for authentication functionality"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.clients.anytype import AnytypeClient
from app.main import get_validated_token


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
