from fastapi import APIRouter, HTTPException, status

from app.schemas.conversa import ConversaDetalhe, ConversaResumo
from app.services.conversas import ConversasService

router = APIRouter()
conversas_service = ConversasService()


@router.get("/conversas", response_model=list[ConversaResumo])
def listar_conversas() -> list[ConversaResumo]:
    return conversas_service.listar()


@router.get("/conversas/{conversa_id}", response_model=ConversaDetalhe)
def obter_conversa(conversa_id: str) -> ConversaDetalhe:
    try:
        return conversas_service.obter(conversa_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada",
        ) from exc


@router.delete("/conversas/{conversa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_conversa(conversa_id: str) -> None:
    try:
        conversas_service.remover(conversa_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada",
        ) from exc
