from typing import Generic, Any

from fastapi_auth import models


class BaseUserDatabase(Generic[models.ID, models.UP]):
    async def get(self, id: models.ID) -> models.UP: 
        ...
    
    async def create(self, data: dict[str, Any]) -> models.UP: 
        ...
    
    async def update(self, user: models.UP, data: dict[str, Any]) -> models.UP: 
        ...

    async def delete(self, id: models.ID) -> None: 
        ...
