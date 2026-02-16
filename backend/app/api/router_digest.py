from fastapi import APIRouter

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("")
async def get_digest():
    return {"status": "not_implemented"}
