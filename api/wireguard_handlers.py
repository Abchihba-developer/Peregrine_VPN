import subprocess
from fastapi import APIRouter, HTTPException, Query, Path
from api.db.database import async_engine
from config import settings
from sqlalchemy import text
from api.wireguard.wireguard_crud import add_wireguard_keys, get_wireguard_keys, delete_wireguard_keys
from api.wireguard.wireguard_keys import generate_wireguard_keys, remove_wireguard_peer

wireguard_router = APIRouter(prefix="/wireguard", tags=["Wireguard"])


@wireguard_router.post("/generate_keys")
async def generate_keys(user_id: int = Query(..., description="Pass a unique user ID"),
                        username: str | None = Query(None, description="Username (optional)")):
    try:
        private_key, public_key = await generate_wireguard_keys()
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT client_ip FROM wireguard ORDER BY id DESC LIMIT 1"))
            last_ip = result.scalar()
            next_ip = 2 if not last_ip else int(last_ip.split('.')[-1].split('/')[0]) + 1
            client_ip = f"10.0.0.{next_ip}/32"
            config = f"""
            [Interface]
            PrivateKey = {private_key}
            Address = {client_ip}
            DNS = 8.8.8.8

            [Peer]
            PublicKey = {settings.serv.SERVER_PUBLIC_KEY}
            Endpoint = {settings.serv.SERVER_IP}:51820
            AllowedIPs = 0.0.0.0/0
            PersistentKeepalive = 25
            """.strip()
            await add_wireguard_keys(user_id=user_id,
                private_key=private_key,
                public_key=public_key,
                client_ip=client_ip,
                config=config,
                username=username)
            subprocess.run([
                "sudo", "wg", "set", "wg0",
                "peer", public_key,
                "allowed-ips", client_ip.split('/')[0]
            ], check=True)
            return {
                "user_id": user_id,
                "username": username,
                "private_key": private_key,
                "public_key": public_key,
                "client_ip": client_ip,
                "config": config
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500,
            detail=f"WireGuard operation failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@wireguard_router.get("/get_keys/{user_id}")
async def get_keys(user_id: int = Path(..., description="Unique user ID")):
    try:
        wireguard_data = await get_wireguard_keys(user_id)
        if not wireguard_data:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return {
            "user_id": wireguard_data["user_id"],
            "username": wireguard_data["username"],
            "client_ip": wireguard_data["client_ip"],
            "config": wireguard_data["config"],
            "created_at": wireguard_data["created_at"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting keys: {str(e)}")


@wireguard_router.delete("/delete_keys/{user_id}")
async def delete_keys(user_id: int = Path(..., description="Unique user ID")):
    try:
        public_key = await delete_wireguard_keys(user_id)
        await remove_wireguard_peer(public_key)
        return {
            "status": "success",
            "message": f"Access revoked for user {user_id}",
            "public_key": public_key}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


