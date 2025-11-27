from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from fastapi_auth.transport.base import BaseTransport


class BearerToken(BaseModel):
    access_token: str
    token_type: str


class BearerService(BaseTransport):
    scheme: OAuth2PasswordBearer

    def __init__(self, tokenUrl: str):
        self.scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl, auto_error=False)
    
    async def login_response(self, token: str):
        return BearerToken(access_token=token, token_type="bearer")

    async def logout_response(self):
        raise NotImplementedError()
