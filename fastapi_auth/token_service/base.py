from typing import Protocol, Generic

from fastapi_auth import models
from fastapi_auth.db.base import BaseUserService


class BaseTokenService(Protocol, Generic[models.ID, models.UP]):
    async def read_token(
        self, 
        token: str, 
        user_service: BaseUserService
    ) -> models.UP | None:
        ...
    
    async def write_token(self, user: models.UP) -> str:
        ...
