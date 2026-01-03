
import telebot
from telebot import types
from users import get_user, save_user
from languages import COUNTRIES
from plans import get_plan, set_plan
from premium import handle_premium

BOT_TOKEN = "СЕНИН_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# =========================
# /start → ӨЛКӨ ТАНДОО
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user:
        show_main_menu(message.chat.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, data in list(COUNTRIES.items())[:350]:  # 350+ өлкө
        markup.add(
            types.InlineKeyboardButton(f"{data['flag']} {data['name']}", callback_data=f"country_{code}")
        )

    bot.send_message(message.chat.id, "🌍 *Өлкөңүздү тандаңыз:*", reply_markup=markup)

# =========================
# ӨЛКӨ САКТОО
# =========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def save_country(call):
    country_code = call.data.split("_")[1]
    country = COUNTRIES[country_code]

    save_user(user_id=call.from_user.id, country=country_code, language=country['lang'], plan="free")
    bot.answer_callback_query(call.id, "✅ Сакталды")
    show_main_menu(call.message.chat.id)

# =========================
# БАШКЫ МЕНЮ
# =========================
def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💬 Суроо берүү")
    markup.add("⭐️ Premium", "🌐 Тилди өзгөртүү")
    markup.add("ℹ️ Мүмкүнчүлүктөр", "🆘 Жардам")
    bot.send_message(chat_id, "🤖 *Tilek AI даяр!*", reply_markup=markup)

# =========================
# PREMIUM МЕНЮ
# =========================
@bot.message_handler(func=lambda m: m.text == "⭐️ Premium")
def premium_menu(message):
    handle_premium(bot, message.chat.id, message.from_user.id)

# =========================
# START BOT
# =========================
print("🔥 Tilek AI старт алды")
bot.infinity_polling()
