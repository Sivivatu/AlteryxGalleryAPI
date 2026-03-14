"""
Authentication models for API.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TokenResponse(BaseModel):
    """OAuth2 token response from server.

    Attributes:
        access_token: The access token string
        token_type: Type of token (typically "Bearer")
        expires_in: Seconds until token expires
        scope: OAuth2 scope (optional)
    """

    access_token: str = Field(..., alias="access_token")
    token_type: str = Field("Bearer", alias="token_type")
    expires_in: int = Field(3600, alias="expires_in")
    scope: Optional[str] = Field(None, alias="scope")

    class Config:
        populate_by_name = True
