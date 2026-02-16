from fastapi import APIRouter

router = APIRouter(prefix="/tracker", tags=["tracker"])


@router.get("/bets")
async def get_bets():
    return {"bets": []}


@router.post("/bets")
async def add_bet():
    return {"status": "not_implemented"}


@router.get("/stats")
async def get_stats():
    return {"status": "not_implemented"}
