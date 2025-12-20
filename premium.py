from telebot import types
import datetime

premium_users = {}  # {user_id: expiry_date}

def is_premium(user_id):
    if user_id in premium_users:
        if premium_users[user_id] > datetime.datetime.now():
            return True
        else:
            del premium_users[user_id]
    return False

def add_premium(user_id, days=30):
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    premium_users[user_id] = expiry

def register_handlers(bot):
    @bot.message_handler(commands=['premium'])
    def premium_command(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Plus — 699 сом", callback_data="buy_plus"))
        markup.add(types.InlineKeyboardButton("Pro — 1499 сом", callback_data="buy_pro"))
        bot.send_message(
            message.chat.id,
            "💎 *Tilek AI Premium*\n\nPlus (699 сом):\n• Жеке эс тутум\n• Акча табуу ментор\n• Копирайтер\n• Чексиз суроо\n\nPro (1499 сом):\n• Бардыгы Plus'тагы +\n• Үн менен сүйлөшүү\n• Сүрөт жасоо\n• YouTube скрипт\n\nТандооңузду басыңыз:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    @bot.callback_query_handler(func=lambda call: call.data in ["buy_plus", "buy_pro"])
    def handle_payment(call):
        if call.data == "buy_plus":
            price = 699
            plan = "Plus"
        else:
            price = 1499
            plan = "Pro"
        
        prices = [types.LabeledPrice(label=f"{plan} — 30 күн", amount=price * 100)]
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"Tilek AI {plan}",
            description=f"{plan} версия — 30 күн",
            payload=call.data,
            provider_token="",  # Renderге / BotFatherдан төлөм токен кошосуң
            currency="XTR",
            prices=prices
        )

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def pre_checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @bot.message_handler(content_types=['successful_payment'])
    def successful_payment(message):
        bot.send_message(message.chat.id, "🎉 Төлөм ийгиликтүү! Премиум версия активдештирилди! 30 күн чексиз колдонуңуз!")
