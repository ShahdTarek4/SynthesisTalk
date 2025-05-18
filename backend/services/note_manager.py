note_store = {}

def save_note(user_id: str, note: str):
    if user_id not in note_store:
        note_store[user_id] = []
    note_store[user_id].append(note)
    return {"notes": note_store[user_id]}

def get_notes(user_id: str):
    return {"notes": note_store.get(user_id, [])}
