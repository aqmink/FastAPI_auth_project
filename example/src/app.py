from typing import Annotated

from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_auth import Authentication, FastAPIAuth, JWTService, CookieService
from fastapi_auth.db.base import BaseUserService

from db import SQLService, User
from conn import get_user_db, create_db_and_tables


async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


class UserService(BaseUserService):
    def __init__(
        self,
        sql_service: SQLService
    ):
        self.sql_service = sql_service

    async def get(self, id) -> User:
        return await self.sql_service.get(id=id)

    async def get_by_username(self, username) -> User:
        return await self.sql_service.get(username=username)

    async def create(self, **data):
        return await self.sql_service.create(**data)

    async def update(self, user, **data):
        return await self.sql_service.update(user, **data)

    async def delete(self, id):
        return await self.sql_service.delete(id=id)


class UserCreate(BaseModel):
    username: str
    password: str


async def get_user_service(user_db: Annotated[SQLService, Depends(get_user_db)]):
    yield UserService(user_db)


cookie_service = CookieService()
jwt_service = JWTService()

backend = Authentication(
    transport=cookie_service,
    get_token_service=jwt_service
)

app = FastAPI(lifespan=lifespan)

fastapi_auth = FastAPIAuth(get_user_service, backend)

current_user = fastapi_auth.current_user()


@app.get("/me")
async def get_me(current_user = Depends(current_user)):
    return current_user


@app.post("/login")
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_by_username(credentials.username)
    if user and credentials.password != user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return await fastapi_auth.login(user)


@app.post("/registration")
async def register(
    user_data: Annotated[UserCreate, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    await user_service.create(**user_data.model_dump())


@app.post("/logout")
async def logout():
    return await fastapi_auth.logout()
