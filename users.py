users = {}

def get_user(user_id):
    return users.get(user_id)

def save_user(user_id, country, language, plan="free"):
    users[user_id] = {
        "country": country,
        "language": language,
        "plan": plan
    }

def set_plan(user_id, plan):
    if user_id in users:
        users[user_id]["plan"] = plan
