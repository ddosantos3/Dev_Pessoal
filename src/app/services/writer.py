from __future__ import annotations
from typing import Iterable
from app.adapters.fs_client import FSClient

class Writer:
    def __init__(self, base_dir: str):
        self.fs = FSClient(base_dir)

    def escrever_pares(self, base_rel: str, pares: Iterable[tuple[str, str]], overwrite: bool) -> list[str]:
        escritos: list[str] = []
        for caminho_rel, conteudo in pares:
            full_rel = f"{base_rel}{caminho_rel}"
            escritos.append(self.fs.escrever(full_rel, conteudo, overwrite))
        return escritos
