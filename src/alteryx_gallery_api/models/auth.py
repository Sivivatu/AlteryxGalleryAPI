from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base import BaseApiModel


class TokenResponse(BaseApiModel):
    access_token: str = Field(..., alias="access_token")
    token_type: str = Field(..., alias="token_type")
    expires_in: int = Field(..., alias="expires_in")
    scope: Optional[str] = Field(default=None, alias="scope")
