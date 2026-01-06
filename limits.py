# limits.py – лимит текшерүү функциясы

from users import get_user  # user маалыматын алуу үчүн

def can_use(user_id):
    """
    Колдонуучу күнүмдүк лимитти колдоно алабы текшерет.
    FREE – 20 суроо, PLUS/PRO – безлимит
    """
    user = get_user(user_id)
    if not user:
        return True  # жаңы колдонуучу – уруксат бер

    if user.get("plan", "free") in ["plus", "pro"]:
        return True  # премиум – безлимит

    # FREE үчүн – күнүмдүк суроолорду сана
    today_count = user.get("daily_count", 0)
    return today_count < 30  # күнүнө 30 суроо лимит

def increment_daily_count(user_id):
    """ Суроо берилгенде санагычты көбөйтөт """
    from users import _users  # ички өзгөрмө
    if user_id in _users:
        today_count = _users[user_id].get("daily_count", 0)
        _users[user_id]["daily_count"] = today_count + 1
