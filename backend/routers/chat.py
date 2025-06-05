from fastapi import APIRouter
from models.schemas import ChatRequest
from services import reasoning, history_manager
from services.context_manager import ContextManager

router = APIRouter()

# Initialize context manager
context_mgr = ContextManager()

@router.post("/message")
def chat_endpoint(chat: ChatRequest):
    """
    FIXED: Use consistent context management for regular chat
    """
    # Add user message to history
    history_manager.add_message(chat.user_id, chat.message)
    
    # Get full history
    full_history = history_manager.get_history(chat.user_id)
    
    # Prepare context messages for LLM
    context_messages = context_mgr.prepare_context_for_llm(full_history[:-1], chat.message)
    
    # Get response with proper context
    reply = reasoning.respond_with_context(context_messages)
    
    # Add assistant's reply to history
    history_manager.add_message(chat.user_id, reply)
    
    return {"reply": reply, "history": history_manager.get_history(chat.user_id)}