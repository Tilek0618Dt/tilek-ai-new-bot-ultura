import telebot
import requests
import os

from premium import register_handlers, is_premium
from users import load_users, save_users

# === TOKENS ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# Premium кнопкалар / төлөмдөр
register_handlers(bot)

SYSTEM_PROMPT = """
Сен — Тилек AI.
Кыргызча, орусча, англисче так жооп бер.
"""

# === START ===
@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "plan": "free",
            "count": 0
        }
        save_users(users)

    bot.send_message(
        message.chat.id,
        "👋 Кош келдиңиз!\n\n"
        "🆓 FREE — 20 суроо\n"
        "⭐ PLUS — кеңейтилген мүмкүнчүлүктөр\n"
        "👑 PRO — толук мүмкүнчүлүктөр\n\n"
        "Суроо жазыңыз же Premium тандаңыз 👇"
    )

# === AI ANSWER ===
@bot.message_handler(func=lambda message: True)
def answer(message):
    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {"plan": "free", "count": 0}

    plan = users[uid]["plan"]

    # FREE
    if plan == "free":
        if users[uid]["count"] >= 20:
            bot.reply_to(
                message,
                "⚠️ Free лимити бүткөн!\n\n"
                "⭐ PLUS же 👑 PRO сатып алыңыз."
            )
            save_users(users)
            return
        users[uid]["count"] += 1
        max_tokens = 400

    # PLUS
    elif plan == "plus":
        max_tokens = 1200

    # PRO
    elif plan == "pro":
        max_tokens = 2000

    save_users(users)

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
                "max_tokens": max_tokens
            },
            timeout=60
        )

        reply = response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        reply = f"⚠️ Ката чыкты: {e}"

    bot.reply_to(message, reply)

# === RUN ===
if __name__ == "__main__":
    print("🔥 Tilek AI иштеп жатат...")
    bot.polling(none_stop=True)
