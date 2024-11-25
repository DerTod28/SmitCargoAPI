from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from cargoapi.core.config import get_db_url

DATABASE_URL = get_db_url()

async_engine = AsyncEngine(
    create_engine(
        url=DATABASE_URL,
        echo=True,
    ),
)


async def init_db() -> None:
    async with async_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:  # type:ignore[misc]
    Session = sessionmaker(  # type:ignore[call-overload]
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with Session() as session:
        yield session
