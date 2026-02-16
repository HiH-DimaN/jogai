from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram")
async def auth_telegram():
    # TODO: validate initData, return JWT
    return {"status": "not_implemented"}


@router.get("/me")
async def get_me():
    # TODO: return current user + locale
    return {"status": "not_implemented"}
