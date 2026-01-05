_users = {}

def get_user(user_id):
    return _users.get(user_id)

def save_user(user_id, country, language, plan="free"):
    _users[user_id] = {
        "country": country,
        "language": language,
        "plan": plan
    }

def set_plan(user_id, plan):
    if user_id in _users:
        _users[user_id]["plan"] = plan
