# premium.py
from telebot import types

premium_users = {}  # user_id: plan

def is_premium(user_id):
    return user_id in premium_users

def register_handlers(bot):

    @bot.message_handler(commands=['premium'])
    def premium_command(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⭐ PLUS", callback_data="buy_plus"))
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
            price = 299 * 100
            payload = "plus"
        else:
            title = "Tilek AI PRO"
            price = 599 * 100
            payload = "pro"

        from telebot.types import LabeledPrice
        prices = [LabeledPrice(label=title, amount=price)]

        PROVIDER_TOKEN = "<СЕНИН_STRIPE_PROVIDER_TOKEN>"
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=title,
            description="AI Premium мүмкүнчүлүктөрү",
            payload=payload,
            provider_token=PROVIDER_TOKEN,
            currency="USD",
            prices=prices,
            start_parameter="premium"
        )


