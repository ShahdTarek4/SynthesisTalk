from typing import Dict, List
import json
import os

STORE_PATH = "data/conversations.json"

def _load():
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r") as f:
        return json.load(f)

def _save(data):
    os.makedirs("data", exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_message(user_id: str, message: str):
    store = _load()
    store.setdefault(user_id, []).append(message)
    _save(store)

def get_history(user_id: str):
    store = _load()
    return store.get(user_id, [])

conversation_store: Dict[str, List[str]] = {}

