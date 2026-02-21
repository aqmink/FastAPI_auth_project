from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse, Response

from fastapi_auth.token_storage.base import BaseStorage


class BearerStorage(BaseStorage):
    scheme: HTTPBearer
    scheme_name: str

    def __init__(self, scheme_name):
        self.scheme_name = scheme_name
        self.scheme = HTTPBearer(scheme_name=scheme_name, auto_error=False)

    async def login_response(
        self, 
        token: str,
        token_type: str,
        response: Response | None = None,
    ):
        return JSONResponse(
            content={
                "token_type": token_type,
                "token": token
            }
        )

    async def logout_response(self, response: Response):
        raise NotImplementedError()
