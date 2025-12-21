import telebot
import requests
import os
from premium import register_handlers

# =========================
# ENV VARIABLES
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN жок (Render Env Vars текшер)")

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
Сен — Тилек AI, Кыргызстандын биринчи толук кыргызча жасалма интеллектисиң.
Кыргызча, орусча, англисче сүйлөйсүң.
"""

# =========================
# COMMANDS
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Салам! Мен Тилек AI 😎")

@bot.message_handler(func=lambda message: True)
def answer(message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.text}
                ],
                "max_tokens": 800
            },
            timeout=60
        )

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

    except Exception as e:
        reply = f"❌ Ката: {e}"

    bot.reply_to(message, reply)

# =========================
# PREMIUM HANDLERS
# =========================
register_handlers(bot)

# =========================
# START BOT
# =========================
if name == "main":
    print("🔥 Tilek AI иштеп жатат...")
    bot.polling(none_stop=True)
