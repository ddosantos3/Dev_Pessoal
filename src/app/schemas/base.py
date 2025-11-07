from __future__ import annotations
from pydantic import BaseModel

class PadraoResposta(BaseModel):
    status: str = "ok"
