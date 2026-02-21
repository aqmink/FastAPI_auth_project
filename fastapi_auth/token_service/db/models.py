from datetime import datetime
from typing import Protocol, TypeVar, Literal

from fastapi_auth import models


class TokenProtocol(Protocol):
    id: int
    token_type: Literal["access_token", "refresh_token"]
    token: str
    user_id: models.ID
    expires: datetime


TP = TypeVar("TP", bound=TokenProtocol)
