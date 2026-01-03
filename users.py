# users.py
import json
import os
from threading import Lock

FILE = "users.json"
_lock = Lock()

def _load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id: int):
    with _lock:
        data = _load()
        return data.get(str(user_id))

def save_user(user_id: int, country: str, language: str, plan="free"):
    with _lock:
        data = _load()
        data[str(user_id)] = {
            "country": country,
            "language": language,
            "plan": plan
        }
        _save(data)

def update_user(user_id: int, **fields):
    with _lock:
        data = _load()
        uid = str(user_id)
        if uid not in data:
            return
        data[uid].update(fields)
        _save(data)
