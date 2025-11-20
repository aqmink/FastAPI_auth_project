from typing import Literal

from fastapi import Response, status
from fastapi.security import APIKeyCookie

from fastapi_auth.transport.base import BaseTransport


class CookieService(BaseTransport):
    scheme: APIKeyCookie

    def __init__(
        self,
        cookie_name: str = "fastapiusersauth",
        cookie_max_age: int | None = None,
        cookie_path: str = "/",
        cookie_domain: str | None = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.scheme = APIKeyCookie(name=self.cookie_name)
    
    def login_response(self, token: str) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self._set_cookie(response, token)
    
    def logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self._delete_cookie(response)
    
    def _set_cookie(self, response: Response, token: str) -> Response:
        response.set_cookie(
            self.cookie_name,
            token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response
    
    def _delete_cookie(self, response: Response) -> Response:
        response.set_cookie(
            self.cookie_name,
            "",
            max_age=0,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response
