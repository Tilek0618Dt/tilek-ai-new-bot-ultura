from config import PLANS

def get_plan(user):
    return user.get("plan", "free")

def is_plus(user):
    return user["plan"] in ["plus", "pro"]

def is_pro(user):
    return user["plan"] == "pro"
