from fastapi import HTTPException, status

class ErroLLM(HTTPException):
    def __init__(self, detalhe: str):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detalhe)

class ErroEscritaArquivo(HTTPException):
    def __init__(self, detalhe: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detalhe)
