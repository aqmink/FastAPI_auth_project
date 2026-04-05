from typing import Generic, Literal

from fastapi import Response, status

from fastapi_auth.token_storage.base import BaseStorage
from fastapi_auth.token_service.base import BaseTokenService
from fastapi_auth import models


class Authentication(Generic[models.UP, models.ID]):
    def __init__(
        self,
        storage: BaseStorage,
        token_service: BaseTokenService[models.UP, models.ID],
        token_type: Literal["access_token", "refresh_token"] = "access_token",
    ):
        self.token_type = token_type
        self.storage = storage
        self.token_service = token_service
    
    async def login(
        self, 
        user: models.UP, 
        response: Response | None = None,
    ):
        if not user:
            return
        return await self.storage.login_response(
            token=await self.token_service.write_token(user, self.token_type),
            token_type=self.token_type,
            response=response,
        )

    async def logout(self, response):
        try:
            return await self.storage.logout_response(response)
        except:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
