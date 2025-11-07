from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

ROLE_MAP: dict[str, str] = {
    "usuario": "user",
    "agente": "assistant",
    "sistema": "system",
}


class MensagemChat(BaseModel):
    papel: Literal["usuario", "agente", "sistema"] = Field(
        default="usuario", description="Origem da mensagem dentro do chat"
    )
    conteudo: str = Field(..., description="Mensagem em texto simples")

    @field_validator("conteudo")
    @classmethod
    def validar_conteudo(cls, value: str) -> str:
        texto = value.strip()
        if not texto:
            raise ValueError("conteudo nao pode ser vazio")
        return texto

    def to_llm_payload(self) -> dict[str, str]:
        return {"role": ROLE_MAP[self.papel], "content": self.conteudo}


class RequisicaoChat(BaseModel):
    mensagens: list[MensagemChat]
    contexto: str | None = Field(
        default=None, description="Contexto adicional (tecnologias, restrições, etc.)"
    )
    conversa_id: str | None = Field(
        default=None, description="Identificador da conversa para histórico persistido"
    )

    @field_validator("mensagens")
    @classmethod
    def validar_mensagens(cls, value: list[MensagemChat]) -> list[MensagemChat]:
        if not value:
            raise ValueError("mensagens deve conter ao menos uma entrada")
        return value

    @field_validator("contexto")
    @classmethod
    def limpar_contexto(cls, value: str | None) -> str | None:
        if value is None:
            return None
        texto = value.strip()
        return texto if texto else None

    @field_validator("conversa_id")
    @classmethod
    def limpar_conversa_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        texto = value.strip()
        return texto if texto else None


class RespostaChat(BaseModel):
    resposta: str
    conversa_id: str
    arquivo: str
    contexto: str | None = None
    arquivos_salvos: list[str] = Field(default_factory=list)
    projeto_dir: str | None = None
