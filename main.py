from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Modelo para a requisição recebida
class WhatsAppMessage(BaseModel):
    event: str
    data: dict

# Rota para receber o webhook do WhatsApp
@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        payload = await request.json()
        event_type = payload.get("event")
        message_data = payload.get("data", {})

        # Log formatado para melhor visualização
        print("============================")
        print(f"Evento recebido: {event_type}")
        print(f"Dados: {message_data}")
        print("============================")

        # Filtrar apenas eventos de mensagens de chat
        if event_type in ["message.updated", "message.created"] and message_data.get("type") == "chat":
            text = message_data.get("text")
            contact_id = message_data.get("contactId")

            if not text or not contact_id:
                raise HTTPException(status_code=400, detail="Dados inválidos")
            
            print(f"Mensagem recebida de {contact_id}: {text}")
            
            return {"status": "success", "message": "Webhook processado com sucesso!", "event": event_type}
        else:
            return {"status": "ignored", "message": "Evento ignorado.", "event": event_type}
    
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao processar a requisição: {str(e)}")

# Rota de teste (GET)
@app.get("/")
def read_root():
    return {"message": "Webhook está funcionando!"}
