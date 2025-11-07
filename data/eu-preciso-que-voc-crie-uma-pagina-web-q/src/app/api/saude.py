from fastapi import APIRouter
from src.app.schemas.base import SaudeResponse

router = APIRouter()

@router.get("/saude", response_model=SaudeResponse)
def saude():
    """
    Endpoint de healthcheck da API.
    """
    return SaudeResponse(status="ok")