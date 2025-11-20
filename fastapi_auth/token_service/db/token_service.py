import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status

from fastapi_auth.token_service.base import BaseTokenService
from fastapi_auth.token_service.db.models import TP
from fastapi_auth.token_service.db.base_token_db import BaseTokenDB
from fastapi_auth.db import BaseUserService
from fastapi_auth import models


class TokenService(BaseTokenService):
    def __init__(
        self,
        db: BaseTokenDB[TP],
        liftime_minutes: int,
    ):
        self.db = db
        self.lifetime_minutes = liftime_minutes
    
    async def read_token(
        self, 
        token: str, 
        user_service: BaseUserService[models.UP, models.ID],
    ):
        token_model = await self.db.get(token)
        if datetime.now() > token_model.expires:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        await user_service.get(token_model.user_id)
    
    async def write_token(self, user: models.UP):
        return await self.db.create(
            token=secrets.token_urlsafe(),
            user_id=user.id,
            expires=datetime.now() + timedelta(minutes=self.lifetime_minutes)
        )
