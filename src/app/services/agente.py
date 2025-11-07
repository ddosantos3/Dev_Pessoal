from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Sequence

import typer

from app.adapters.git_client import GitClient
from app.adapters.llm_client import LLMClient
from app.core.settings import Settings
from app.services.planner import Planner
from app.services.prompt_base import PROMPT_BASE_SENIOR
from app.services.writer import Writer

LLMMessage = dict[str, str]

app_cli = typer.Typer()


class AgenteDev:
    """
    Orquestra o fluxo de conversa, planejamento e escrita dos arquivos.
    """

    def __init__(self, app_settings: Settings | None = None) -> None:
        self.settings = app_settings or Settings()

    async def conversar(self, mensagens: Sequence[LLMMessage], contexto: str | None) -> str:
        prompt: list[LLMMessage] = [{"role": "system", "content": PROMPT_BASE_SENIOR}]
        if contexto:
            prompt.append({"role": "system", "content": f"Contexto: {contexto}"})
        prompt.extend(mensagens)
        return await LLMClient().chat(prompt)

    async def gerar_projeto(
        self,
        objetivo: str,
        path_saida: str | None,
        overwrite: bool,
        git: bool,
    ):
        planner = Planner()
        plano = planner.planejar(objetivo)
        base_rel: str = plano["base"]
        if base_rel and not base_rel.endswith("/"):
            base_rel = f"{base_rel}/"

        arquivos = plano["arquivos"]
        prompt = self._montar_prompt_geracao(objetivo, arquivos, base_rel.rstrip("/"))
        resposta = await LLMClient().chat(prompt)

        pares, passos_execucao = self._extrair_arquivos(resposta)

        destino_root = Path(path_saida or self.settings.base_dir_saida).expanduser()
        writer = Writer(str(destino_root))
        escritos = writer.escrever_pares(base_rel, pares, overwrite=overwrite)

        commit_hash: str | None = None
        if git:
            repo_dir = destino_root / Path(base_rel)
            commit_hash = GitClient(str(repo_dir)).commit_tudo(
                f"feat: projeto gerado - {objetivo}"
            )

        if passos_execucao:
            plano["passos_execucao"] = passos_execucao
        plano["destino_absoluto"] = str((destino_root / Path(base_rel)).resolve())

        return plano, escritos, commit_hash

    def _montar_prompt_geracao(
        self,
        objetivo: str,
        arquivos: Sequence[str],
        base_rel: str,
    ) -> list[LLMMessage]:
        lista_arquivos = "\n".join(f"- {arquivo}" for arquivo in arquivos)
        destino = base_rel or "."
        user = (
            f"OBJETIVO: {objetivo}\n\n"
            f"Crie os seguintes ARQUIVOS dentro de '{destino}' (use blocos de código com o caminho como linguagem):\n"
            f"{lista_arquivos}\n\n"
            "Formato de resposta OBRIGATÓRIO para cada arquivo:\n"
            "```{caminho_do_arquivo}\n"
            "{CONTEUDO INTEGRAL}\n"
            "```\n"
            "Inclua também um bloco final com passos de execução (make run/test, docker) "
            "usando o arquivo PASSOS_EXECUCAO.md.\n"
        )
        return [
            {"role": "system", "content": PROMPT_BASE_SENIOR},
            {"role": "user", "content": user},
        ]

    def _extrair_arquivos(self, resposta: str) -> tuple[list[tuple[str, str]], str | None]:
        pares: list[tuple[str, str]] = []
        passos_execucao: str | None = None

        blocos = resposta.split("```")
        for indice in range(1, len(blocos), 2):
            bloco = blocos[indice].strip()
            if not bloco:
                continue

            primeira_linha, sep, restante = bloco.partition("\n")
            if not sep:
                continue

            caminho = primeira_linha.strip().strip("/")
            conteudo = restante.rstrip()
            if not caminho or not conteudo:
                continue

            if caminho.lower() in {"passos_execucao.md", "passos_execucao.txt"}:
                passos_execucao = conteudo

            pares.append((caminho, conteudo))

        return pares, passos_execucao


@app_cli.command("gerar")
def cli_gerar(
    objetivo: str = typer.Option(..., help="Descrição do que gerar"),
    path_saida: str | None = typer.Option(
        None,
        help="Diretório base onde o projeto será escrito (padrão definido nas configurações)",
    ),
    overwrite: bool = typer.Option(False, help="Permitir sobrescrever arquivos existentes"),
    git: bool = typer.Option(False, help="Efetuar commit automático após a escrita"),
) -> None:
    """
    Interface CLI que invoca o agente e imprime o resultado em JSON.
    """

    async def _run() -> None:
        agente = AgenteDev()
        plano, escritos, commit_hash = await agente.gerar_projeto(objetivo, path_saida, overwrite, git)
        print(
            json.dumps(
                {"plano": plano, "arquivos": escritos, "commit": commit_hash},
                ensure_ascii=False,
                indent=2,
            )
        )

    asyncio.run(_run())


if __name__ == "__main__":
    app_cli()
