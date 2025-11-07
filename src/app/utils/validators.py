def nao_vazio(valor: str, campo: str) -> None:
    if not valor or not valor.strip():
        raise ValueError(f"{campo} não pode ser vazio")
