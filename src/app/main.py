from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.conversas import router as conversas_router
from app.api.gerar import router as gerar_router
from app.api.saude import router as saude_router
from app.core.logging_config import configurar_logging

configurar_logging()
app = FastAPI(title="Agente Dev", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(saude_router, tags=["saude"])
app.include_router(chat_router, prefix="/v1", tags=["chat"])
app.include_router(gerar_router, prefix="/v1", tags=["gerar"])
app.include_router(conversas_router, prefix="/v1", tags=["conversas"])

FRONTEND_DIST_DIR = Path(__file__).resolve().parent / "frontend" / "quest-talk-gui" / "dist"
FRONTEND_INDEX_FILE = FRONTEND_DIST_DIR / "index.html"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"

FRONTEND_AVAILABLE = FRONTEND_INDEX_FILE.exists()

if FRONTEND_AVAILABLE:
    if FRONTEND_ASSETS_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend-assets")

    app.mount("/app", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    async def serve_frontend_root() -> FileResponse:
        return FileResponse(FRONTEND_INDEX_FILE)
else:
    @app.get("/", include_in_schema=False)
    async def frontend_not_ready() -> JSONResponse:
        return JSONResponse(
            {
                "message": "Frontend não encontrado. Execute 'make frontend-build' ou 'npm run build' "
                "em src/app/frontend/quest-talk-gui para gerar o diretório dist."
            },
            status_code=503,
        )
