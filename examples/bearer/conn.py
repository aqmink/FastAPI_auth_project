from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db import UserDatabase, User, Base

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session = sessionmaker(autoflush=False, bind=engine, class_=AsyncSession)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield UserDatabase(User, session)
