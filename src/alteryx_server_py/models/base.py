"""
Base model for all API response models.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseApiModel(BaseModel):
    """Base model for API responses with strict validation.

    Features:
        - Strict mode: Reject unknown fields
        - Empty string to None coercion
        - Alias support for snake_case/camelCase conversion
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseApiModel":
        """Create model from dictionary, handling empty strings as None.

        Args:
            data: Dictionary of model data

        Returns:
            Instance of the model
        """
        cleaned = {}
        for key, value in data.items():
            if value == "":
                cleaned[key] = None
            else:
                cleaned[key] = value
        return cls.model_validate(cleaned)
