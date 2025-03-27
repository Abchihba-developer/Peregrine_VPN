from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


async_engine = create_async_engine(
    url=settings.db.get_db_url,
    echo=settings.db.echo)

async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
