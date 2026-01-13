# users.py – толук версия: план + реферал саны + бонус (5 дос = 1 жума бекер PLUS)

_users = {}

def get_user(user_id):
    # Эгер колдонуучу жок болсо – демо маалымат кайтарат (default free)
    return _users.get(user_id, {
        "country": None,
        "language": "ky",  # демо тил – кыргызча
        "plan": "free",
        "referral_count": 0,
        "referral_code": None,
        "bonus_until": None  # 1 жума бонус үчүн убакыт (datetime)
    })

def save_user(user_id, country, language, plan="free"):
    referral_code = f"TILEK{user_id % 10000:04d}"  # уникалдуу код
    _users[user_id] = {
        "country": country,
        "language": language,
        "plan": plan,
        "referral_count": 0,
        "referral_code": referral_code,
        "bonus_until": None
    }

def set_plan(user_id, plan):
    if user_id in _users:
        _users[user_id]["plan"] = plan
        # Бонус убактысын тазала (жаңы план болсо)
        _users[user_id]["bonus_until"] = None

def add_referral(user_id):
    if user_id in _users:
        _users[user_id]["referral_count"] += 1
        count = _users[user_id]["referral_count"]
        
        if count >= 5:
            from datetime import datetime, timedelta
            
            # 1 жума бекер PLUS (эгер free же plus болсо – PLUS'ка көтөр)
            current_plan = _users[user_id]["plan"]
            if current_plan in ["free", "plus"]:
                _users[user_id]["plan"] = "plus"
                # Бонус убактысын кошуу (1 жума)
                _users[user_id]["bonus_until"] = datetime.now() + timedelta(days=7)
                return True  # бонус берилди
            return False  # бонус берилген жок (мисалы PRO бар болсо)
    return False

def get_referral_code(user_id):
    user = get_user(user_id)
    return user.get("referral_code", f"TILEK{user_id % 10000:04d}")

def check_bonus(user_id):
    user = get_user(user_id)
    if user.get("bonus_until"):
        from datetime import datetime
        if datetime.now() > user["bonus_until"]:
            # Бонус бүттү – free'ге кайтар
            _users[user_id]["plan"] = "free"
            _users[user_id]["bonus_until"] = None
            return "Бонус убактысы бүттү, досум. Кайра чакырсаң – кайра аласың! 😎"
    return None
