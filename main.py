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
    data = await request.json()
    
    # Validação básica dos dados recebidos
    if not data.get("from_user") or not data.get("message"):
        raise HTTPException(status_code=400, detail="Dados inválidos")
    
    # Aqui você pode processar a mensagem (ex: enviar para a API do DeepSeek)
    print(f"Mensagem recebida de {data['from_user']}: {data['message']}")
    
    return {"status": "success", "message": "Webhook recebido com sucesso!"}

# Rota de teste
@app.get("/")
def read_root():
    return {"message": "Webhook está funcionando!"}
