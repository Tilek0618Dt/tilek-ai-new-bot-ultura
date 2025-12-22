from telebot import types
import datetime

premium_users = {}

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
            "💎 *Tilek AI Premium*\n\n"
            "Plus (699 сом):\n• Чексиз суроо\n\n"
            "Pro (1499 сом):\n• Баары + кошумча функциялар",
            reply_markup=markup,
            parse_mode="Markdown"
        )
