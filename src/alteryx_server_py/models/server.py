"""Server information models for API."""

from typing import Optional

from pydantic import ConfigDict, Field

from .base import BaseApiModel


class ServerInfo(BaseApiModel):
    """Model for server information responses."""

    model_config = ConfigDict(extra="allow")

    server_version: Optional[str] = Field(None, alias="serverVersion")
    base_address: Optional[str] = Field(None, alias="baseAddress")


class ServerSettings(BaseApiModel):
    """Model for server settings responses."""

    model_config = ConfigDict(extra="allow")

    gallery_name: Optional[str] = Field(None, alias="galleryName")
    allow_api_access: Optional[bool] = Field(None, alias="allowApiAccess")
