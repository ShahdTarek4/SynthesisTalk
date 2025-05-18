from typing import Dict, List

conversation_store: Dict[str, List[str]] = {}

def add_message(user_id: str, message: str):
    if user_id not in conversation_store:
        conversation_store[user_id] = []
    conversation_store[user_id].append(message)

def get_history(user_id: str):
    return conversation_store.get(user_id, [])
