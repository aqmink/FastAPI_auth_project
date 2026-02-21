from typing import Literal
import secrets
from datetime import datetime, timedelta

from fastapi_auth.token_service.base import BaseTokenService
from fastapi_auth.token_service.db.models import TP
from fastapi_auth.token_service.db.base_token_db import BaseTokenDatabase
from fastapi_auth.db import BaseUserDatabase
from fastapi_auth import models


class TokenDatabaseService(BaseTokenService):
    def __init__(
        self,
        db: BaseTokenDatabase[TP],
        liftime_minutes: int,
    ):
        self.db = db
        self.lifetime_minutes = liftime_minutes

    async def read_token(
        self, 
        token: str, 
        user_service: BaseUserDatabase[models.UP, models.ID],
    ):
        token_model = await self.db.get(token)
        if not token_model:
            return None, None
        if datetime.now() > token_model.expires:
            return None, token_model.token_type
        return (
            await user_service.get(id=token_model.user_id), 
            token_model.token_type
        )
    
    async def write_token(
        self, 
        user: models.UP,
        token_type: Literal["access_token", "refresh_token"]
    ):
        token = secrets.token_urlsafe()
        try:
            await self.db.create(
                token=token,
                token_type=token_type,
                user_id=user.id,
                expires=datetime.now() + timedelta(minutes=self.lifetime_minutes)
            )
        except:
            await self.db.update(
                token=token,
                token_type=token_type,
                user_id=user.id,
                expires=datetime.now() + timedelta(minutes=self.lifetime_minutes)
            )
        return token
