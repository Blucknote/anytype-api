"""Tests for authentication functionality"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.clients.anytype import AnytypeClient
from app.helpers.api import APIError
from app.helpers.schemas import DisplayCodeResponse, TokenResponse
from app.routers.auth import get_auth_display_code, get_token


@pytest.fixture
def mock_client():
    client = MagicMock(spec=AnytypeClient)
    client.get_auth_display_code = AsyncMock(
        return_value=DisplayCodeResponse(challenge_id="abc123")
    )
    client.get_token = AsyncMock(
        return_value=TokenResponse(
            app_key="test_app_key", session_token="test_session_token"
        )
    )
    return client


@pytest.mark.asyncio
async def test_get_auth_display_code_success(mock_client):
    """Test successful display code retrieval"""
    app_name = "Test App"
    result = await get_auth_display_code(app_name, mock_client)
    assert isinstance(result, DisplayCodeResponse)
    assert result.challenge_id == "abc123"
    mock_client.get_auth_display_code.assert_called_once_with(app_name)


@pytest.mark.asyncio
async def test_get_auth_display_code_error(mock_client):
    """Test display code retrieval with API error"""
    mock_client.get_auth_display_code.side_effect = APIError("API Error", 500)
    app_name = "Test App"

    with pytest.raises(HTTPException) as exc_info:
        await get_auth_display_code(app_name, mock_client)

    assert exc_info.value.status_code == 500
    assert "API Error" in str(exc_info.value.detail)
    mock_client.get_auth_display_code.assert_called_once_with(app_name)


@pytest.mark.asyncio
async def test_get_token_success(mock_client):
    """Test successful token retrieval"""
    code = "123456"
    challenge_id = "abc123"
    result = await get_token(code, challenge_id, mock_client)
    assert isinstance(result, TokenResponse)
    assert result.app_key == "test_app_key"
    assert result.session_token == "test_session_token"
    mock_client.get_token.assert_called_once_with(code, challenge_id)


@pytest.mark.asyncio
async def test_get_token_error(mock_client):
    """Test token retrieval with API error"""
    mock_client.get_token.side_effect = APIError("Invalid code", 400)
    code = "invalid"
    challenge_id = "abc123"

    with pytest.raises(HTTPException) as exc_info:
        await get_token(code, challenge_id, mock_client)

    assert exc_info.value.status_code == 400
    assert "Invalid code" in str(exc_info.value.detail)
    mock_client.get_token.assert_called_once_with(code, challenge_id)
