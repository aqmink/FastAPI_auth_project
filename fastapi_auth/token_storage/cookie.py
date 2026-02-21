from typing import Literal

from fastapi import Response, status
from fastapi.security import APIKeyCookie

from fastapi_auth.token_storage.base import BaseStorage


class CookieStorage(BaseStorage):
    scheme_name: str
    scheme: APIKeyCookie

    def __init__(
        self,
        scheme_name: str,
        cookie_max_age: int | None = None,
        cookie_path: str = "/",
        cookie_domain: str | None = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.scheme_name = scheme_name
        self.scheme = APIKeyCookie(
            name=scheme_name, 
            scheme_name=scheme_name,
            auto_error=False
        )

    async def login_response(
        self, 
        token: str,
        token_type: str,
        response: Response | None = None,
    ):
        if not response:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)
        self._set_cookie(response, token)
        return response
    
    async def logout_response(self, response):
        return self._delete_cookie(response)
    
    def _set_cookie(
        self, 
        response: Response, 
        token: str,
    ) -> Response:
        response.set_cookie(
            key=self.scheme_name,
            value=token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response
    
    def _delete_cookie(self, response: Response) -> Response:
        response.delete_cookie(
            key=self.scheme_name,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response
