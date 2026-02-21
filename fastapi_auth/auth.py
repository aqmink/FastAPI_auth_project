from typing import Generic, Annotated, Sequence
from fastapi import status, HTTPException, Depends

from fastapi_auth.utils import _with_new_signature
from fastapi_auth.types import DependencyCallable
from fastapi_auth import models
from fastapi_auth.db.base import BaseUserDatabase
from fastapi_auth.backend import Authentication


class Authenticator(Generic[models.ID, models.UP]):
    def __init__(
        self,
        backends: Sequence[Authentication[models.UP, models.ID]],
        get_user_service: DependencyCallable[BaseUserDatabase[models.UP, models.ID]], 
    ):
        self.backends = backends
        self.get_user_service = get_user_service
    
    def get_current_user_token(self):
        @_with_new_signature(
            **{
                backend.storage.scheme_name: 
                    Depends(backend.storage.scheme) for backend in self.backends
            }
        )
        async def current_user_token_dependency(
            user_service: Annotated[
                BaseUserDatabase[models.UP, models.ID], 
                Depends(self.get_user_service)
            ],
            **kwargs,
        ):
            token, _ = await self._authenticate(
                user_service=user_service,
                **kwargs,
            )
            return token
        
        return current_user_token_dependency
            
    def get_current_user(self):
        @_with_new_signature(
            **{
                backend.storage.scheme_name: 
                    Depends(backend.storage.scheme) for backend in self.backends
            }
        )
        async def current_user_dependency(
            user_service: Annotated[
                BaseUserDatabase[models.UP, models.ID], 
                Depends(self.get_user_service),
            ],
            **kwargs,
        ): 
            _, user = await self._authenticate(
                user_service=user_service,
                **kwargs,
            )
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return user

        return current_user_dependency

    async def _authenticate(
        self,
        user_service: BaseUserDatabase[models.UP, models.ID],
        *args,
        **kwargs,
    ):  
        for backend in self.backends:
            try:
                token = kwargs[backend.storage.scheme_name]
            except KeyError:
                return None, None
            if not token:
                return None, None
            if not isinstance(token, str):
                token = token.credentials
            user = await self._check_token_type(
                backend=backend,
                user_service=user_service,
                token=token,
            )
            if user:
                break
        return token, user

    async def _check_token_type(
        self,
        backend: Authentication[models.UP, models.ID],
        user_service: BaseUserDatabase[models.UP, models.ID],
        token: str,
    ):
        user, token_type = await backend.token_service.read_token(
            token, user_service
        )
        if token_type != "access_token":
            return
        if user:
            return user
        return
