from fastapi import APIRouter

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("")
async def analyze_bonus():
    # TODO: accept text/image, locale in body, run AI analysis
    return {"status": "not_implemented"}
