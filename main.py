# main.py – АКЫРКЫ версия: Grok + ҮН + ВИДЕО + СҮРӨТ + РЕФЕРАЛ + ИЗДӨӨ + JOKE/MOTIVATION + VIP ✨ Video 📸

import telebot
from telebot import types
import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import requests
import base64

# PRO үчүн ElevenLabs
try:
    from elevenlabs import ElevenLabs, VoiceSettings
except ImportError:
    ElevenLabs = None

from config import BOT_TOKEN
from users import get_user, save_user, set_plan, add_referral, get_referral_code, check_bonus
from countries import COUNTRIES
from languages import t
from grok_ai import grok_answer
from plans import is_plus, is_pro

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MarkdownV2")

r = sr.Recognizer()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
KLING_API_KEY = os.getenv("KLING_API_KEY")  # же RUNWAY_API_KEY

# Үн менен сүйлөшүү (PLUS/Pro)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, "❌ Үн менен сүйлөшүү PLUS же PRO үчүн гана! ⭐️ Premium баскыңыз.")
        return

    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('voice.ogg', 'wb') as f:
            f.write(downloaded_file)

        sound = AudioSegment.from_ogg("voice.ogg")
        sound.export("voice.wav", format="wav")

        with sr.AudioFile("voice.wav") as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language="ky-KG")
            except:
                text = "Үндү түшүнбөдүм 😅 Текст менен жазыңызчы."

        bot.send_message(message.chat.id, f"Сиз айттыңыз: {text}")

        lang = user.get("language", "ky") if user else "ky"
        answer = grok_answer(text, lang=lang, is_pro=is_pro(user))

        bot.send_message(message.chat.id, answer)

        if is_pro(user) and ElevenLabs and ELEVENLABS_API_KEY:
            audio = ElevenLabs(api_key=ELEVENLABS_API_KEY).generate(
                text=answer,
                voice="Rachel",
                model="eleven_multilingual_v2"
            )
            with open("answer.mp3", "wb") as f:
                for chunk in audio:
                    f.write(chunk)
        else:
            tts = gTTS(text=answer, lang='ky')
            tts.save("answer.mp3")

        bot.send_voice(message.chat.id, open("answer.mp3", "rb"))

        os.remove("voice.ogg")
        os.remove("voice.wav")
        os.remove("answer.mp3")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Үн иштетүүдө ката: {str(e)}\nТекст менен жазыңызчы 😅")

# Видео генерация (PRO үчүн – Kling же Runway)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and ("видео" in m.text.lower() or m.text.startswith("/video")))
def handle_video(message):
    user = get_user(message.from_user.id)
    if not is_pro(user):
        bot.send_message(message.chat.id, "❌ Видео генерация PRO үчүн гана! ⭐️ Premium баскыңыз.")
        return

    prompt = message.text.replace("/video", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, "Видео үчүн текст жазыңыз, досум (мисалы: /video Кыргызстан тоолору)")
        return

    bot.send_message(message.chat.id, "Видео жасалууда... 30-60 секунд күтүңүз 🚀")

    try:
        headers = {"Authorization": f"Bearer {KLING_API_KEY}"}
        payload = {
            "prompt": prompt,
            "duration": 10,
            "resolution": "720p"
        }
        response = requests.post("https://api.kling.ai/v1/video/generate", json=payload, headers=headers)
        result = response.json()

        if "video_url" in result:
            bot.send_video(message.chat.id, result["video_url"])
            bot.send_message(message.chat.id, "Видео даяр! 🎥")
        else:
            bot.send_message(message.chat.id, f"Ката: {result.get('error', 'Белгисиз ката')}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Видео жасоодо ката: {str(e)}\nДосум, тынч бол, мен сени колдойм! 😅")

# Сүрөт тануу + анализ (PLUS/Pro)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, "❌ Сүрөт тануу PLUS же PRO үчүн гана! ⭐️ Premium баскыңыз.")
        return

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('photo.jpg', 'wb') as f:
            f.write(downloaded_file)

        lang = user.get("language", "ky") if user else "ky"
        prompt = "Бул сүрөттү толук сүрөттөп бер, кулкулуу жана чынчыл комментарий кош. Эмне бар, кандай маанай, эмнеге окшош?"
        answer = grok_answer(prompt, lang=lang, is_pro=is_pro(user), image_path='photo.jpg')

        bot.send_message(message.chat.id, answer)

        os.remove("photo.jpg")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Сүрөт танууда ката: {str(e)}\nТекст менен жазыңызчы, досум 😅")

# Сүрөт жасоо (PRO үчүн)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and m.text.startswith("/image"))
def handle_image_gen(message):
    user = get_user(message.from_user.id)
    prompt = message.text.replace("/image", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, "Сүрөт үчүн текст жазыңыз, досум (мисалы: /image Кыргызстан тоолору)")
        return

    bot.send_message(message.chat.id, "Сүрөт жасалууда... 10-30 секунд күтүңүз 🚀")

    try:
        answer = grok_answer(f"Сүрөт жасап бер: {prompt}", lang=user.get("language", "ky"), is_pro=True)
        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Сүрөт жасоодо ката: {str(e)}\nДосум, тынч бол, мен сени колдойм! 😅")

# Интернет издөө (PRO үчүн)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and ("?" in m.text or "издөө" in m.text.lower()))
def handle_search(message):
    user = get_user(message.from_user.id)
    query = message.text.strip()
    bot.send_message(message.chat.id, "Издеп жатам, досум... 5-10 секунд күтүңүз 🚀")

    try:
        answer = grok_answer(f"Интернеттен издөө: {query}", lang=user.get("language", "ky"), is_pro=True)
        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Издөөдө ката: {str(e)}\nДосум, тынч бол, мен сени колдойм! 😅")

