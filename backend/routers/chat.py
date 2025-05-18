from fastapi import APIRouter
from models.schemas import ChatRequest
from services import reasoning, history_manager

router = APIRouter()

@router.post("/message")
def chat_endpoint(chat: ChatRequest):
    history_manager.add_message(chat.user_id, chat.message)
    full_history = history_manager.get_history(chat.user_id)
    reply = reasoning.respond_with_history(full_history)
    history_manager.add_message(chat.user_id, reply)
    return {"reply": reply, "history": history_manager.get_history(chat.user_id)}
