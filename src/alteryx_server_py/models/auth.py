"""
Authentication models for API.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    """OAuth2 token response from server.

    Attributes:
        access_token: The access token string
        token_type: Type of token (typically "Bearer")
        expires_in: Seconds until token expires
        scope: OAuth2 scope (optional)
    """

    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(..., alias="access_token")
    token_type: str = Field("Bearer", alias="token_type")
    expires_in: int = Field(3600, alias="expires_in")
    scope: Optional[str] = Field(None, alias="scope")
