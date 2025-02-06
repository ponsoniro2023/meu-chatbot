from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
from config import API_BASE_URL, API_TOKEN

app = FastAPI()

# Número autorizado para testes
NUMERO_TESTE = "5511976829298"  # Formato correto com DDI do Brasil

# Função para enviar mensagem via API do WhatsApp
def enviar_mensagem(numero_telefone: str, mensagem: str):
    url = f"{API_BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "number": numero_telefone,  # Corrigido para "number"
        "type": "chat",
        "text": mensagem
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Falha ao enviar mensagem: {response.status_code}, {response.text}")
    return response.status_code

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

        # Capturar o número real do telefone do usuário
        contact_id = message_data.get("contactId", "")
        numero_telefone = message_data.get("idFromService", "")

        # Se o número vier no formato "5511976829298@c.us", remover "@c.us"
        if numero_telefone and "@c.us" in numero_telefone:
            numero_telefone = numero_telefone.replace("@c.us", "")

        # Se o número não foi encontrado, buscar em "data.number"
        if not numero_telefone:
            numero_telefone = message_data.get("data", {}).get("number", "")

        text = message_data.get("text", "").strip()  # Evita erro caso text seja None e remove espaços extras

        if not text or not contact_id or not numero_telefone:
            raise HTTPException(status_code=400, detail="Dados inválidos")
        
        print(f"Mensagem recebida de {contact_id} ({numero_telefone}): {text}")
        
        # Verifica se a mensagem foi enviada pelo número de teste e se o texto é "teste"
        if numero_telefone == NUMERO_TESTE and text.lower() == "teste":
            enviar_mensagem(numero_telefone, "Recebemos sua mensagem de teste!")
            return {"status": "success", "message": "Mensagem de teste processada!", "event": event_type}
        
        return {"status": "ignored", "message": "Número ou mensagem não autorizados para teste.", "event": event_type}
    
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao processar a requisição: {str(e)}")

# Rota de teste (GET)
@app.get("/")
def read_root():
    return {"message": "Webhook está funcionando!"}
