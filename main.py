# main.py – АКЫРКЫ версия: Grok + ҮН (PLUS/Pro) + ВИДЕО (PRO) + СҮРӨТ ТАНУУ/ЖАСОО (PLUS/Pro) + РЕФЕРАЛ + ИЗДӨӨ + JOKE/MOTIVATION

import telebot
from telebot import types
import os
import speech_recognition as sr  # үн → текст
from gtts import gTTS  # текст → үн (PLUS үчүн)
from pydub import AudioSegment  # ogg → wav
import requests  # Kling/Runway үчүн
import base64  # сүрөттү base64'ке айлантуу үчүн

# PRO үчүн ElevenLabs (супер сапаттагы үн)
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

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# Үн үчүн recognizer
r = sr.Recognizer()

# API key'лер (Render Environment Variables'тен алынат)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
KLING_API_KEY = os.getenv("KLING_API_KEY")  # же Runway API key

# Үн билдирүү handler (PLUS/Pro үчүн гана)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, "❌ Үн менен сүйлөшүү PLUS (8\( ) же PRO (18 \)) үчүн гана! ⭐️ Premium баскыңыз.")
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

        # Үн жооп
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

# Видео генерация (PRO үчүн гана)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and ("видео" in m.text.lower() or m.text.startswith("/video")))
def handle_video(message):
    user = get_user(message.from_user.id)
    if not is_pro(user):
        bot.send_message(message.chat.id, "❌ Видео генерация PRO (18$) үчүн гана! ⭐️ Premium баскыңыз.")
        return

    prompt = message.text.replace("/video", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, "Видео үчүн текст жазыңыз, досум (мисалы: /video Кыргызстан тоолорунда ат минген адам)")
        return

    bot.send_message(message.chat.id, "Видео жасалууда... 30-60 секунд күтүңүз 🚀")

    try:
        headers = {"Authorization": f"Bearer {os.getenv('KLING_API_KEY')}"}
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

# Сүрөт тануу + анализ (PLUS/Pro үчүн гана)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, "❌ Сүрөт тануу + анализ PLUS (8\( ) же PRO (18 \)) үчүн гана! ⭐️ Premium баскыңыз, досум 😅")
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

# Сүрөт жасоо (PRO үчүн гана)
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
        bot.send_message(message.chat.id, answer)  # Эгер URL келсе – bot.send_photo(answer)
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

# Башка handler'лер (өзгөрүүсүз калды)
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
    text = "*💎 Премиум пландар:*\n\n⭐️ PLUS – безлимит + тез жооп + үн менен сүйлөшүү + сүрөт анализ\n👑 PRO – бардык функциялар + видео генерация + супер үн + сүрөт жасоо"
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

    # Бонус убактысын текшер
    bonus_msg = check_bonus(message.from_user.id)
    if bonus_msg:
        bot.send_message(message.chat.id, bonus_msg)

    lang = user["language"]
    is_pro_user = is_pro(user)

    answer = grok_answer(message.text, lang=lang, is_pro=is_pro_user)

    if is_plus(user):
        answer += "\n\n⚡️ *PLUS режим: тез жана безлимит*"
    if is_pro(user):
        answer += "\n\n👑 *PRO режим: эң күчтүү Grok + бардык функциялар*"

    bot.send_message(message.chat.id, answer) 

print("🔥 Tilek AI ишке кирди – Grok күчү менен + бардык функциялар!")
bot.infinity_polling()
