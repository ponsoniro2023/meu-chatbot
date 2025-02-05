from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Exemplo de modelo de dados para o webhook
class WhatsAppMessage(BaseModel):
    from_user: str
    message: str

# Rota para receber o webhook
@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        data = await request.json()
        print(f"Dados recebidos: {data}")  # Log para depuração
        
        # Extrair campos obrigatórios
        from_user = data.get("from_user") or data.get("from") or data.get("sender")
        message = data.get("message") or data.get("text") or data.get("body")
        
        # Validação básica dos dados recebidos
        if not from_user or not message:
            raise HTTPException(status_code=400, detail="Dados inválidos")
        
        # Aqui você pode processar a mensagem (ex: enviar para a API do DeepSeek)
        print(f"Mensagem recebida de {from_user}: {message}")
        
        return {"status": "success", "message": "Webhook recebido com sucesso!"}
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")  # Log de erros
        raise HTTPException(status_code=400, detail="Erro ao processar a requisição")
