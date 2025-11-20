from datetime import datetime
from typing import Protocol, TypeVar

from fastapi_auth import models


class TokenProtocol(Protocol):
    token: str
    user_id: models.ID
    expires: datetime


TP = TypeVar("TP", bound=TokenProtocol)
