from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.app.api.saude import router as saude_router
from src.app.core.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Barbearia - Landing Page de Agendamento",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(saude_router, prefix="/api")

# Servir arquivos estáticos (frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")