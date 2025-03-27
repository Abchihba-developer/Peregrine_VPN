import asyncio
import uvicorn
from fastapi import FastAPI
from config import settings
from api.wireguard_handlers import wireguard_router
from api.db.database import async_engine, Base
from api.db.models import Wireguard # Нужно для нормального функционирования metadata в Base

app = FastAPI(root_path="/api")
app.include_router(wireguard_router)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Database table created!!!")


if __name__ == "__main__":
    asyncio.run(init_db())
    uvicorn.run(app="run:app", host=settings.run.host, port=settings.run.port)
