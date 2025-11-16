from typing import Generic

from fastapi_auth.backend import Authentication
from fastapi_auth.auth import Authenticator
from fastapi_auth.db.base import BaseUserService
from fastapi_auth import models


class FastAPIAuth(Generic[models.UP, models.ID]):
    def __init__(
        self, 
        user_service: BaseUserService[models.UP, models.ID], 
        backend: Authentication[models.UP, models.ID],
    ):
        self.authenticator = Authenticator(backend, user_service)
        self.user_service = user_service
        self.current_user = self.authenticator.get_current_user
