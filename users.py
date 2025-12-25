import json
import os

FILE = "users.json"

def load_users():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
