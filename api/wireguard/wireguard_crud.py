from api.db.database import async_engine, Base
from sqlalchemy import text
from datetime import datetime


async def add_wireguard_keys(user_id: int, private_key: str, public_key: str, client_ip: str, config: str, username: str | None = None):
    async with async_engine.connect() as conn:
        stmt = text("""INSERT INTO wireguard (user_id, username, private_key, public_key, client_ip, config, created_at)
            VALUES (:user_id, :username, :private_key, :public_key, :client_ip, :config, :created_at)""")
        await conn.execute(stmt, {"user_id": user_id,
            "username": username,
            "private_key": private_key,
            "public_key": public_key,
            "client_ip": client_ip,
            "config": config,
            "created_at": datetime.now()})
        await conn.commit()


async def get_wireguard_keys(user_id: int):
    async with async_engine.connect() as conn:
        stmt = text("SELECT * FROM wireguard WHERE user_id = :user_id")
        res = await conn.execute(stmt, {"user_id": user_id})
        return res.fetchone()


async def delete_wireguard_keys(user_id: int):
    async with async_engine.connect() as conn:
        stmt = text("SELECT public_key FROM wireguard WHERE user_id = :user_id")
        res = await conn.execute(stmt, {"user_id": user_id})
        public_key = res.scalar()
        if not public_key:
            raise ValueError(f"User {user_id} not found")
        delete_stmt = text("DELETE FROM wireguard WHERE user_id = :user_id")
        await conn.execute(delete_stmt, {"user_id": user_id})
        await conn.commit()
        return public_key

