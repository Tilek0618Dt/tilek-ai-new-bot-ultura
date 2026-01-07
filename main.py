# main.py – акыркы туура версия (иштейт!)

import telebot
from telebot import types

from config import BOT_TOKEN
from users import get_user, save_user, set_plan
from countries import COUNTRIES
from languages import t
from grok_ai import grok_answer
from plans import is_plus, is_pro

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if user and user.get("language"):
        show_menu(message)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, c in COUNTRIES.items():
        markup.add(types.InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{code}"))

    bot.send_message(message.chat.id, "🌍 *Өлкөңүздү тандаңыз / Choose your country:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("country_"))
def save_country(call):
    code = call.data.split("_")[1]
    c = COUNTRIES.get(code)
    if c:
        save_user(call.from_user.id, code, c["lang"])
        bot.answer_callback_query(call.id)
        show_menu(call.message)

def show_menu(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("💬 Суроо берүү", "⭐️ Premium")
    kb.add("🌐 Тил өзгөртүү", "🆘 Жардам")

    bot.send_message(message.chat.id, f"*{t('menu_ready', lang)}*", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "⭐️ Premium")
def premium(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("⭐️ PLUS – 8$/ай", callback_data="buy_plus"),
        types.InlineKeyboardButton("👑 PRO – 18$/ай", callback_data="buy_pro")
    )
    kb.add(types.InlineKeyboardButton("🔙 Артка", callback_data="back"))

    user = get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"
    text = "*💎 Премиум пландар:*\n\n⭐️ PLUS – безлимит + тез жооп\n👑 PRO – бардык функциялар + видео генерация"
    bot.send_message(message.chat.id, f"*{t('menu_ready', lang)}*\n\n{text}", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data in ["buy_plus", "buy_pro", "back"])
def buy(call):
    if call.data == "back":
        show_menu(call.message)
        bot.answer_callback_query(call.id)
        return
    plan = "plus" if call.data == "buy_plus" else "pro"
    set_plan(call.from_user.id, plan)
    bot.answer_callback_query(call.id, f"{plan.upper()} активдешти! 🎉")
    show_menu(call.message)

@bot.message_handler(func=lambda message: message.text in ["💬 Суроо берүү", "🌐 Тил өзгөртүү", "🆘 Жардам"])
def handle_menu(message):
    if message.text == "🌐 Тил өзгөртүү":
        start(message)
        return
    elif message.text == "🆘 Жардам":
        bot.send_message(message.chat.id, "🆘 *Жардам*\n\nБул бот Grok күчү менен иштейт. Суроо бериңиз – чынчыл жана акылдуу жооп аласыз!\n\nПремиум пландар үчүн ⭐️ Premium баскыла.")
        return
    else:  # "💬 Суроо берүү"
        user = get_user(message.from_user.id)
        lang = user.get("language", "en") if user else "en"
        bot.send_message(message.chat.id, t('ask_question', lang))

@bot.message_handler(content_types=["text"])
def chat(message):
    user = get_user(message.from_user.id)
    if not user or not user.get("language"):
        start(message)
        return

    lang = user["language"]
    is_pro_user = is_pro(user)

    answer = grok_answer(message.text, lang=lang, is_pro=is_pro_user)

    if is_plus(user):
        answer += "\n\n⚡️ *PLUS режим: тез жана безлимит*"
    if is_pro(user):
        answer += "\n\n👑 *PRO режим: эң күчтүү Grok + бардык функциялар*"

    bot.send_message(message.chat.id, answer)

print("🔥 Tilek AI ишке кирди – Grok күчү менен!")
bot.infinity_polling()
