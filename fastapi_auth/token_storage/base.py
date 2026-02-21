from typing import Protocol
from fastapi import Response

from fastapi_auth.schemas import AuthResponse
from fastapi.security.base import SecurityBase


class BaseStorage(Protocol):
    scheme: SecurityBase
    scheme_name: str

    async def login_response(
        self, 
        token: str,
        token_type: str,
        response: Response | None = None,
    ) -> Response: 
        ...
    
    async def logout_response(self, response: Response) -> Response:
        ...
