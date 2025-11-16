from typing import Protocol

from fastapi import Response
from fastapi.security.base import SecurityBase


class BaseTransport(Protocol):
    scheme: SecurityBase

    async def login_response(self, token: str) -> Response:
        ...
    
    async def logout_response(self) -> None:
        ...
