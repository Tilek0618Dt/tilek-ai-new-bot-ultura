from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import json

from countries import COUNTRIES

TOKEN = "BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def save_user(user_id, country, lang):
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    users[str(user_id)] = {
        "country": country,
        "lang": lang,
        "plan": "free"
    }

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)

    for c in COUNTRIES[:20]:  # азыр 20, кийин пагинация
        kb.add(
            InlineKeyboardButton(
                text=c["name"],
                callback_data=f"country_{c['code']}"
            )
        )

    await message.answer(
        "🌍 Choose your country (350+ available):",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda call: call.data.startswith("country_"))
async def country_selected(call: types.CallbackQuery):
    code = call.data.split("_")[1]

    country = next(c for c in COUNTRIES if c["code"] == code)

    save_user(
        call.from_user.id,
        country["name"],
        country["lang"]
    )

    await call.message.answer(
        f"✅ Country selected: {country['name']}\n"
        f"🌐 Language set automatically"
    )

if __name__ == "__main__":
    executor.start_polling(dp)
