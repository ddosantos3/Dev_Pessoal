from __future__ import annotations
from pydantic import BaseModel, Field, field_validator


class RequisicaoGerar(BaseModel):
    objetivo: str = Field(..., description="Descrição do projeto a ser gerado")
    path_saida: str | None = Field(
        default=None,
        description="Diretório base de saída. Usa o padrão da aplicação quando omitido.",
    )
    overwrite: bool = Field(
        default=False, description="Permite sobrescrever arquivos já existentes"
    )
    git: bool = Field(default=False, description="Inicializa repositório Git e cria commit")

    @field_validator("objetivo")
    @classmethod
    def validar_objetivo(cls, value: str) -> str:
        texto = value.strip()
        if len(texto) < 5:
            raise ValueError("objetivo deve conter ao menos 5 caracteres")
        return texto

    @field_validator("path_saida")
    @classmethod
    def limpar_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        texto = value.strip()
        return texto or None


class RespostaGerar(BaseModel):
    plano: dict
    arquivos: list[str]
    commit: str | None = None
