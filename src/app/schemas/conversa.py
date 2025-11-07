from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MensagemArmazenada(BaseModel):
    papel: Literal["usuario", "agente", "sistema"] = Field(..., description="Origem da mensagem")
    conteudo: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime | None = Field(
        default=None, description="Momento em que a mensagem foi registrada (UTC)"
    )


class ConversaResumo(BaseModel):
    id: str
    titulo: str
    contexto: str | None = None
    arquivo: str
    criado_em: datetime
    atualizado_em: datetime


class ConversaDetalhe(ConversaResumo):
    mensagens: list[MensagemArmazenada]
