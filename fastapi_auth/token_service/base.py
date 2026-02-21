from typing import Protocol, Generic, Literal

from fastapi_auth import models
from fastapi_auth.db.base import BaseUserDatabase


class BaseTokenService(Protocol, Generic[models.ID, models.UP]):
    async def read_token(
        self, 
        token: str, 
        user_service: BaseUserDatabase[models.UP, models.ID]
    ) -> models.UP | None:
        ...
    
    async def write_token(
        self, 
        user: models.UP,
        token_type: Literal["access_token", "refresh_token"],
    ) -> str:
        ...
