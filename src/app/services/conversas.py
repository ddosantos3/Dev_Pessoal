from __future__ import annotations

import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from app.core.settings import settings
from app.schemas.chat import MensagemChat
from app.schemas.conversa import ConversaDetalhe, ConversaResumo, MensagemArmazenada


class ConversasService:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.base_dir_conversas).expanduser().resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def listar(self) -> list[ConversaResumo]:
        conversas: list[ConversaResumo] = []
        for pasta in sorted(self.base_dir.iterdir()):
            if not pasta.is_dir():
                continue
            json_path = pasta / f"{pasta.name}.json"
            if not json_path.exists():
                continue
            try:
                with json_path.open("r", encoding="utf-8") as arquivo:
                    dados = json.load(arquivo)
                conversas.append(self._converter_resumo(dados, json_path))
            except Exception:
                continue
        conversas.sort(key=lambda c: c.atualizado_em, reverse=True)
        return conversas

    def obter(self, conversa_id: str) -> ConversaDetalhe:
        json_path = self._resolver_json_path(conversa_id)
        if not json_path.exists():
            raise FileNotFoundError(f"Conversa '{conversa_id}' não encontrada")
        with json_path.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return self._converter_detalhe(dados, json_path)

    def registrar(
        self,
        mensagens: Sequence[MensagemChat],
        resposta_agente: str,
        conversa_id: str | None = None,
        contexto: str | None = None,
    ) -> ConversaDetalhe:
        agora = datetime.now(timezone.utc)

        titulo = self._definir_titulo(contexto, mensagens)
        contexto_limpo = self._limpar_contexto(contexto)
        dados_existentes: dict | None = None
        mensagens_existentes: list[dict] = []

        if conversa_id:
            json_path = self._resolver_json_path(conversa_id)
            if not json_path.exists():
                # caso o arquivo tenha sido removido manualmente, trata como novo
                conversa_id, json_path = self._criar_novos_paths(contexto_limpo or titulo, agora)
                criado_em = agora
            else:
                with json_path.open("r", encoding="utf-8") as arquivo:
                    dados_existentes = json.load(arquivo)
                criado_em = self._parse_datetime(dados_existentes.get("criado_em")) or agora
                mensagens_existentes = dados_existentes.get("mensagens", []) or []
                if contexto_limpo is None:
                    contexto_limpo = self._limpar_contexto(dados_existentes.get("contexto"))
                if dados_existentes.get("titulo") and not self._limpar_contexto(contexto):
                    titulo = dados_existentes["titulo"]
        else:
            conversa_id, json_path = self._criar_novos_paths(
                contexto_limpo or titulo,
                agora,
            )
            criado_em = agora

        mensagens_salvas: list[MensagemArmazenada] = []
        for indice, mensagem in enumerate(mensagens):
            timestamp_existente: datetime | None = None
            if mensagens_existentes:
                try:
                    timestamp_existente = self._parse_datetime(
                        mensagens_existentes[indice].get("timestamp")
                    )
                except (IndexError, AttributeError):
                    timestamp_existente = None
            mensagens_salvas.append(
                MensagemArmazenada(
                    papel=mensagem.papel,
                    conteudo=mensagem.conteudo,
                    timestamp=timestamp_existente,
                )
            )

        mensagens_salvas.append(
            MensagemArmazenada(
                papel="agente",
                conteudo=resposta_agente,
                timestamp=agora,
            )
        )

        contexto_final = contexto_limpo or titulo

        dados = {
            "id": conversa_id,
            "titulo": titulo,
            "contexto": contexto_final,
            "arquivo": str(json_path.resolve()),
            "criado_em": criado_em.isoformat(),
            "atualizado_em": agora.isoformat(),
            "mensagens": [mensagem.model_dump(mode="json") for mensagem in mensagens_salvas],
        }

        json_path.parent.mkdir(parents=True, exist_ok=True)
        with json_path.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

        return self._converter_detalhe(dados, json_path)

    def atualizar_ultima_resposta(self, conversa_id: str, conteudo: str) -> None:
        json_path = self._resolver_json_path(conversa_id)
        if not json_path.exists():
            return
        with json_path.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        mensagens: list[dict] = dados.get("mensagens", [])
        for mensagem in reversed(mensagens):
            if mensagem.get("papel") == "agente":
                mensagem["conteudo"] = conteudo
                mensagem["timestamp"] = datetime.now(timezone.utc).isoformat()
                break
        dados["mensagens"] = mensagens
        dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
        with json_path.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    def remover(self, conversa_id: str) -> None:
        pasta = self.base_dir / conversa_id
        if not pasta.exists():
            raise FileNotFoundError(f"Conversa '{conversa_id}' não encontrada")
        if not pasta.is_dir():
            pasta.unlink()
            return
        shutil.rmtree(pasta)

    def _converter_resumo(self, dados: dict, json_path: Path) -> ConversaResumo:
        return ConversaResumo(
            id=dados["id"],
            titulo=dados.get("titulo") or dados["id"],
            contexto=dados.get("contexto"),
            arquivo=dados.get("arquivo", str(json_path.resolve())),
            criado_em=self._parse_datetime(dados.get("criado_em")) or datetime.now(timezone.utc),
            atualizado_em=self._parse_datetime(dados.get("atualizado_em")) or datetime.now(timezone.utc),
        )

    def _converter_detalhe(self, dados: dict, json_path: Path) -> ConversaDetalhe:
        mensagens = [
            MensagemArmazenada.model_validate(mensagem) for mensagem in dados.get("mensagens", [])
        ]
        return ConversaDetalhe(
            id=dados["id"],
            titulo=dados.get("titulo") or dados["id"],
            contexto=dados.get("contexto"),
            arquivo=dados.get("arquivo", str(json_path.resolve())),
            criado_em=self._parse_datetime(dados.get("criado_em")) or datetime.now(timezone.utc),
            atualizado_em=self._parse_datetime(dados.get("atualizado_em")) or datetime.now(timezone.utc),
            mensagens=mensagens,
        )

    def _resolver_json_path(self, conversa_id: str) -> Path:
        pasta = self.base_dir / conversa_id
        return pasta / f"{pasta.name}.json"

    def _criar_novos_paths(self, contexto: str, agora: datetime) -> tuple[str, Path]:
        slug_base = self._slugify(contexto)
        timestamp = agora.strftime("%Y%m%d_%H%M%S")
        conversa_id = f"{slug_base}-{timestamp}"
        pasta = self.base_dir / conversa_id
        if pasta.exists():
            sufixo = uuid.uuid4().hex[:8]
            conversa_id = f"{slug_base}-{timestamp}-{sufixo}"
            pasta = self.base_dir / conversa_id
        return conversa_id, pasta / f"{conversa_id}.json"

    def _slugify(self, texto: str) -> str:
        texto_limpo = texto.strip().lower()
        texto_limpo = re.sub(r"[^\w\s-]", "", texto_limpo, flags=re.UNICODE)
        texto_limpo = re.sub(r"[\s_-]+", "-", texto_limpo)
        texto_limpo = texto_limpo.strip("-")
        return texto_limpo or "conversa"

    def _limpar_contexto(self, contexto: str | None) -> str | None:
        if contexto is None:
            return None
        texto = contexto.strip()
        return texto or None

    def _definir_titulo(self, contexto: str | None, mensagens: Sequence[MensagemChat]) -> str:
        contexto_limpo = self._limpar_contexto(contexto)
        if contexto_limpo:
            return self._formatar_titulo(contexto_limpo)

        tema = self._inferir_tema(mensagens)
        if tema:
            return tema

        for mensagem in mensagens:
            if mensagem.papel == "usuario":
                return self._formatar_titulo(mensagem.conteudo)
        return "Nova conversa"

    def _parse_datetime(self, valor: str | None) -> datetime | None:
        if not valor:
            return None
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None

    def _inferir_tema(self, mensagens: Sequence[MensagemChat]) -> str | None:
        temas = [
            ("dashboard", "Dashboard personalizado"),
            ("landing page", "Landing page sob medida"),
            ("landing-page", "Landing page sob medida"),
            ("site", "Site institucional"),
            ("portfólio", "Portfólio digital"),
            ("portfolio", "Portfólio digital"),
            ("ecommerce", "Loja virtual"),
            ("loja", "Loja online"),
            ("blog", "Blog moderno"),
            ("formulário", "Formulário interativo"),
        ]
        for mensagem in mensagens:
            if mensagem.papel != "usuario":
                continue
            texto = mensagem.conteudo.lower()
            for palavra, titulo in temas:
                if palavra in texto:
                    return titulo
        return None

    def _formatar_titulo(self, texto: str) -> str:
        if not texto:
            return "Nova conversa"
        primeira_linha = texto.strip().splitlines()[0]
        primeira_frase = primeira_linha.split(".")[0]
        palavras = primeira_frase.split()
        resumo = " ".join(palavras[:12])
        if len(palavras) > 12:
            resumo += "..."
        resumo = resumo.strip()
        return resumo[:80].capitalize() if resumo else "Nova conversa"