# Реферал система
@bot.message_handler(commands=['ref', 'referral'])
def handle_referral(message):
    user = get_user(message.from_user.id)
    code = get_referral_code(message.from_user.id)
    bot.send_message(message.chat.id, f"Досум, чындыкты түз айтайын – сенин реферал кодуң: {code}\n5 дос чакырсаң 1 жума бекер PLUS ачылат! 😎 Досторуңа жөнөт!")

# Кошумча кулкулуу функциялар (PRO үчүн)
@bot.message_handler(commands=['joke'])
def handle_joke(message):
    user = get_user(message.from_user.id)
    if not is_pro(user):
        bot.send_message(message.chat.id, "❌ Joke функциясы PRO үчүн гана! ⭐️ Premium баскыңыз 😅")
        return
    answer = grok_answer("Күлкүлүү анекдот айт, досум", lang=user.get("language", "ky"), is_pro=True)
    bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['motivation'])
def handle_motivation(message):
    user = get_user(message.from_user.id)
    if not is_pro(user):
        bot.send_message(message.chat.id, "❌ Motivation функциясы PRO үчүн гана! ⭐️ Premium баскыңыз 😅")
        return
    answer = grok_answer("Мотивациялык сөз айт, досум", lang=user.get("language", "ky"), is_pro=True)
    bot.send_message(message.chat.id, answer)

# VIP ✨ Video 📸 – өзүнчө платный функция
@bot.message_handler(func=lambda m: m.text == "VIP ✨ Video 📸" or m.text.startswith("/vipvideo"))
def handle_vip_video(message):
    user = get_user(message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "Салам, досум! /start менен баштаңыз 😅")
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("1 видео (30–60 сек) – 14.99$", callback_data="vip_1"),
        types.InlineKeyboardButton("3 видео пакети – 35$ (скидка!)", callback_data="vip_3"),
        types.InlineKeyboardButton("5 видео пакети – 55$ (чоң скидка!)", callback_data="vip_5")
    )
    kb.add(types.InlineKeyboardButton("🔙 Артка", callback_data="back_menu"))

    bot.send_message(message.chat.id, 
        "Досум, VIP ✨ Video 📸 – кино стилиндеги күчтүү видео! 🔥\n"
        "Реклама, Инстаграм, блог үчүн идеалдуу. Кайсы пакетти тандайсың? 😎",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
def process_vip_payment(call):
    package = call.data.split("_")[1]

    prices = {
        "1": 14.99,
        "3": 35.00,
        "5": 55.00
    }

    amount = prices.get(package, 14.99)
    bot.answer_callback_query(call.id)

    # Unlimint төлөм линк (верификация бүткөндө реалдуу иштейт)
    payment_link = f"https://unlimint.com/pay?amount={amount}&user_id={call.from_user.id}&package={package}&description=VIP+Video+{package}+видео"
    
    bot.send_message(call.message.chat.id, 
        f"Досум, төлөм линк даяр! 🚀\n"
        f"Сумма: {amount}$\n"
        f"Төлөм жасагандан кийин видеоң дароо жасалат (30–60 сек, Runway сапаты)! 🎥\n\n"
        f"[Төлөмгө өтүү →]({payment_link})",
        parse_mode="MarkdownV2"
    )

@bot.callback_query_handler(func=lambda c: c.data == "back_menu")
def back_to_menu(call):
    bot.answer_callback_query(call.id)
    show_menu(call.message)

# Башка handler'лер
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if user and user.get("language"):
        show_menu(message)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, c in COUNTRIES.items():
        markup.add(types.InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{code}"))

    bot.send_message(message.chat.id, "🌍 Өлкөңүздү тандаңыз / Choose your country:", reply_markup=markup)

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
    kb.add("VIP ✨ Video 📸")  # VIP Video баскычы кошулду

    menu_text = t('menu_ready', lang).replace('*', '\\*').replace('_', '\\_')
    bot.send_message(message.chat.id, menu_text, reply_markup=kb)

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
    text = t('menu_ready', lang) + "\n\n💎 Премиум пландар:\n\n⭐️ PLUS – безлимит + тез жооп + үн менен сүйлөшүү + сүрөт анализ\n👑 PRO – бардык функциялар + видео генерация + супер үн + сүрөт жасоо"
    bot.send_message(message.chat.id, text, reply_markup=kb)

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
        bot.send_message(message.chat.id, "🆘 Жардам\n\nБул бот Grok күчү менен иштейт. Суроо бериңиз – чынчыл жана акылдуу жооп аласыз!\n\nПремиум пландар үчүн ⭐️ Premium баскыла.")
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

    bonus_msg = check_bonus(message.from_user.id)
    if bonus_msg:
        bot.send_message(message.chat.id, bonus_msg)

    lang = user["language"]
    is_pro_user = is_pro(user)

    answer = grok_answer(message.text, lang=lang, is_pro=is_pro_user)

    if is_plus(user):
        answer += "\n\n⚡️ PLUS режим: тез жана безлимит"
    if is_pro(user):
        answer += "\n\n👑 PRO режим: эң күчтүү Grok + бардык функциялар"

    # MarkdownV2 үчүн коопсуз кылуу
    answer = answer.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')
    bot.send_message(message.chat.id, answer)

if __name__ == "__main__":
    print("🔥 Tilek AI ишке кирди – Grok күчү менен + бардык функциялар + VIP Video!")
    bot.infinity_polling()
    
