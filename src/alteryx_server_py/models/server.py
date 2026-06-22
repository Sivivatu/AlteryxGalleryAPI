"""Server information models for API."""

from typing import Optional

from pydantic import Field

from .base import PermissiveApiModel


class ServerInfo(PermissiveApiModel):
    """Model for server information responses."""

    server_version: Optional[str] = Field(None, alias="serverVersion")
    base_address: Optional[str] = Field(None, alias="baseAddress")


class ServerSettings(PermissiveApiModel):
    """Model for server settings responses."""

    gallery_name: Optional[str] = Field(None, alias="galleryName")
    allow_api_access: Optional[bool] = Field(None, alias="allowApiAccess")
