from fastapi import APIRouter
from app.schemas.gerar import RequisicaoGerar, RespostaGerar
from app.services.agente import AgenteDev

router = APIRouter()

@router.post("/gerar", response_model=RespostaGerar)
async def gerar(req: RequisicaoGerar) -> RespostaGerar:
    """
    Gera um projeto completo em disco (planeja -> escreve arquivos -> git opcional).
    """
    agente = AgenteDev()
    plano, arquivos_escritos, commit_hash = await agente.gerar_projeto(
        objetivo=req.objetivo,
        path_saida=req.path_saida,
        overwrite=req.overwrite,
        git=req.git,
    )
    return RespostaGerar(plano=plano, arquivos=arquivos_escritos, commit=commit_hash)
