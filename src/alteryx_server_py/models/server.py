"""
Server information models for API.
"""

from pydantic import ConfigDict

from .base import BaseApiModel


class ServerInfo(BaseApiModel):
    """Model for server information responses."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )


class ServerSettings(BaseApiModel):
    """Model for server settings responses."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )
