from typing import Generic, Annotated

from fastapi import status, HTTPException, Depends

from fastapi_auth import models
from fastapi_auth.db.base import BaseUserService
from fastapi_auth.backend import Authentication


# class Authentication:
#     def __init__(
#         self, 
#         user_db: UserBaseManager,
#         token_db: TokenBaseManager,
#         base: CookieBasedAuth = CookieBasedAuth(),
#     ):
#         self.base = base
#         self.user_db = user_db
#         self.token_db = token_db

#     async def login(self, response: Response, username: str, password: str):
#         exception = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
#         try: 
#             user = await self.user_db.get_by_username(username)
#         except:
#             raise exception
#         if user.password != password:
#             raise exception
#         access_token = self.base.create_token(token_type="access", sub=user.id)
#         refresh_token = self.base.create_token(token_type="refresh", sub=user.id)
#         self.base.set_token(
#             token_type="access", 
#             response=response, 
#             token=access_token
#         )
#         self.base.set_token(
#             token_type="refresh", 
#             response=response,
#             token=refresh_token
#         )
#         try:
#             await self.token_db.create(
#                 user_id=user.id,
#                 token=refresh_token,
#                 created_at=datetime.now(),
#                 expires=self.base._config.refresh_token_expires,
#             )
#         except:
#             pass
#         return {status.HTTP_202_ACCEPTED: "Success!"}

#     async def logout(self, response: Response, request: Request, token: str):
#         token = request.cookies.get("refresh_token")
#         try:
#             await self.token_db.delete(token=token)
#         except:
#             {status.HTTP_401_UNAUTHORIZED: "soss"}
#         self.base.unset_token(response=response)
#         return {"msg": "you logged out"}

#     async def get_current_user(self, request: Request):
#         try:
#             token = request.cookies["access_token"]
#             user_id = self.base.decode_jwt(token)["sub"]
#             return await self.user_db.get(id=user_id)
#         except:
#             HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


# class Authentication:
#     def __init__(
#         self,
#         backend: AuthenticationBackend,
#         manager,
#     ):
#         self.backend = backend
    
#     async def authenticate(self, request, token_manager):
#         exception = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = self.manager.get(
#                 self.backend.strategy.decode_jwt(
#                     self.backend.strategy.get_access_token(request)
#                 )
#             )
#             await self.refresh(request, token_manager)
#         except:
#             raise exception
    
#     async def refresh(self, request, token_manager):
#         user = self.backend.strategy.decode_jwt(
#             self.backend.strategy.get_access_token(request)
#         )
#         refresh_session = token_manager.get(
#             self.backend.strategy.get_refresh_token(request)
#         )
#         if not refresh_session:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#         response = Response(status_code=status.HTTP_201_CREATED)
#         refresh_token = self.backend.strategy.create_token("refresh", user.id)
#         self.backend.strategy.set_token(
#             "access", 
#             self.backend.strategy.create_token("access", user.id),
#             response,
#         )
#         token_manager.update(refresh_token)
#         self.backend.strategy.set_token("refresh", refresh_token, response)
#         return response

#     def get_current_user(self):
#         return self.authenticate()


class Authenticator(Generic[models.ID, models.UP]):
    def __init__(
        self,
        backend: Authentication[models.UP, models.ID],
        get_user_service: BaseUserService[models.UP, models.ID], 
    ):
        self.backend = backend
        self.get_user_service = get_user_service

    def get_current_user(self):
        async def current_user_dependency(
            token: Annotated[str, Depends(self.backend.transport.scheme)],
            user_service: Annotated[BaseUserService, Depends(self.get_user_service)]
        ):
            return await self._authenticate(token, user_service)

        return current_user_dependency

    async def _authenticate(
        self, 
        token: str, 
        user_service: BaseUserService[models.UP, models.ID],
    ):
        user = await self.backend.token_servce.read_token(token, user_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user
