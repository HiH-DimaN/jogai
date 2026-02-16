from fastapi import APIRouter

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/start")
async def quiz_start():
    return {"status": "not_implemented"}


@router.post("/answer")
async def quiz_answer():
    return {"status": "not_implemented"}


@router.get("/result")
async def quiz_result():
    return {"status": "not_implemented"}
