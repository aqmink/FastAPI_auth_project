from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth import UserProtocol


class Base(DeclarativeBase):
    pass


class User(Base, UserProtocol):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(index=True, unique=True, primary_key=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()


class SQLService:
    def __init__(self, model: Base, session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, *filter, **params):
        result = await self.session.execute(
            select(self.model).
            filter(*filter).
            filter_by(**params)
        )
        return result.scalars().first()
    
    async def get_by_username(self, username):
        return await self.get(username=username)

    async def get_all(
        self,
        *filter,
        limit: int = 0, 
        offset: int = 50, 
        **params
    ):
        result = await self.session.execute(
            select(self.model).
            filter(*filter).
            filter_by(**params).
            offset(offset).
            limit(limit)
        )
        return result.scalars().all()

    async def create(self, *args, **data):
        await self.session.execute(
            insert(self.model).
            values(*args, **data)
        )
        await self.session.commit()

    async def update(self, *filter, **data):
        await self.session.execute(
            update(self.model).
            filter(*filter).
            values(**data)
        )
        await self.session.commit()

    async def delete(self, *filter, **params):
        await self.session.execute(
            delete(self.model).
            filter(*filter).
            filter_by(**params)
        )
        await self.session.commit()
