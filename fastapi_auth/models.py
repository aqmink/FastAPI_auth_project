from typing import Protocol, TypeVar


ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    id: ID
    username: str
    password: str
    is_active: bool
    is_superuser: bool


UP = TypeVar("UP", bound=UserProtocol)
