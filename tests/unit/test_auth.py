"""Tests for authentication functionality"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.clients.anytype import AnytypeClient
from app.helpers.api import APIError
from app.helpers.schemas import ChallengeResponse, TokenResponse
from app.routers.auth import create_api_key, create_challenge


@pytest.fixture
def mock_client():
    client = MagicMock(spec=AnytypeClient)
    client.create_challenge = AsyncMock(
        return_value=ChallengeResponse(challenge_id="abc123")
    )
    client.create_api_key = AsyncMock(
        return_value=TokenResponse(api_key="test_api_key")
    )
    return client


@pytest.mark.asyncio
async def test_create_challenge_success(mock_client):
    """Test successful challenge creation"""
    app_name = "Test App"
    result = await create_challenge(app_name, mock_client)
    assert isinstance(result, ChallengeResponse)
    assert result.challenge_id == "abc123"
    mock_client.create_challenge.assert_called_once_with(app_name)


@pytest.mark.asyncio
async def test_create_challenge_error(mock_client):
    """Test challenge creation with API error"""
    mock_client.create_challenge.side_effect = APIError("API Error", 500)
    app_name = "Test App"

    with pytest.raises(HTTPException) as exc_info:
        await create_challenge(app_name, mock_client)

    assert exc_info.value.status_code == 500
    assert "API Error" in str(exc_info.value.detail)
    mock_client.create_challenge.assert_called_once_with(app_name)


@pytest.mark.asyncio
async def test_create_api_key_success(mock_client):
    """Test successful API key creation"""
    code = "123456"
    challenge_id = "abc123"
    result = await create_api_key(code, challenge_id, mock_client)
    assert isinstance(result, TokenResponse)
    assert result.api_key == "test_api_key"
    mock_client.create_api_key.assert_called_once_with(code, challenge_id)


@pytest.mark.asyncio
async def test_create_api_key_error(mock_client):
    """Test API key creation with API error"""
    mock_client.create_api_key.side_effect = APIError("Invalid code", 400)
    code = "invalid"
    challenge_id = "abc123"

    with pytest.raises(HTTPException) as exc_info:
        await create_api_key(code, challenge_id, mock_client)

    assert exc_info.value.status_code == 400
    assert "Invalid code" in str(exc_info.value.detail)
    mock_client.create_api_key.assert_called_once_with(code, challenge_id)
