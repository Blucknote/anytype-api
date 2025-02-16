"""Tests for validation utilities"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.helpers.schemas import TypeDetails
from app.helpers.validators import TypeValidator


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_types = AsyncMock()
    return client


@pytest.fixture
def validator():
    return TypeValidator()


@pytest.mark.asyncio
async def test_validate_types_none(validator, mock_client):
    """Test validation with no types provided"""
    result = await validator.validate_types(None, None, mock_client, "test_token")
    assert result is None
    mock_client.get_types.assert_not_called()


@pytest.mark.asyncio
async def test_validate_types_empty_list(validator, mock_client):
    """Test validation with empty type list"""
    result = await validator.validate_types([], None, mock_client, "test_token")
    assert result is None
    mock_client.get_types.assert_not_called()


@pytest.mark.asyncio
async def test_validate_types_global(validator, mock_client):
    """Test validation against global types"""
    mock_types = [
        TypeDetails(id="type1", name="Type 1"),
        TypeDetails(id="type2", name="Type 2"),
    ]
    mock_client.get_types.return_value = mock_types

    result = await validator.validate_types(
        ["type1", "type2"], None, mock_client, "test_token"
    )

    assert result == ["type1", "type2"]
    mock_client.get_types.assert_called_once_with(
        space_id=None, include_system=True, token="test_token"
    )


@pytest.mark.asyncio
async def test_validate_types_space_specific(validator, mock_client):
    """Test validation against space-specific types"""
    mock_types = [
        TypeDetails(id="type1", name="Type 1"),
        TypeDetails(id="type2", name="Type 2"),
    ]
    mock_client.get_types.return_value = mock_types
    space_id = "test_space"

    result = await validator.validate_types(
        ["type1"], space_id, mock_client, "test_token"
    )

    assert result == ["type1"]
    mock_client.get_types.assert_called_once_with(
        space_id=space_id, include_system=True, token="test_token"
    )


@pytest.mark.asyncio
async def test_validate_types_invalid(validator, mock_client):
    """Test validation with invalid types"""
    mock_types = [TypeDetails(id="type1", name="Type 1")]
    mock_client.get_types.return_value = mock_types

    with pytest.raises(HTTPException) as exc_info:
        await validator.validate_types(
            ["type1", "invalid_type"], None, mock_client, "test_token"
        )

    assert exc_info.value.status_code == 400
    assert "Invalid type(s): invalid_type" in str(exc_info.value.detail)
    assert "Valid types are: type1" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_validate_types_no_types_returned(validator, mock_client):
    """Test validation when no types are returned"""
    mock_client.get_types.return_value = []
    types_to_validate = ["type1", "type2"]

    result = await validator.validate_types(
        types_to_validate, None, mock_client, "test_token"
    )

    assert result == types_to_validate
    mock_client.get_types.assert_called_once()


@pytest.mark.asyncio
async def test_validate_types_type_not_found_error(validator, mock_client):
    """Test validation when type not found error occurs"""
    mock_client.get_types.side_effect = Exception("type not found")
    types_to_validate = ["type1", "type2"]

    result = await validator.validate_types(
        types_to_validate, None, mock_client, "test_token"
    )

    assert result == types_to_validate
    mock_client.get_types.assert_called_once()


@pytest.mark.asyncio
async def test_validate_types_other_error(validator, mock_client):
    """Test validation when other error occurs"""
    mock_client.get_types.side_effect = Exception("Other error")

    with pytest.raises(Exception) as exc_info:
        await validator.validate_types(["type1"], None, mock_client, "test_token")

    assert str(exc_info.value) == "Other error"
    mock_client.get_types.assert_called_once()


@pytest.mark.asyncio
async def test_validate_types_caching(validator, mock_client):
    """Test type validation caching"""
    mock_types = [
        TypeDetails(id="type1", name="Type 1"),
        TypeDetails(id="type2", name="Type 2"),
    ]
    mock_client.get_types.return_value = mock_types

    # First call should fetch types
    await validator.validate_types(["type1"], None, mock_client, "test_token")
    assert mock_client.get_types.call_count == 1

    # Second call should use cached types
    await validator.validate_types(["type2"], None, mock_client, "test_token")
    assert mock_client.get_types.call_count == 1

    # Call with different space_id should fetch new types
    await validator.validate_types(["type1"], "space1", mock_client, "test_token")
    assert mock_client.get_types.call_count == 2
