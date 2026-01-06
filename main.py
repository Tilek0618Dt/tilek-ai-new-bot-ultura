import telebot
from telebot import types

from config import BOT_TOKEN
from users import get_user, save_user, set_plan
from plans import is_plus, is_pro
from languages import COUNTRIES
from ai import ai_answer

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ======================
# START → ӨЛКӨ ТАНДОО
# ======================
@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    if user:
        show_menu(message.chat.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, c in COUNTRIES.items():
        markup.add(
            types.InlineKeyboardButton(
                f"{c['flag']} {c['name']}",
                callback_data=f"country_{code}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🌍 *Өлкөңүздү тандаңыз:*",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("country_"))
def save_country(call):
    code = call.data.split("_")[1]
    c = COUNTRIES.get(code)

    if not c:
        return

    save_user(call.from_user.id, code, c["lang"])
    show_menu(call.message.chat.id)

# ======================
# МЕНЮ
# ======================
def show_menu(chat_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💬 Суроо берүү")
    kb.add("⭐️ Premium", "🌐 Тил")
    kb.add("🆘 Жардам")

    bot.send_message(
        chat_id,
        "🤖 *Tilek AI даяр!*",
        reply_markup=kb
    )

# ======================
# PREMIUM
# ======================
@bot.message_handler(func=lambda m: m.text == "⭐️ Premium")
def premium(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("⭐️ PLUS – 8$", callback_data="buy_plus"),
        types.InlineKeyboardButton("👑 PRO – 18$", callback_data="buy_pro")
    )

    bot.send_message(
        message.chat.id,
        "*💎 Premium пландар:*",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data in ("buy_plus", "buy_pro"))
def buy(call):
    plan = "plus" if call.data == "buy_plus" else "pro"
    set_plan(call.from_user.id, plan)

    bot.send_message(
        call.message.chat.id,
        f"🎉 *{plan.upper()}* планы активдешти!\n_(Демо режим)_"
    )

# ======================
# ЧАТ
# ======================
@bot.message_handler(func=lambda m: m.text == "💬 Суроо берүү")
def ask(message):
    bot.send_message(
        message.chat.id,
        "✍️ Сурооңузду жазыңыз"
    )

@bot.message_handler(content_types=["text"])
def chat(message):
    user = get_user(message.from_user.id)
    if not user:
        show_menu(message.chat.id)
        return

    answer = ai_answer(message.text)

    if is_plus(user):
        answer += "\n\n⚡️ *PLUS артыкчылык*"
    if is_pro(user):
        answer += "\n\n👑 *PRO эксперт режим*"

    bot.send_message(message.chat.id, answer)

print("🔥 Tilek AI ишке кирди")
bot.infinity_polling(skip_pending=True)
