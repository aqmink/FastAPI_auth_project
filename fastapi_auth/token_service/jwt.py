from jose import jwt, JWTError
from fastapi import HTTPException, status

from .base import BaseTokenService
from fastapi_auth import models
from fastapi_auth.db.base import BaseUserService


class JWTService(BaseTokenService[models.ID, models.UP]):
    def __init__(
        self,
        secret: str = "secret",
        alorithm: str = "HS256",
        access_token_expires: int = 240,
        refresh_token_expires: int = 30,
        header_token_name: None | str = "Authorization",
        header_token_type: None | str = "bearer",
    ) -> None:
        self.secret = secret
        self.alorithm = alorithm
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires
        self.header_token_name = header_token_name
        self.header_token_type = header_token_type
    
    async def read_token(
        self, 
        token: str,
        user_service: BaseUserService[models.ID, models.UP],
    ) -> str:
        try:
            payload = jwt.decode(
                token=token,
                key=self.secret,
                algorithms=self.alorithm,
                options={"verify_exp": False}
            )
            return await user_service.get(int(payload.get("sub")))
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    async def write_token(self, user: models.UP) -> str:
        return jwt.encode(
            claims={"sub": str(user.id), "exp": self.access_token_expires},
            key=self.secret,
            algorithm=self.alorithm,
        )
