curl -s http://127.0.0.1:8000/v1/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "mensagens":[
      {"papel":"usuario","conteudo":"Quero um microserviço que calcula EMA/VWAP via FastAPI"}
    ],
    "contexto":"Python 3.11, testes, logging, sem banco por enquanto"
  }' | jq
