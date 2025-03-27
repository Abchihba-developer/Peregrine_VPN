from fastapi import APIRouter, HTTPException, Query, Path
from api.wireguard.wireguard_crud import add_wireguard_keys, get_wireguard_keys, delete_wireguard_keys

wireguard_router = APIRouter(prefix="/wireguard", tags=["Wireguard"])


@wireguard_router.post("/generate_keys")
async def generate_keys(user_id: int = Query(..., description="Pass a unique user ID"),
                        username: str | None = Query(None, description="Username (optional)")):
    try:
        res = await add_wireguard_keys(user_id, username)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wireguard_router.get("/get_keys/{user_id}")
async def get_keys(user_id: int = Path(..., description="Unique user ID")):
    try:
        private_key, public_key = await get_wireguard_keys(user_id)
        return private_key, public_key
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@wireguard_router.delete("/delete_keys/{user_id}")
async def delete_keys(user_id: int = Path(..., description="Unique user ID")):
    try:
        res = await delete_wireguard_keys(user_id)
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


