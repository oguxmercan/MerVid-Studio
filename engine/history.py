import os
import json
from datetime import datetime
from engine.cookies import get_app_dir

def get_history_file_path():
    return os.path.join(get_app_dir(), 'history.json')

def load_history() -> list:
    path = get_history_file_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history: list):
    path = get_history_file_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")

def add_history_item(item: dict) -> list:
    history = load_history()
    item['timestamp'] = datetime.now().isoformat()
    item['date_formatted'] = datetime.now().strftime('%d %b %Y, %H:%M')
    history.insert(0, item)
    # keep max 500 items
    if len(history) > 500:
        history = history[:500]
    save_history(history)
    return history

def delete_history_item(item_id: str) -> list:
    history = load_history()
    history = [h for h in history if h.get('id') != item_id]
    save_history(history)
    return history

def clear_all_history() -> list:
    save_history([])
    return []
