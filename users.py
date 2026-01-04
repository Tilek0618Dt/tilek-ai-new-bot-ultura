# users.py

_users = {}

def get_user(user_id):
    return _users.get(user_id)

def save_user(user_id, data):
    _users[user_id] = data
