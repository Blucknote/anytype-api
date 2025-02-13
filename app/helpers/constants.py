"""API endpoint constants and configuration"""

# API Endpoints
ENDPOINTS = {
    # Object operations
    "createObject": "/spaces/{space_id}/objects",
    "deleteObject": "/spaces/{space_id}/objects/{object_id}",
    "getObject": "/spaces/{space_id}/objects/{object_id}",
    "getObjects": "/spaces/{space_id}/objects",
    "searchObjects": "/spaces/{space_id}/search",
    "globalSearch": "/search",
    "getExport": "/spaces/{space_id}/objects/{object_id}/export/{format}",
    # Space operations
    "createSpace": "/spaces",
    "getSpaces": "/spaces",
    "getMembers": "/spaces/{space_id}/members",
    # Type operations
    "getTypes": "/spaces/{space_id}/types",
    "getTemplates": "/spaces/{space_id}/types/{type_id}/templates",
    # Authentication
    "displayCode": "/auth/display_code?app_name={app_name}",
    "getToken": "/auth/token?challenge_id={challenge_id}&code={code}",
}

# Object URL patterns
OBJECT_URL_PATTERN = "anytype://object?objectId={objectId}&spaceId={spaceId}"
SPACE_URL_PATTERN = "anytype://space?spaceId={spaceId}"

# View Types
VIEW_TYPES = {
    "note": "note",
    "task": "task",
    "set": "set",
    "bookmark": "bookmark",
    "file": "file",
    "image": "image",
    "audio": "audio",
    "video": "video",
    "pdf": "pdf",
    "canvas": "canvas",
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
MAX_PAGE_SIZE = 100
ICON_TIMEOUT = 5000  # milliseconds

# System Types
SYSTEM_TYPES = [
    "note",
    "task",
    "set",
    "bookmark",
    "file",
    "image",
    "audio",
    "video",
    "pdf",
    "canvas",
]
