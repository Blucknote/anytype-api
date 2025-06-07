"""API endpoint constants and configuration"""

# API Endpoints
ENDPOINTS = {
    # Object operations
    "createObject": "/v1/spaces/{space_id}/objects",
    "deleteObject": "/v1/spaces/{space_id}/objects/{object_id}",
    "getObject": "/v1/spaces/{space_id}/objects/{object_id}",
    "getObjects": "/v1/spaces/{space_id}/objects",
    "searchObjects": "/v1/spaces/{space_id}/search",
    "globalSearch": "/v1/search",
    "getExport": "/v1/spaces/{space_id}/objects/{object_id}/export/{format}",
    # Space operations
    "createSpace": "/v1/spaces",
    "getSpace": "/v1/spaces/{space_id}",
    "getSpaces": "/v1/spaces",
    "getMembers": "/v1/spaces/{space_id}/members",
    # Type operations
    "getTypes": "/v1/spaces/{space_id}/types",
    "getType": "/v1/spaces/{space_id}/types/{type_id}",
    "getTemplates": "/v1/spaces/{space_id}/types/{type_id}/templates",
    # Authentication (NEW)
    "createChallenge": "/v1/auth/challenges",
    "createApiKey": "/v1/auth/api_keys",
    # Tag operations
    "getTags": "/v1/spaces/{space_id}/properties/{property_id}/tags",
    "getTag": "/v1/spaces/{space_id}/properties/{property_id}/tags/{tag_id}",
    "createTag": "/v1/spaces/{space_id}/properties/{property_id}/tags",
    "updateTag": "/v1/spaces/{space_id}/properties/{property_id}/tags/{tag_id}",
    "deleteTag": "/v1/spaces/{space_id}/properties/{property_id}/tags/{tag_id}",
}

# Object URL patterns
OBJECT_URL_PATTERN = "anytype://objects/{objectId}@space/{spaceId}"
SPACE_URL_PATTERN = "anytype://space?spaceId={spaceId}"

# View Types
VIEW_TYPES = {
    "note": "note",
    "task": "task",
    "todo": "todo",
    "set": "set",
    "bookmark": "bookmark",
    "file": "file",
    "image": "image",
    "audio": "audio",
    "video": "video",
    "pdf": "pdf",
    "canvas": "canvas",
    "basic": "basic",
}

# Export Formats
EXPORT_FORMATS = {
    "markdown": "markdown",
    "html": "html",
    "pdf": "pdf",
}

# Sort Orders
SORT_ORDERS = {
    "created_date": "created_date",
    "last_modified_date": "last_modified_date",
    "last_opened_date": "last_opened_date",
    "name": "name",
    "type": "type",
}

# Member Roles
MEMBER_ROLES = {
    "owner": "owner",
    "admin": "admin",
    "member": "member",
    "viewer": "viewer",
}

# API Limits
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000
ICON_TIMEOUT = 5000  # milliseconds

# System Types
SYSTEM_TYPES = [
    "note",
    "task",
    "todo",
    "set",
    "bookmark",
    "file",
    "image",
    "audio",
    "video",
    "pdf",
    "canvas",
    "basic",
]
