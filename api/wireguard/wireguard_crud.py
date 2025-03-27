from api.db.database import async_engine, Base
from api.wireguard.wireguard_keys import generate_wireguard_keys, remove_wireguard_peer
from sqlalchemy import text


async def add_wireguard_keys(user_id: int, username: str | None = None):
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM wireguard WHERE tg_id = :param1"), {"param1": user_id})
        if res.fetchone() is None:
            private_key, public_key = await generate_wireguard_keys()
            stmt = text("""INSERT INTO wireguard (tg_id, username, private_key, public_key)
                        VALUES (:param1, :param2, :param3, :param4)""")
            await conn.execute(stmt, {"param1": user_id, "param2": username, "param3": private_key, "param4": public_key})
            await conn.commit()
            return {"tg_id": user_id, "username": username, "private_key": private_key, "public_key": public_key}
        else:
            raise ValueError(f"Пользователь с ID = {user_id} уже существует")


async def get_wireguard_keys(user_id: int):
    async with async_engine.connect() as conn:
        stmt = text("SELECT private_key, public_key FROM wireguard WHERE tg_id = :param1")
        res = await conn.execute(stmt, {"param1": user_id})
        keys = res.fetchone()
        if not keys:
            raise ValueError(f"Пользователь с ID = {user_id} не найден")
        private_key, public_key = keys
        return private_key, public_key


async def delete_wireguard_keys(user_id: int):
    async with async_engine.connect() as conn:
        private_key, public_key = await get_wireguard_keys(user_id=user_id) # server
        await remove_wireguard_peer(public_key=public_key)

        stmt = text("DELETE FROM wireguard WHERE tg_id = :param1") # db
        res = await conn.execute(stmt, {"param1": user_id})
        await conn.commit()

        if res.rowcount == 0:
            raise ValueError(f"Пользователь с ID = {user_id} не найден")
    return {"message": f"Ключи для пользователя с ID {user_id} успешно удалены"}
