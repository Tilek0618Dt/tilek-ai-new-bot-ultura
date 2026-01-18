# users.py – толук версия: план + реферал саны + 5 дос = 1 жума бекер PLUS

import json
import time
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

def get_user(user_id):
    user_id_str = str(user_id)
    return users.get(user_id_str, {
        "country": None,
        "language": "ky",
        "plan": "free",
        "referral_count": 0,
        "referral_code": None,
        "plus_bonus_activated": False,
        "plus_bonus_until": 0
    })

def save_user(user_id, country, language):
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {
            "country": country,
            "language": language,
            "plan": "free",
            "referral_count": 0,
            "referral_code": f"TILEK{user_id % 1000000:06d}",
            "plus_bonus_activated": False,
            "plus_bonus_until": 0
        }
    else:
        users[user_id_str]["country"] = country
        users[user_id_str]["language"] = language
    save_users(users)

def set_plan(user_id, plan):
    user_id_str = str(user_id)
    if user_id_str in users:
        users[user_id_str]["plan"] = plan
        save_users(users)

def add_referral(user_id):
    user_id_str = str(user_id)
    if user_id_str in users:
        users[user_id_str]["referral_count"] = users[user_id_str].get("referral_count", 0) + 1
        count = users[user_id_str]["referral_count"]
        if count >= 5 and not users[user_id_str].get("plus_bonus_activated", False):
            users[user_id_str]["plan"] = "plus"
            users[user_id_str]["plus_bonus_activated"] = True
            users[user_id_str]["plus_bonus_until"] = int(time.time()) + 7 * 24 * 3600
            save_users(users)
            return True  # бонус берилди
        save_users(users)
        return False
    return False

def get_referral_code(user_id):
    user = get_user(user_id)
    return user.get("referral_code", f"TILEK{user_id % 1000000:06d}")

def check_bonus(user_id):
    user = get_user(user_id)
    if user.get("plus_bonus_activated", False):
        until = user.get("plus_bonus_until", 0)
        if time.time() > until:
            user["plan"] = "free"
            user["plus_bonus_activated"] = False
            save_users(users)
            return None  # кабар бербейбиз
        else:
            return f"✅ 1 жума бекер PLUS активдүү!"
    return None
