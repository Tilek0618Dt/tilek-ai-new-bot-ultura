# main.py – акыркы версия + үн менен сүйлөшүү (voice handler кошулду!)

import telebot
from telebot import types
import os
import speech_recognition as sr  # үн → текст
from gtts import gTTS  # текст → үн
from pydub import AudioSegment  # ogg → wav конверт

from config import BOT_TOKEN
from users import get_user, save_user, set_plan
from countries import COUNTRIES
from languages import t
from grok_ai import grok_answer
from plans import is_plus, is_pro

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# Үн билдирүү үчүн recognizer
r = sr.Recognizer()

# Үн менен сүйлөшүү функциясы (voice handler)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Үн файлды жүктө
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('voice.ogg', 'wb') as f:
            f.write(downloaded_file)

        # OGG → WAV конверт
        sound = AudioSegment.from_ogg("voice.ogg")
        sound.export("voice.wav", format="wav")

        # Үн → текст (кыргызча)
        with sr.AudioFile("voice.wav") as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language="ky-KG")  # кыргызча
            except sr.UnknownValueError:
                text = "Үндү түшүнбөдүм, текст менен жазыңызчы 😅"
            except sr.RequestError:
                text = "Үн сервиси иштебей жатат, текст менен жазыңызчы"

        bot.send_message(message.chat.id, f"Сиз айттыңыз: {text}")

        # Grok'ко жөнөт
        user = get_user(message.from_user.id)
        lang = user.get("language", "ky") if user else "ky"
        answer = grok_answer(text, lang=lang, is_pro=is_pro(user))

        # Текст жооп
        bot.send_message(message.chat.id, answer)

        # Үн жооп (gTTS аркылуу – кыргызча үн)
        tts = gTTS(text=answer, lang='ky')
        tts.save("answer.mp3")
        bot.send_voice(message.chat.id, open("answer.mp3", "rb"))

        # Файлдарды тазала
        os.remove("voice.ogg")
        os.remove("voice.wav")
        os.remove("answer.mp3")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Үн иштетүүдө ката: {str(e)}\nТекст менен жазыңызчы 😅")

# Башка handler'лер (өзгөрүүсүз)
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
