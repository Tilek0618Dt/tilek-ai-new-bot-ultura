from telebot import types

premium_users = set()

def is_premium(user_id):
    return user_id in premium_users

def register_handlers(bot):

    @bot.message_handler(commands=['premium'])
    def premium_command(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "⭐ Premium активдештирүү",
                callback_data="activate_premium"
            )
        )

        bot.send_message(
            message.chat.id,
            "💎 *Tilek AI Premium*\n\n"
            "• Чексиз суроо\n"
            "• Тез жооп\n"
            "• Күчтүү AI режим\n\n"
            "Төмөнкү баскычты бас:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    @bot.callback_query_handler(func=lambda call: call.data == "activate_premium")
    def activate(call):
        premium_users.add(call.from_user.id)
        bot.answer_callback_query(call.id, "✅ Premium активдешти!")
        bot.send_message(
            call.message.chat.id,
            "🎉 Сиз эми *PREMIUM* колдонуучусуз!",
            parse_mode="Markdown"
        )
