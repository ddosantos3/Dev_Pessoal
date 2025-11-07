# Agente Dev – Seu robo pessoal que escreve código completo (API + CLI + Frontend)

## Visão geral
Este projeto entrega um agente de IA capaz de planejar e gerar projetos inteiros a partir de uma conversa. Ele cria a estrutura de pastas, escreve os arquivos (HTML/CSS/JS ou stacks solicitadas), salva históricos em disco e ainda expõe API/CLI para automação.  
Principais componentes:
- **API FastAPI** (`/v1/chat`, `/v1/gerar`, `/v1/conversas`)  
- **Frontend React + Vite** conectado ao agente (histórico visual, chat e geração automática)  
- **Histórico versionado** em `data/conversas` (JSON + arquivos criados)  
- **CLI** (`python -m app.services.agente`) para rodar direto do terminal  

## Índice
1. [Requisitos](#requisitos)  
2. [Setup rápido](#setup-rápido)  
3. [Ambiente virtual](#ambiente-virtual)  
4. [Variáveis de ambiente](#variáveis-de-ambiente)  
5. [Executando a API](#executando-a-api-uvicorn)  
6. [Executando o Frontend](#executando-o-frontend-vite--react)  
7. [Usando a CLI](#usando-a-cli)  
8. [Exemplos com curl e HTTPie](#exemplos-com-curl-e-httpie)  
9. [Docker e docker-compose](#docker-e-docker-compose)  
10. [Integração com VS Code e GitHub](#integração-com-vs-code--github)  
11. [Fluxo recomendado](#fluxo-recomendado)  
12. [Troubleshooting](#troubleshooting)  
13. [Organização do projeto](#organização-do-projeto)  
14. [Boas práticas e segurança](#boas-práticas-e-segurança)  

## Requisitos
- Python 3.11+  
- Pip atualizado (`python -m pip install -U pip`)  
- Node.js 18+ (frontend em Vite/React)  
- (Opcional) Docker + Docker Compose  
- Chave de API: `OPENAI_API_KEY` ou `HUGGINGFACE_API_KEY`  

## Setup rápido
```bash
git clone https://github.com/ddosantos3/Dev_Pessoal.git agente_dev
cd agente_dev

cp .env.example .env          # edite com sua chave e preferências
python -m venv .venv
. .venv/Scripts/activate      # ou . .venv/bin/activate no Linux/macOS
pip install -r requirements.txt

make frontend-install
cp src/app/frontend/quest-talk-gui/.env.example src/app/frontend/quest-talk-gui/.env.local
```
Ajuste `VITE_API_BASE_URL` no `.env.local` se a API estiver em outra URL (por padrão 127.0.0.1:8000).  

### Publicar build de produção do frontend
```powershell
cd src/app/frontend/quest-talk-gui
npm run build
```

### Rodar frontend em modo dev
```powershell
cd src/app/frontend/quest-talk-gui
npm run dev
```

## Ambiente virtual
### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```
### Windows (CMD)
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -U pip
pip install -r requirements.txt
```
### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```
Para sair: `deactivate`.  

## Variáveis de ambiente
Edite `.env` com base no `.env.example`:
```
LLM_PROVIDER=openai              # ou huggingface
OPENAI_API_KEY=...
HUGGINGFACE_API_KEY=...
MODEL_LLM=gpt-4.1
MODEL_EMBEDDINGS=text-embedding-3-large
BASE_DIR_SAIDA=./saida           # onde projetos gerados são salvos
BASE_DIR_CONVERSAS=./data/conversas
GIT_AUTO_COMMIT=false
```
Nunca versiona chaves sensíveis.  

## Executando a API (Uvicorn)
```bash
uvicorn --app-dir src app.main:app --reload
```
A API sobe em `http://127.0.0.1:8000`.  
Docs Swagger: `http://127.0.0.1:8000/docs`  
Health check: `GET /health -> {"status":"ok"}`  

Rotas principais:  
- `POST /v1/chat` – conversa/ideação com salvamento automático em `data/conversas`  
- `POST /v1/gerar` – (opcional) geração guiada via API/CLI  
- `GET /v1/conversas`, `GET /v1/conversas/{id}`, `DELETE /v1/conversas/{id}` – gestão do histórico e arquivos  

## Executando o Frontend (Vite + React)
O frontend vive em `src/app/frontend/quest-talk-gui`.

**Modo dev**  
```bash
make frontend-dev    # roda Vite na porta 5173
```
A UI em `http://127.0.0.1:5173` conversa com a API definida via `VITE_API_BASE_URL`.  

**Build de produção**  
```bash
make frontend-build
```
Os artefatos ficam em `src/app/frontend/quest-talk-gui/dist`. Se o diretório existir, o FastAPI serve automaticamente em `http://127.0.0.1:8000/app` (assets em `/assets`).  

**Fluxo na UI**  
- Clique em **Nova conversa**, defina o contexto (ex.: “Landing page em Tailwind para barbearia”).  
- Use o chat para pedir o site. O backend gera `index.html`, `assets/styles.css`, `assets/script.js` e salva tudo em `data/conversas/<slug>/`.  
- Cada resposta traz um resumo animado (com emojis e lista de arquivos) para indicar o que foi salvo.  
- Histórico na barra lateral (com zoom/hover) permite reabrir ou excluir conversas.  

## Usando a CLI
```bash
python -m app.services.agente gerar ^
  --objetivo "Gerar um CRUD de tarefas com FastAPI, Supabase e testes" ^
  --path_saida "./saida/crud_tarefas" ^
  --overwrite true ^
  --git true
```
Linux/macOS: use `\` ao invés de `^`.  

Parâmetros:  
- `--objetivo`: descrição do projeto (mínimo 1–2 frases)  
- `--path_saida`: diretório base (usa `BASE_DIR_SAIDA` se omitido)  
- `--overwrite`: permite sobrescrever arquivos existentes  
- `--git`: ativa commit automático após a geração  

## Exemplos com curl e HTTPie
```bash
# Chat (ideação)
curl -s http://127.0.0.1:8000/v1/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "mensagens":[{"papel":"usuario","conteudo":"Quero um site institucional minimalista"}],
    "contexto":"Landing page com Tailwind e foco em UX"
  }'

# Geração completa
curl -s http://127.0.0.1:8000/v1/gerar -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "objetivo":"Gerar um CRUD de tarefas com FastAPI, Supabase e testes",
    "path_saida":"./saida/crud_tarefas",
    "overwrite": true,
    "git": true
  }'
```

## Docker e docker-compose
```bash
docker build -t agente-dev:latest .
docker compose up --build
```
O `docker-compose.yml` já monta o volume e injeta o `.env`. A API fica em `http://127.0.0.1:8000`. Lembre de rodar `make frontend-build` **antes** se estiver usando bind mount e quiser servir o frontend.  

## Integração com VS Code & GitHub
1. Abra a pasta no VS Code e selecione a venv (`Python: Select Interpreter`).  
2. Extensões úteis: Python, Pylance, Ruff, Black, GitLens, Thunder Client.  
3. Para GitHub, configure apenas um usuário (`git config --global user.name/user.email`) e use `cmdkey /delete:git:https://github.com` para limpar credenciais duplicadas se necessário.  
4. Repositório principal: <https://github.com/ddosantos3/Dev_Pessoal> (frontend integrado).  

## Fluxo recomendado
1. Defina o objetivo da página/experiência.  
2. Abra uma nova conversa no frontend, descreva o briefing (tema, cores, seções).  
3. O agente gera HTML/CSS/JS e salva em `data/conversas/<slug>/`.  
4. Abra o projeto no VS Code diretamente dessa pasta para ajustes finos.  
5. Use `git add`, `git commit`, `git push` para versionar tudo em um único repo.  

## Troubleshooting
- **`uvicorn` não sobe**: confira se a venv está ativa e se `uvicorn --app-dir src app.main:app --reload` está correto.  
- **Frontend reclama de JSON inválido**: verifique `VITE_API_BASE_URL`; o front assume automaticamente `http://127.0.0.1:8000` quando roda em outra porta.  
- **Histórico não aparece**: garanta que `BASE_DIR_CONVERSAS` existe e que o backend tem permissão de escrita.  
- **GitHub pedindo conta toda hora**: limpe credenciais com `cmdkey /delete:git:https://github.com` e autentique apenas o usuário principal.  

## Organização do projeto
```
.
├── data/                     # conversas e arquivos gerados
├── src/
│   └── app/
│       ├── api/              # rotas FastAPI
│       ├── core/             # settings, logging
│       ├── frontend/quest-talk-gui/   # app React/Vite
│       ├── services/         # agente, planner, writer, histórico
│       └── ...
├── requirements.txt / pyproject.toml
├── Makefile                  # comandos (install/run/test/frontend-*)
└── README.md
```

## Boas práticas e segurança
- Não faça commit do `.env` nem de chaves sensíveis.  
- `BASE_DIR_CONVERSAS` e `BASE_DIR_SAIDA` bloqueiam path traversal (apenas caminhos relativos).  
- `overwrite` é falso por padrão para evitar perda de arquivos.  
- Verifique sempre os arquivos gerados antes de publicar em produção.  
- Use tokens do GitHub (PAT) e configure o Credential Manager para um único usuário para evitar prompts repetidos.  
