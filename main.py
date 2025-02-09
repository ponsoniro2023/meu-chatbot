from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
from config import API_BASE_URL, API_TOKEN

app = FastAPI()

# Modelo para a requisição recebida
class WhatsAppMessage(BaseModel):
    event: str
    data: dict

# Número autorizado para testes
NUMERO_TESTE = "5511976829298"

# Função para buscar número de telefone pelo contactId
def obter_numero_telefone(contact_id):
    url = f"{API_BASE_URL}/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contact_data = response.json()
        return contact_data.get("data", {}).get("number")  # Ajuste conforme a resposta real da API
    else:
        print(f"Erro ao buscar número de telefone para {contact_id}: {response.text}")
        return None

# Função para enviar mensagem via API do WhatsApp
def enviar_mensagem(numero_telefone: str, mensagem: str):
    url = f"{API_BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "number": numero_telefone,
        "type": "chat",
        "text": mensagem,
        "serviceId": "8e473787-7548-417f-83e1-5eb1bd533d6f",
        "userId": "d2787b46-36fd-4718-93f7-1c86f0e3cab9",
        "dontOpenTicket": True
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Falha ao enviar mensagem: {response.status_code}, {response.text}")
    return response.status_code

# Função para enviar um comentário e transferir o atendimento para outro departamento
def enviar_comentario_e_transferir(ticket_id: str, comentario: str, novo_departamento_id: str):
    url = f"{API_BASE_URL}/tickets/{ticket_id}/transfer"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "comment": comentario,
        "departmentId": "61249740-edcb-4518-9ea6-21c92f775163"
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Comentário enviado e atendimento transferido com sucesso!")
    else:
        print(f"Falha ao transferir atendimento: {response.status_code}, {response.text}")
    return response.status_code

# Rota para receber o webhook do WhatsApp
@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        payload = await request.json()
        print("=== Webhook recebido ===")
        print(payload)
        print("========================")
        
        event_type = payload.get("event")
        message_data = payload.get("data", {})

        # Validando os dados recebidos
        if not isinstance(message_data, dict):
            raise HTTPException(status_code=400, detail="Formato inválido para 'data'")
        
        text = message_data.get("text")  # Pode ser None
        contact_id = message_data.get("contactId")  # Pode ser None
        numero_telefone = message_data.get("fromId")  # Pode ser None
        is_from_me = message_data.get("isFromMe", False)  # Verifica se foi enviado pelo próprio sistema
        ticket_id = message_data.get("ticketId")  # Pode ser None
        
        if not event_type or not text or not contact_id:
            raise HTTPException(status_code=400, detail="Dados obrigatórios ausentes ou inválidos")
        
        print(f"Texto recebido: {text}")
        print(f"From ID recebido: {numero_telefone}")
        print(f"Contact ID recebido: {contact_id}")
        print(f"Mensagem enviada pelo próprio sistema: {is_from_me}")
        
        # Se a mensagem foi enviada pelo próprio sistema, não responder
        if is_from_me:
            print("Mensagem foi enviada pelo próprio sistema. Ignorando...")
            return {"status": "ignored", "message": "Mensagem enviada pelo próprio sistema.", "event": event_type}
        
        # Obtém o número de telefone real, se necessário
        if numero_telefone and "@c.us" in numero_telefone:
            numero_telefone = numero_telefone.split("@")[0]
        else:
            numero_telefone = obter_numero_telefone(contact_id)
        
        print(f"Número de telefone final: {numero_telefone}")
        print(f"Comparação com número teste: {numero_telefone == NUMERO_TESTE}")
        
        # Se a mensagem for "teste", enviar uma resposta
        if numero_telefone == NUMERO_TESTE and text.lower() == "teste":
            enviar_mensagem(numero_telefone, "Recebemos sua mensagem!")
            return {"status": "success", "message": "Mensagem de teste processada!", "event": event_type}
        
        # Se a mensagem for "teste2", transferir o atendimento
        if numero_telefone == NUMERO_TESTE and text.lower() == "teste2" and ticket_id:
            enviar_comentario_e_transferir(ticket_id, "Transferindo atendimento para outro setor.", "NOVO_DEPARTAMENTO_ID")
            return {"status": "success", "message": "Atendimento transferido!", "event": event_type}
        
        return {"status": "ignored", "message": "Número ou mensagem não autorizados para teste.", "event": event_type}
    
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao processar a requisição: {str(e)}")

# Rota de teste (GET)
@app.get("/")
def read_root():
    return {"message": "Webhook está funcionando!"}
