from typing import Annotated

from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_auth import Authentication, FastAPIAuth
from fastapi_auth.token_service import JWTService
from fastapi_auth.transport import Cookie
from fastapi_auth.db.base import BaseUserService

from db import SQLService
from conn import get_user_db

app = FastAPI()

cookie_service = Cookie()
jwt_service = JWTService()


class UserService(BaseUserService):
    def __init__(
        self,
        sql_service: SQLService
    ):
        self.sql_service = sql_service
    
    async def get(self, id):
        return await self.sql_service.get(id)
    
    async def get_by_username(self, username):
        return await self.sql_service.get_by_username(username)
    
    async def create(self, data):
        return await self.sql_service.create(**data)
    
    async def update(self, user, data):
        return await self.sql_service.update(user, **data)
    
    async def delete(self, id):
        return await self.sql_service.delete(id)


class UserCreate(BaseModel):
    username: str
    password: str


async def get_user_service(user_db: Annotated[SQLService, Depends(get_user_db)]):
    yield UserService(user_db)


async def get_auth_service():
    return Authentication(
        transport=cookie_service,
        get_token_service=jwt_service
    )


fastapi_auth = FastAPIAuth(get_user_service, get_user_service())

current_user = fastapi_auth.current_user


@app.get("/me")
async def get_me(current_user = Depends(current_user)):
    return current_user


@app.post("/login")
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[Authentication, Depends(get_auth_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    await auth_service.login(
        await user_service.get_by_username(credentials.username)
    )


@app.post("/registration")
async def register(
    user_data: Annotated[UserCreate, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user_service.create(**user_data)
