"""Tests for string formatting utilities"""

from datetime import datetime
from typing import Any, Optional, Union

import pytest

from app.helpers.strings import (
    format_date,
    format_error_message,
    format_member_role,
    format_object_name,
    format_object_url,
    format_relation_key,
    format_snippet,
    format_source_link,
    format_space_name,
    format_tag_name,
    format_template_name,
    format_type_name,
    pluralize,
    sanitize_query,
)


@pytest.mark.parametrize(
    "count,singular,plural,expected",
    [
        (1, "item", None, "item"),
        (2, "item", None, "items"),
        (0, "item", None, "items"),
        (2, "child", "children", "children"),
        (1, "child", "children", "child"),
    ],
)
def test_pluralize(count: int, singular: str, plural: str, expected: str):
    """Test pluralization of words"""
    assert pluralize(count, singular, plural) == expected


@pytest.mark.parametrize(
    "object_id,space_id,expected",
    [
        ("123", "456", "anytype://object?objectId=123&spaceId=456"),
        ("", "", "anytype://object?objectId=&spaceId="),
    ],
)
def test_format_object_url(object_id: str, space_id: str, expected: str):
    """Test object URL formatting"""
    assert format_object_url(object_id, space_id) == expected


@pytest.mark.parametrize(
    "query,expected",
    [
        ("  hello  world  ", "hello world"),
        ("hello@#$%^&*world", "helloworld"),
        ("hello-world 123", "hello-world 123"),
        ("", ""),
        ("@#$%^&*", ""),
        ("   ", ""),
    ],
)
def test_sanitize_query(query: str, expected: str):
    """Test search query sanitization"""
    assert sanitize_query(query) == expected


@pytest.mark.parametrize(
    "text,max_length,expected",
    [
        ("Hello world", 20, "Hello world"),
        (
            "This is a very long text that needs to be truncated properly with ellipsis",
            20,
            "This is a very...",
        ),
        ("", 20, ""),
        ("  Hello   world  ", 20, "Hello world"),
        ("x" * 200, None, "x" * 147 + "..."),
    ],
)
def test_format_snippet(text: str, max_length: Optional[int], expected: str):
    """Test text snippet formatting"""
    result = format_snippet(text, max_length) if max_length else format_snippet(text)
    assert result == expected
    if max_length:
        assert len(result) <= max_length
    if text and len(text) > (max_length or 150):
        assert result.endswith("...")


@pytest.mark.parametrize(
    "error,expected",
    [
        ({"message": "Error occurred"}, "Error occurred"),
        (ValueError("Invalid value"), "Invalid value"),
        ("Error", "Error"),
        (123, "123"),
        (None, "None"),
    ],
)
def test_format_error_message(
    error: Union[dict, Exception, str, int, None], expected: str
):
    """Test error message formatting"""
    assert format_error_message(error) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("hello world", "Hello World"),
        ("  hello   world  ", "Hello World"),
        ("hello", "Hello"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_object_name(name: str, expected: str):
    """Test object name formatting"""
    assert format_object_name(name) == expected


@pytest.mark.parametrize(
    "type_name,expected",
    [
        ("Hello World", "hello_world"),
        ("  Hello   World  ", "hello_world"),
        ("HELLO", "hello"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_type_name(type_name: str, expected: str):
    """Test type name formatting"""
    assert format_type_name(type_name) == expected


@pytest.mark.parametrize(
    "date_str,expected",
    [
        ("2024-02-17T12:34:56Z", "2024-02-17 12:34:56"),
        ("invalid", "invalid"),
        ("", ""),
    ],
)
def test_format_date(date_str: str, expected: str):
    """Test date string formatting"""
    assert format_date(date_str) == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com/", "https://example.com"),
        ("http://example.com/", "http://example.com"),
        ("example.com/", "https://example.com"),
        ("", ""),
    ],
)
def test_format_source_link(url: str, expected: str):
    """Test source link URL formatting"""
    assert format_source_link(url) == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        ("OWNER", "owner"),
        ("admin", "admin"),
        ("  Member  ", "member"),
        ("viewer", "viewer"),
        ("invalid", "member"),
        ("", "member"),
    ],
)
def test_format_member_role(role: str, expected: str):
    """Test member role string formatting"""
    assert format_member_role(role) == expected


@pytest.mark.parametrize(
    "tag,expected",
    [
        ("Hello World", "hello-world"),
        ("  Hello   World  ", "hello-world"),
        ("hello@#$%^&*world", "helloworld"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_tag_name(tag: str, expected: str):
    """Test tag name formatting"""
    assert format_tag_name(tag) == expected


@pytest.mark.parametrize(
    "key,expected",
    [
        ("Hello World", "hello_world"),
        ("  Hello   World  ", "hello_world"),
        ("hello@#$%^&*world", "helloworld"),
        ("hello_world", "hello_world"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_relation_key(key: str, expected: str):
    """Test relation key formatting"""
    assert format_relation_key(key) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("hello world", "Hello World"),
        ("  hello   world  ", "Hello World"),
        ("hello", "Hello"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_space_name(name: str, expected: str):
    """Test space name formatting"""
    assert format_space_name(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("hello world", "Hello World"),
        ("  hello   world  ", "Hello World"),
        ("hello", "Hello"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_template_name(name: str, expected: str):
    """Test template name formatting"""
    assert format_template_name(name) == expected
