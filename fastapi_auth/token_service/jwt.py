from typing import Literal
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from .base import BaseTokenService
from fastapi_auth import models
from fastapi_auth.db.base import BaseUserDatabase


class JWTService(BaseTokenService[models.ID, models.UP]):
    def __init__(
        self,
        secret: str = "secret",
        alorithm: str = "HS256",
        token_expires: int = 240,
    ) -> None:
        self.secret = secret
        self.alorithm = alorithm
        self.token_expires = token_expires
    
    async def read_token(
        self, 
        token: str,
        user_service: BaseUserDatabase[models.ID, models.UP],
    ) -> models.UP | None: 
        return_value = (None, None)
        if not token:
            return return_value
        try:
            payload = jwt.decode(
                token=token,
                key=self.secret,
                algorithms=self.alorithm,
            )
            return_value = (
                await user_service.get(id=int(payload.get("sub"))), 
                payload.get("type")
            )
        except JWTError:
            return return_value
        return return_value
    
    async def write_token(
        self, 
        user: models.UP, 
        token_type: Literal["access_token", "refresh_token"]
    ) -> str:
        return jwt.encode(
            claims={
                "sub": str(user.id), 
                "exp": datetime.now(timezone.utc) + timedelta(seconds=self.token_expires),
                "type": token_type
            },
            key=self.secret,
            algorithm=self.alorithm,
        )
