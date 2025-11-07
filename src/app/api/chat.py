import json
import re
from pathlib import Path

from fastapi import APIRouter

from app.schemas.chat import RequisicaoChat, RespostaChat
from app.services.agente import AgenteDev
from app.services.conversas import ConversasService

router = APIRouter()
conversas_service = ConversasService()


def _slugify(value: str) -> str:
    texto = value.strip().lower()
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = re.sub(r"[\s_-]+", "-", texto)
    texto = texto.strip("-")
    return texto or "site"


@router.post("/chat", response_model=RespostaChat)
async def chat(req: RequisicaoChat) -> RespostaChat:
    """Conversa livre: ideação, refino e rascunhos de código."""
    agente = AgenteDev()
    mensagens = [mensagem.to_llm_payload() for mensagem in req.mensagens]
    resposta = await agente.conversar(mensagens, req.contexto)
    arquivos_payload: list[dict] = []
    slug_projeto: str | None = None
    mensagem_resumo = resposta.strip()

    try:
        payload = json.loads(resposta)
        if isinstance(payload, dict):
            mensagem_resumo = str(payload.get("mensagem") or "").strip() or mensagem_resumo
            arquivos_payload = payload.get("arquivos") or []
            if not isinstance(arquivos_payload, list):
                arquivos_payload = []
            slug_projeto = payload.get("slug_projeto") or payload.get("slug") or None
    except json.JSONDecodeError:
        payload = None

    if not mensagem_resumo:
        mensagem_resumo = "Estrutura criada com sucesso."

    registro = conversas_service.registrar(
        mensagens=req.mensagens,
        resposta_agente=mensagem_resumo,
        conversa_id=req.conversa_id,
        contexto=req.contexto,
    )

    arquivos_salvos: list[str] = []
    projeto_dir: Path | None = None

    if arquivos_payload:
        conversa_dir = Path(registro.arquivo).parent
        slug = _slugify(slug_projeto or mensagem_resumo.splitlines()[0])
        projeto_dir = conversa_dir / slug
        projeto_dir.mkdir(parents=True, exist_ok=True)

        for item in arquivos_payload:
            caminho_raw = item.get("caminho")
            conteudo = item.get("conteudo")
            if not isinstance(caminho_raw, str) or not caminho_raw.strip():
                continue
            if not isinstance(conteudo, str):
                continue
            caminho = Path(caminho_raw.strip())
            if caminho.is_absolute() or ".." in caminho.parts:
                continue
            destino = projeto_dir / caminho
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(conteudo, encoding="utf-8")
            arquivos_salvos.append(str(destino.resolve()))

    mensagem_final = mensagem_resumo
    if arquivos_salvos:
        lista = "\n".join(f"• {caminho}" for caminho in arquivos_salvos)
        blocos: list[str] = [f"✨ {mensagem_resumo}"]
        if projeto_dir:
            blocos.append(f"📁 Pasta do projeto: {projeto_dir}")
        blocos.append("🧩 Arquivos salvos:")
        blocos.append(lista)
        blocos.append("🚀 Pode abrir o index.html para validar e pedir ajustes quando quiser.")
        mensagem_final = "\n\n".join(blocos)
        conversas_service.atualizar_ultima_resposta(registro.id, mensagem_final)

    return RespostaChat(
        resposta=mensagem_final,
        conversa_id=registro.id,
        arquivo=registro.arquivo,
        contexto=registro.contexto,
        arquivos_salvos=arquivos_salvos,
        projeto_dir=str(projeto_dir.resolve()) if projeto_dir else None,
    )
