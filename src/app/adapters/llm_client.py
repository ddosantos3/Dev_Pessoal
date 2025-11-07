from __future__ import annotations

import httpx

from app.core.errors import ErroLLM
from app.core.settings import settings


class LLMClient:
    """
    Cliente simples para OpenAI ou HuggingFace (inference API) no modo chat.
    """

    async def chat(self, mensagens: list[dict[str, str]]) -> str:
        prov = settings.llm_provider.lower()
        try:
            if prov == "openai":
                return await self._chat_openai(mensagens)
            if prov == "huggingface":
                return await self._chat_hf(mensagens)
        except httpx.HTTPError as exc:
            raise ErroLLM(f"Falha ao chamar provedor {prov}: {exc}") from exc
        except (KeyError, IndexError, TypeError) as exc:
            raise ErroLLM("Resposta inesperada do provedor LLM") from exc
        raise ValueError("LLM_PROVIDER inválido. Use 'openai' ou 'huggingface'.")

    async def _chat_openai(self, mensagens: list[dict[str, str]]) -> str:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.model_llm,
            "messages": mensagens,
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resposta = await client.post(url, headers=headers, json=payload)
            resposta.raise_for_status()
            data = resposta.json()
            return data["choices"][0]["message"]["content"]

    async def _chat_hf(self, mensagens: list[dict[str, str]]) -> str:
        if not settings.huggingface_api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY não configurada")
        role_map = {"system": "Sistema", "user": "Usuário", "assistant": "Assistente"}
        partes: list[str] = []
        for mensagem in mensagens:
            role = mensagem.get("role", "user")
            prefixo = role_map.get(role, role.capitalize())
            partes.append(f"{prefixo}: {mensagem.get('content', '')}")
        prompt = "\n\n".join(partes)
        url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 1500, "temperature": 0.2},
        }
        async with httpx.AsyncClient(timeout=240) as client:
            resposta = await client.post(url, headers=headers, json=payload)
            resposta.raise_for_status()
            data = resposta.json()
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"]
            if isinstance(data, dict) and data.get("generated_text"):
                return str(data["generated_text"])
            return str(data)
