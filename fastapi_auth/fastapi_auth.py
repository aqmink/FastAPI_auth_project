from typing import Generic, Sequence

from fastapi import Response, status, HTTPException

from fastapi_auth.types import DependencyCallable
from fastapi_auth.backend import Authentication
from fastapi_auth.auth import Authenticator
from fastapi_auth.db import BaseUserDatabase
from fastapi_auth import models
from fastapi_auth.utils import get_response_content, set_response_body


class FastAPIAuth(Generic[models.UP, models.ID]):
    def __init__(
        self, 
        get_user_service: DependencyCallable[
            BaseUserDatabase[models.UP, models.ID]
        ],
        backends: Sequence[Authentication[models.UP, models.ID]],
    ):
        self.get_user_service = get_user_service
        self.backends = backends
        self.auth = Authenticator(self.backends, get_user_service)
        self.current_user = self.auth.get_current_user
        self.current_token = self.auth.get_current_user_token

    async def login(
        self, 
        user: models.UP,
        user_service: BaseUserDatabase[models.UP, models.ID]
    ):
        await user_service.update(user.id, is_active=True)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return await self._get_token_pair(user)

    async def logout(self):
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        for backend in self.backends:
            try:
                response = await backend.logout(response)
            except:
                continue
        return response
    
    async def refresh(
        self,
        token: str,
        user_service: BaseUserDatabase[models.UP, models.ID]
    ):
        for backend in self.backends:
            user, token_type = await backend.token_service.read_token(
                token, user_service
            )
            if user and token_type != "refresh_token":
                user = None
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        user = await user_service.update(user.id, is_active=False)
        return await self._get_token_pair(user)
    
    async def _get_token_pair(self, user: models.UP):
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        token_pair = {}
        for backend in self.backends:
            response = await backend.login(user, response)
            data = get_response_content(response)
            if "token_type" in data.keys() and "token" in data.keys():
                token_pair[data["token_type"]] = data["token"]
                response.status_code = status.HTTP_200_OK
        if token_pair:
            response = set_response_body(response, token_pair)
        return response
