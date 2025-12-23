from telebot import types
import datetime

# Пайдаланууну сактоо
premium_users = {}   # {user_id: plan}

free_limit = {}      # {user_id: count}

FREE_MAX = 20

def is_premium(user_id):
    return user_id in premium_users

def add_free_usage(user_id):
    free_limit[user_id] = free_limit.get(user_id, 0) + 1

def free_usage_left(user_id):
    return max(FREE_MAX - free_limit.get(user_id, 0), 0)

def register_handlers(bot):

    # Старт менюдагы кнопкалар
    @bot.message_handler(commands=['start'])
    def start_menu(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("💡 Free (20 суроо)", callback_data="free"),
            types.InlineKeyboardButton("✨ Plus", callback_data="plus"),
            types.InlineKeyboardButton("💎 Pro", callback_data="pro")
        )
        bot.send_message(
            message.chat.id,
            "Салам! Мен Тилек AI 😎\nТандооңузду басыңыз:",
            reply_markup=markup
        )

    # Кнопка логикасы
    @bot.callback_query_handler(func=lambda call: call.data in ["free", "plus", "pro"])
    def handle_plan(call):
        user_id = call.from_user.id
        if call.data == "free":
            bot.answer_callback_query(call.id, f"💡 Free план: {free_usage_left(user_id)} суроо калды")
        elif call.data == "plus":
            premium_users[user_id] = "Plus"
            bot.answer_callback_query(call.id, "✨ Plus активдешти!")
            bot.send_message(call.message.chat.id, "🎉 Сиз Plus колдонуучусуз! Кошумча функциялар ачык")
        elif call.data == "pro":
            premium_users[user_id] = "Pro"
            bot.answer_callback_query(call.id, "💎 Pro активдешти!")
            bot.send_message(call.message.chat.id, "🎉 Сиз Pro колдонуучусуз! Бардык функциялар ачык")
