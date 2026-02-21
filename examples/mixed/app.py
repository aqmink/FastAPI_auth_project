from typing import Annotated

from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_auth import (
    Authentication, 
    FastAPIAuth, 
    JWTService, 
    TokenDatabaseService, 
    BearerStorage,
    CookieStorage,
)

from db import UserDatabase, TokenDatabase, get_user_db
from conn import create_db_and_tables

bearer_storage = BearerStorage("auth")
cookie_storage = CookieStorage("refresh")
jwt_service = JWTService(token_expires=30)
token_db_service = TokenDatabaseService(TokenDatabase(), liftime_minutes=1)

access_backend = Authentication(
    storage=bearer_storage,
    token_service=jwt_service,
)
refresh_backend = Authentication(
    storage=cookie_storage,
    token_service=token_db_service,
    token_type="refresh_token",
)

fastapi_auth = FastAPIAuth(
    get_user_db,
    [
        access_backend,
        refresh_backend,
    ],
)

current_user = fastapi_auth.current_user()
current_token = fastapi_auth.current_token()


class UserCreate(BaseModel):
    username: str
    password: str


async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, debug=True)


@app.post("/registration")
async def register(
    user_data: Annotated[UserCreate, Depends()],
    user_service: Annotated[UserDatabase, Depends(get_user_db)],
):
    await user_service.create(**user_data.model_dump())


@app.get("/me")
async def me(current_user = Depends(current_user)):
    return await current_user


@app.post("/login")
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserDatabase, Depends(get_user_db)],
):
    user = await user_service.get(username=credentials.username)
    if user and credentials.password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return await fastapi_auth.login(user)


@app.post("/logout")
async def logout():
    return await fastapi_auth.logout()


@app.post("/refresh")
async def refresh(
    refresh_token: Annotated[str, Depends(current_token)],
    user_service: Annotated[UserDatabase, Depends(get_user_db)],
):
    return await fastapi_auth.refresh(await refresh_token, user_service)
