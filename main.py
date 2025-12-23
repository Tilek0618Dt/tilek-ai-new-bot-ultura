# 1. IMPORT
import telebot
import requests
import os

from premium import register_handlers, is_premium

# 2. ТОКЕНДЕР
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 3. УШУЛ САП ЭҢ МААНИЛҮҮ
register_handlers(bot)

SYSTEM_PROMPT = """
Сен — Тилек AI...
"""

# 4. START
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Салам! Мен Тилек AI 😎")

# 5. 👇 СЕНИН КОДУҢ УШУЛ ЖЕРГЕ КЕЛЕТ
@bot.message_handler(func=lambda message: True)
def answer(message):

    if is_premium(message.from_user.id):
        max_tokens = 1200
    else:
        max_tokens = 400

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
            }
        )

        reply = response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        reply = "⚠️ Ката чыкты: " + str(e)

    bot.reply_to(message, reply)

# 6. RUN
if __name__ == "__main__":
    print("🔥 Tilek AI иштеп жатат...")
    bot.polling(none_stop=True)
