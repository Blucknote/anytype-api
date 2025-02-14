"""Tests for authentication functionality"""

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import validate_token


class MockHeader:
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)


class MockQuery:
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)


@pytest.mark.asyncio
async def test_validate_token_with_header():
    """Test token validation with Authorization header"""
    test_token = "test_token"
    authorization = MockHeader(f"Bearer {test_token}")
    result = await validate_token(authorization=authorization)
    assert result == test_token


@pytest.mark.asyncio
async def test_validate_token_with_query():
    """Test token validation with query parameter"""
    test_token = "test_token"
    token = MockQuery(test_token)
    result = await validate_token(authorization=None, token=token)
    assert result == test_token


@pytest.mark.asyncio
async def test_validate_token_with_both():
    """Test token validation with both header and query parameter (header should take precedence)"""
    header_token = "header_token"
    query_token = "query_token"
    authorization = MockHeader(f"Bearer {header_token}")
    token = MockQuery(query_token)
    result = await validate_token(authorization=authorization, token=token)
    assert result == header_token


@pytest.mark.asyncio
async def test_validate_token_missing():
    """Test token validation with no token provided"""
    with pytest.raises(HTTPException) as exc_info:
        await validate_token(authorization=None, token=None)
    assert exc_info.value.status_code == 401
    assert "No valid token found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_validate_token_invalid_header():
    """Test token validation with invalid Authorization header format"""
    authorization = MockHeader("InvalidFormat token")
    with pytest.raises(HTTPException) as exc_info:
        await validate_token(authorization=authorization, token=None)
    assert exc_info.value.status_code == 401
    assert "No valid token found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_validate_token_empty_header():
    """Test token validation with empty Bearer token"""
    authorization = MockHeader("Bearer ")
    with pytest.raises(HTTPException) as exc_info:
        await validate_token(authorization=authorization, token=None)
    assert exc_info.value.status_code == 401
    assert "No valid token found" in str(exc_info.value.detail)
