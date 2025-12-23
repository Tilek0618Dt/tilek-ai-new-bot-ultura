import telebot
import requests
import os
from premium import register_handlers, is_premium, add_free_usage, free_usage_left

# ТОКЕНДЕР
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
bot = telebot.TeleBot(BOT_TOKEN)

# PREMIUM логикасын кошуу
register_handlers(bot)

SYSTEM_PROMPT = """
Сен — Тилек AI, Кыргызстандын биринчи толук кыргызча жасалма интеллектисиң.
Кыргызча, орусча, англисче сүйлөйсүң.
"""

# Free лимит + AI жооп
@bot.message_handler(func=lambda message: True)
def answer(message):
    user_id = message.from_user.id

    if is_premium(user_id):
        plan = premium_users[user_id]
        if plan == "Plus":
            max_tokens = 1200
        elif plan == "Pro":
            max_tokens = 2000
        else:
            max_tokens = 400
    else:
        add_free_usage(user_id)
        if free_usage_left(user_id) <= 0:
            bot.reply_to(message, "⚠️ Free лимити бүткөн! Premium сатып алыңыз")
            return
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
            },
            timeout=60
        )
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"⚠️ Ката чыкты: {e}"

    bot.reply_to(message, reply)

# RUN
if __name__ == "__main__":
    print("🔥 Tilek AI иштеп жатат...")
    bot.polling(none_stop=True)
