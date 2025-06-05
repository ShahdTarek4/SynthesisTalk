import json
import os

STORE_PATH = "data/notes.json"

def _load():
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r") as f:
        return json.load(f)

def _save(data):
    os.makedirs("data", exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def save_note(user_id: str, note: str):
    notes = _load()
    notes.setdefault(user_id, []).append(note)
    _save(notes)
    return {"notes": notes[user_id]}

def get_notes(user_id: str):
    notes = _load()
    return {"notes": notes.get(user_id, [])}

def delete_note(user_id: str, index: int):
    notes = _load()
    if user_id in notes and 0 <= index < len(notes[user_id]):
        del notes[user_id][index]
        _save(notes)
    return {"notes": notes.get(user_id, [])}

def clear_notes(user_id: str):
    notes = _load()
    notes[user_id] = []
    _save(notes)
    return {"notes": []}
