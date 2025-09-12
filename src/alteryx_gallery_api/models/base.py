from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, field_validator

class BaseApiModel(BaseModel):
    """
    Base for all API DTOs. Enforces strictness and predictable I/O.
    """
    model_config = ConfigDict(
        extra="forbid",            # reject unexpected fields
        populate_by_name=True,     # allow aliases
        frozen=False,
        str_strip_whitespace=True,
        str_min_length=0,
        from_attributes=False,     # set True if you deserialize from ORMs
        arbitrary_types_allowed=False,
    )

    @field_validator("*", mode="before")
    @classmethod
    def _coerce_empty_strings_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and v == "":
            return None
        return v

# test