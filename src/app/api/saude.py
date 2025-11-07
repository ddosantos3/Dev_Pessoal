from fastapi import APIRouter

router = APIRouter()

@router.get("/saude")
def saude():
    return {"ok": True}
