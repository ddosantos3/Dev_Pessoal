from __future__ import annotations
from app.utils.text import sanitize_filename

class Planner:
    """
    Constrói um plano mínimo: árvore + lista de arquivos com caminhos relativos.
    O conteúdo será pedido ao LLM.
    """

    def planejar(self, objetivo: str) -> dict:
        # Simples plano baseado em objetivo; você pode enriquecer com heurísticas
        nome_slug = sanitize_filename(objetivo)[:40] or "projeto"
        base = f"{nome_slug}/"
        arquivos = [
            "README.md",
            "pyproject.toml",
            "requirements.txt",
            "Makefile",
            "Dockerfile",
            "docker-compose.yml",
            "src/app/main.py",
            "src/app/api/saude.py",
            "src/app/core/settings.py",
            "src/app/core/logging_config.py",
            "src/app/core/errors.py",
            "src/app/schemas/base.py",
            "src/app/services/modulo.py",
            "tests/test_saude.py",
        ]
        return {"base": base, "arquivos": arquivos}
