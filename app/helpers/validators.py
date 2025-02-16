"""Validation utilities"""

from typing import Any, Dict, List, Optional, Set

from fastapi import HTTPException


class TypeValidator:
    """Validator for Anytype object types"""

    def __init__(self):
        self._valid_types: Optional[Set[str]] = None
        self._space_types: Dict[str, Set[str]] = {}

    async def validate_types(
        self,
        types: Optional[List[str]],
        space_id: Optional[str],
        client: Any,
        token: str,
    ) -> Optional[List[str]]:
        """Validate a list of types against available types in Anytype

        Args:
            types: List of types to validate
            space_id: Optional space ID to validate against space-specific types
            client: AnytypeClient instance
            token: Authentication token

        Returns:
            Validated list of types or None if no types provided

        Raises:
            HTTPException: If any type is invalid or if types cannot be fetched
        """
        if not types:
            return None

        # Get valid types for the space if not cached
        cache_key = space_id or "global"
        if cache_key not in self._space_types:
            try:
                type_list = await client.get_types(
                    space_id=space_id, include_system=True, token=token
                )
                if not type_list:
                    # If no types are returned, don't validate
                    # This handles the case where the space might be new or empty
                    return types
                self._space_types[cache_key] = {t.id for t in type_list}
            except Exception as e:
                error_msg = str(e)
                # Handle both raw error message and wrapped APIError message format
                if (
                    "type not found" in error_msg.lower()
                    or "'message': 'type not found'" in error_msg
                ):
                    # If types can't be fetched, don't validate
                    # This handles the case where the space might not support type listing
                    return types
                # Re-raise the original error to preserve the error chain
                raise

        valid_types = self._space_types[cache_key]
        invalid_types = [t for t in types if t not in valid_types]

        if invalid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type(s): {', '.join(invalid_types)}. Valid types are: {', '.join(sorted(valid_types))}",
            )

        return types
