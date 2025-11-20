from typing import Generic

from fastapi import Response, status, HTTPException

from fastapi_auth.transport.base import BaseTransport
from fastapi_auth.token_service.base import BaseTokenService
from fastapi_auth import models


class Authentication(Generic[models.UP, models.ID]):
    def __init__(self,
        transport: BaseTransport,
        get_token_service: BaseTokenService,
    ):
        self.transport = transport
        self.token_servce = get_token_service

    async def login(self, user: models.UP):
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return self.transport.login_response(
            await self.token_servce.write_token(user)
        )

    async def logout(self):
        try:
            return self.transport.logout_response()
        except:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        
