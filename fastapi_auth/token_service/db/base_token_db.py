from typing import Protocol, Generic, Any

from fastapi_auth.token_service.db import models


class BaseTokenDB(Protocol, Generic[models.TP]):
    async def get(self, token: str) -> models.TP | None: 
        ...
    
    async def create(self, data: dict[str, Any]) -> models.TP: 
        ...
    
    async def update(self, token: models.TP, data: dict[str, Any]) -> models.TP:
        ...

    async def delete(self, id: models.TP) -> None: 
        ...
