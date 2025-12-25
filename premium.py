# premium.py
import json
from telebot import types

premium_users = {}  # user_id: plan
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def is_premium(user_id):
    return str(user_id) in premium_users

def add_free_usage(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"plan": "free", "count": 0}
    users[uid]["count"] += 1
    save_users(users)

def free_usage_left(user_id, max_free=20):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return max_free
    if users[uid]["plan"] != "free":
        return max_free
    return max_free - users[uid]["count"]

def register_handlers(bot):

    @bot.message_handler(commands=['premium'])
    def premium_command(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⭐️ PLUS", callback_data="buy_plus"))
        markup.add(types.InlineKeyboardButton("👑 PRO", callback_data="buy_pro"))
        bot.send_message(
            message.chat.id,
            "💎 Premium планы тандаңыз:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data in ["buy_plus", "buy_pro"])
    def pay(call):
        if call.data == "buy_plus":
            title = "Tilek AI PLUS"
            price = 800 * 100  # $8
            payload = "plus"
        else:
            title = "Tilek AI PRO"
            price = 1800 * 100  # $18
            payload = "pro"

        from telebot.types import LabeledPrice
        prices = [LabeledPrice(label=title, amount=price)]

        PROVIDER_TOKEN = "<СЕНИН_STRIPE_PROVIDER_TOKEN>"

        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=title,
            description="AI Premium мүмкүнчүлүктөрү",
            provider_token=PROVIDER_TOKEN,
            currency="USD",
            prices=prices,
            start_parameter=payload
        )

    @bot.message_handler(content_types=['successful_payment'])
    def successful_payment(message):
        users = load_users()
        uid = str(message.from_user.id)

        plan = message.successful_payment.invoice_payload
        if plan not in ["plus", "pro"]:
            plan = "plus"
        users[uid] = {"plan": plan, "count": 0}
        save_users(users)

        premium_users[uid] = plan

        bot.send_message(
            message.chat.id,
            f"🎉 Төлөм ийгиликтүү!\nСиз {plan.upper()} актив кылдыңыз."
        )

