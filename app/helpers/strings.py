"""String manipulation and formatting utilities"""

import re
from typing import Any, Optional


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Return singular or plural form based on count"""
    if count == 1:
        return singular
    if plural is not None:
        return plural
    return f"{singular}s"


def format_object_url(object_id: str, space_id: str) -> str:
    """Format object URL with proper encoding"""
    return f"anytype://object?objectId={object_id}&spaceId={space_id}"


def sanitize_query(query: str) -> str:
    """Sanitize search query string"""
    # Remove multiple spaces
    query = re.sub(r"\s+", " ", query.strip())
    # Remove special characters that might interfere with search
    query = re.sub(r"[^\w\s-]", "", query)
    return query


def format_snippet(text: str, max_length: int = 150) -> str:
    """Format text snippet with proper length and ellipsis"""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def format_error_message(error: Any) -> str:
    """Format error message for consistent display"""
    if isinstance(error, dict) and "message" in error:
        return str(error["message"])
    if isinstance(error, Exception):
        return str(error)
    return str(error)


def format_object_name(name: str) -> str:
    """Format object name according to Anytype conventions"""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Replace multiple spaces with single space
    name = re.sub(r"\s+", " ", name)
    # Capitalize first letter of each word
    name = name.title()
    return name


def format_type_name(type_name: str) -> str:
    """Format type name according to Anytype conventions"""
    # Remove leading/trailing whitespace
    type_name = type_name.strip()
    # Replace multiple spaces with single space
    type_name = re.sub(r"\s+", " ", type_name)
    # Convert to lowercase
    type_name = type_name.lower()
    # Replace spaces with underscores
    type_name = type_name.replace(" ", "_")
    return type_name


def format_date(date_str: str) -> str:
    """Format date string for consistent display"""
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return date_str


def format_source_link(url: str) -> str:
    """Format source link URL"""
    if not url:
        return ""
    # Ensure URL has proper scheme
    if not re.match(r"^https?://", url):
        url = f"https://{url}"
    # Remove trailing slashes
    url = url.rstrip("/")
    return url


def format_member_role(role: str) -> str:
    """Format member role string"""
    role = role.lower().strip()
    valid_roles = {"owner", "admin", "member", "viewer"}
    return role if role in valid_roles else "member"


def format_tag_name(tag: str) -> str:
    """Format tag name according to Anytype conventions"""
    # Remove leading/trailing whitespace and special characters
    tag = re.sub(r"[^\w\s-]", "", tag.strip())
    # Replace multiple spaces with single space
    tag = re.sub(r"\s+", " ", tag)
    # Convert to lowercase
    tag = tag.lower()
    # Replace spaces with hyphens
    tag = tag.replace(" ", "-")
    return tag


def format_relation_key(key: str) -> str:
    """Format relation key according to Anytype conventions"""
    # Remove leading/trailing whitespace
    key = key.strip()
    # Replace multiple spaces with single space
    key = re.sub(r"\s+", " ", key)
    # Convert to lowercase and replace spaces with underscores
    key = key.lower().replace(" ", "_")
    # Remove special characters except underscores
    key = re.sub(r"[^\w_]", "", key)
    return key


def format_space_name(name: str) -> str:
    """Format space name according to Anytype conventions"""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Replace multiple spaces with single space
    name = re.sub(r"\s+", " ", name)
    # Capitalize first letter of each word
    name = name.title()
    return name


def format_template_name(name: str) -> str:
    """Format template name according to Anytype conventions"""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Replace multiple spaces with single space
    name = re.sub(r"\s+", " ", name)
    # Capitalize first letter of each word
    name = name.title()
    return name
