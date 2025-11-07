import re

def sanitize_filename(texto: str) -> str:
    """
    Sanitiza nome para uso como parte de caminho.
    """
    t = texto.lower().strip()
    t = re.sub(r"[^a-z0-9_\-]+", "-", t)
    t = re.sub(r"-{2,}", "-", t)
    return t.strip("-_")
