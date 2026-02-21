from typing import Annotated

from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_auth import Authentication, FastAPIAuth, JWTService, BearerStorage

from db import UserDatabase, User
from conn import get_user_db, create_db_and_tables


async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


class UserCreate(BaseModel):
    username: str
    password: str


bearer_storage = BearerStorage("auth")
jwt_service = JWTService()

access_token_backend = Authentication(
    storage=bearer_storage,
    token_service=jwt_service,
)
refresh_token_backend = Authentication(
    storage=bearer_storage,
    token_service=jwt_service,
    token_type="refresh_token"
)

fastapi_auth = FastAPIAuth(
    get_user_db, 
    [
        access_token_backend,
        refresh_token_backend,
    ]
)

current_user = fastapi_auth.current_user()
current_token = fastapi_auth.current_token()

app = FastAPI(lifespan=lifespan, debug=True)


@app.get("/me")
async def get_me(current_user: Annotated[User, Depends(current_user)]):
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


@app.post("/registration")
async def register(
    user_data: Annotated[UserCreate, Depends()],
    user_service: Annotated[UserDatabase, Depends(get_user_db)],
):
    await user_service.create(**user_data.model_dump())


@app.post("/logout")
async def logout():
    return await fastapi_auth.logout()


@app.post("/refresh")
async def refresh(
    refresh_token: Annotated[str, Depends(current_token)],
    user_service: Annotated[UserDatabase, Depends(get_user_db)],
):
    return await fastapi_auth.refresh(await refresh_token, user_service)
