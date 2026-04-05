from typing import Generic, Annotated
from datetime import datetime

from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_auth import ID, TP, UP
from fastapi_auth import BaseUserDatabase, BaseTokenDatabase

from conn import async_session, sessionmaker, Base, get_session


class UserBase(Generic[ID]):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(index=True, unique=True, primary_key=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)


class TokenBase(Generic[TP]):
    __tablename__ = "Tokens"

    user_id: Mapped[int] = mapped_column(index=True, unique=True, primary_key=True)
    token: Mapped[str] = mapped_column()
    token_type: Mapped[str] = mapped_column()
    expires: Mapped[datetime] = mapped_column()


class Token(TokenBase, Base):
    pass


class User(UserBase, Base):
    pass


class TokenDatabase(BaseTokenDatabase[TP]):
    def __init__(self, async_session: sessionmaker = async_session):
        self.async_session = async_session
    
    async def execute(self, stmt, commit = True):
        async with self.async_session() as session:
            result = await session.execute(stmt)
            if commit:
                await session.commit()
        return result

    async def get(self, token):
        return (
            await self.execute(
                select(Token).filter_by(token=token), 
                commit=False,
            )
        ).scalars().first()
    
    async def create(self, **data):
        await self.execute(insert(Token).values(**data))

    async def update(self, token, **data):
        await self.execute(update(Token).values(token=token, **data))
    
    async def delete(self, token):
        await self.execute(delete(Token))


class UserDatabase(BaseUserDatabase[UP, ID]):
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

    async def create(self, *args, **data):
        await self.session.execute(
            insert(self.model).
            values(*args, **data)
        )
        await self.session.commit()

    async def update(self, user_id: int, *filter, **data):
        await self.session.execute(
            update(self.model).
            filter_by(id=user_id).
            values(**data)
        )
        await self.session.commit()
        return await self.get(id=user_id)

    async def delete(self, *filter, **params):
        await self.session.execute(
            delete(self.model).
            filter(*filter).
            filter_by(**params)
        )
        await self.session.commit()


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield UserDatabase(User, session)
