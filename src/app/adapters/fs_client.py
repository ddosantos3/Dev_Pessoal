from __future__ import annotations
from pathlib import Path
from app.core.errors import ErroEscritaArquivo


class FSClient:
    def __init__(self, base: str):
        self.base = Path(base).resolve()

    def caminho(self, rel: str) -> Path:
        destino = self.base.joinpath(rel).resolve()
        if not destino.is_relative_to(self.base):
            raise ErroEscritaArquivo("Caminho inválido (path traversal detectado).")
        return destino

    def escrever(self, rel_path: str, conteudo: str, overwrite: bool = False) -> str:
        destino = self.caminho(rel_path)
        destino.parent.mkdir(parents=True, exist_ok=True)

        if destino.exists() and not overwrite:
            raise ErroEscritaArquivo(f"Arquivo já existe: {rel_path}")

        destino.write_text(conteudo, encoding="utf-8")
        return str(destino)
