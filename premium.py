from telebot import types

premium_users = {}  # user_id: plan

def handle_premium(bot, chat_id, user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⭐ PLUS – 8$", callback_data="plan_plus"))
    markup.add(types.InlineKeyboardButton("👑 PRO – 18$", callback_data="plan_pro"))

    bot.send_message(chat_id, "*💎 Premium пландар:*", reply_markup=markup)

def is_premium(user_id):
    return user_id in premium_users

def set_plan(user_id, plan):
    premium_users[user_id] = plan

# =========================
# Callback PLAN
# =========================
def register_plan_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data in ["plan_plus", "plan_pro"])
    def choose_plan(call):
        plan = "plus" if call.data == "plan_plus" else "pro"
        set_plan(call.from_user.id, plan)
        bot.answer_callback_query(call.id, f"✅ {plan.upper()} планы активдүү (демо)")
        bot.send_message(call.message.chat.id, f"🎉 *{plan.upper()}* планы активдешти!")

        # =========================
        # Демо функцияларды көрсөтүү
        # =========================
        if plan == "plus":
            bot.send_message(call.message.chat.id, "💡 Plus: текст, суроо-жооп, OCR текст анализ, обучение/код/бизнес режимдер")
        else:
            bot.send_message(call.message.chat.id, "💎 Pro: Plus функциялар + видео, камера, голосовой ввод, личный помощник, конфиденциальность")

