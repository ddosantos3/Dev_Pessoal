curl -s http://127.0.0.1:8000/v1/gerar -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "objetivo":"Gerar um CRUD de tarefas com FastAPI, Supabase e testes",
    "path_saida":"./saida/crud_tarefas",
    "overwrite": true,
    "git": true
  }' | jq
