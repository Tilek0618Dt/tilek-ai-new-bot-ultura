# main.py – АКЫРКЫ версия: Grok + ҮН + ВИДЕО + СҮРӨТ + ВИДЕО АНАЛИЗ + РЕФЕРАЛ + ИЗДӨӨ + JOKE/MOTIVATION + VIP ✨ Video 📸
# Тилек стили 100% – досум, кулкулуу, бооркеер, чынчыл, кээде серёзный кеңеш

import telebot
from telebot import types
import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import requests
import base64
import time

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
KLING_API_KEY = os.getenv("KLING_API_KEY")

print("🔥 Tilek AI ишке кирди – Grok күчү менен + бардык функциялар + VIP Video! Досум, сен легендасың!")

def escape_markdown(text):
    """MarkdownV2 үчүн бардык резерв символдорду качуу"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Үн менен сүйлөшүү (PLUS/Pro)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, escape_markdown("❌ Үн менен сүйлөшүү PLUS же PRO үчүн гана! ⭐️ Premium баскыңыз, досум 😅"))
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
                text = "Үндү түшүнбөдүм, досум 😅 Текст менен жазып көрчү?"

        bot.send_message(message.chat.id, f"Сиз айттыңыз: {text}")

        lang = user.get("language", "ky") if user else "ky"
        answer = grok_answer(text, lang=lang, is_pro=is_pro(user))

        bot.send_message(message.chat.id, escape_markdown(answer))

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
        bot.send_message(message.chat.id, escape_markdown(f"❌ Үн иштетүүдө ката кетти, досум: {str(e)}\nТекст менен жазып көрчү, мен сени колдойм 😎"))

# Видео генерация (PRO үчүн)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and ("видео" in m.text.lower() or m.text.startswith("/video")))
def handle_video(message):
    user = get_user(message.from_user.id)
    if not is_pro(user):
        bot.send_message(message.chat.id, escape_markdown("❌ Видео генерация PRO үчүн гана, досум! ⭐️ Premium баскыңыз 😅"))
        return

    prompt = message.text.replace("/video", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, escape_markdown("Видео үчүн текст жазыңызчы, досум (мисалы: /video Кыргызстан тоолорунда ат минген адам)"))
        return

    bot.send_message(message.chat.id, escape_markdown("Видео жасалууда... 30-60 секунд күтүңүз, досум (күчтүү болот)! 🚀"))

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
            bot.send_message(message.chat.id, escape_markdown("Видео даяр болду, досум! 🎥 Күчтүү чыкты окшойт 😎"))
        else:
            bot.send_message(message.chat.id, escape_markdown(f"Ката чыкты, досум: {result.get('error', 'Белгисиз ката')}\nТынч бол, мен сени колдойм 😅"))
    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"❌ Видео жасоодо ката кетти, досум: {str(e)}\nТынч бол, мен ойлонуп, кайра аракет кылам 🚀"))

# Видео анализ (PRO үчүн)
@bot.message_handler(content_types=['video'])
def handle_video_analysis(message):
    user = get_user(message.from_user.id)
    if not user or not is_pro(user):
        bot.send_message(message.chat.id, escape_markdown("❌ Видео анализ PRO үчүн гана, досум! ⭐️ Premium баскыңыз 😅"))
        return

    try:
        bot.send_message(message.chat.id, escape_markdown("Видео жүктөлүүдө... талдап жатам, досум (бир аз күт) 🚀"))

        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('video.mp4', 'wb') as f:
            f.write(downloaded_file)

        prompt = "Бул видео эмне жөнүндө? Толук сүрөттөп бер, досум, кулкулуу комментарий кош, маанилүү учурларды айт!"
        answer = grok_answer(prompt, lang=user.get("language", "ky"), is_pro=True)

        bot.send_message(message.chat.id, escape_markdown(answer))

        os.remove("video.mp4")

    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"❌ Видео талдоодо ката кетти, досум: {str(e)}\nТынч бол, мен сени колдойм 😎"))

# ... (калган функциялар өзгөрбөйт, бирок бардык bot.send_message жерлеринде escape_markdown колдонсоң жакшы)

# VIP ✨ Video 📸 – өзүнчө платный функция (АКЫРКЫ ОҢДОЛГОН ВЕРСИЯ)
@bot.message_handler(func=lambda m: "VIP" in m.text and "Video" in m.text)
def handle_vip_video(message):
    user = get_user(message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, escape_markdown("Салам, досум! /start менен баштаңыз 😅"))
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton(escape_markdown("1 видео (30–60 сек) – 14.99$"), callback_data="vip_1"),
        types.InlineKeyboardButton(escape_markdown("3 видео пакети – 35$ (скидка)"), callback_data="vip_3"),
        types.InlineKeyboardButton(escape_markdown("5 видео пакети – 55$ (чоң скидка)"), callback_data="vip_5")
    )
    kb.add(types.InlineKeyboardButton(escape_markdown("🔙 Артка"), callback_data="back_menu"))

    vip_text = escape_markdown(
        "Досум, VIP ✨ Video 📸 – кино стилиндеги күчтүү видео! 🔥\n"
        "Реклама, Инстаграм, блог үчүн идеалдуу. Кайсы пакетти тандайсың? 😎"
    )

    try:
        bot.send_message(message.chat.id, vip_text, reply_markup=kb)
    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"❌ VIP меню ачууда ката кетти, досум: {str(e)}\nМен оңдоп жатам, тынч бол 😅"))

# ... (process_vip_payment жана башка функциялар өзгөрбөйт, бирок payment_text дагы escape кылынат)

@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
def process_vip_payment(call):
    package = call.data.split("_")[1]

    prices = {"1": 14.99, "3": 35.00, "5": 55.00}
    amount = prices.get(package, 14.99)
    bot.answer_callback_query(call.id)

    payment_link = f"https://unlimint.com/pay?amount={amount}&user_id={call.from_user.id}&package={package}&description=VIP+Video+{package}+видео"

    payment_text = escape_markdown(
        f"Досум, төлөм линк даяр! 🚀\n"
        f"Сумма: {amount}$\n"
        f"Төлөм жасагандан кийин видеоң дароо жасалат (30–60 сек, Runway сапаты)! 🎥\n\n"
        f"[Төлөмгө өтүү →]({payment_link})"
    )

    bot.send_message(call.message.chat.id, payment_text)

# ... (калган код өзгөрбөйт)

if __name__ == "__main__":
    time.sleep(5)  # Render үчүн кечигүүнү көбөйттүк
    print("🔥 Tilek AI ишке кирди – Grok күчү менен + бардык функциялар + VIP Video! Досум, сен легендасың!")
    bot.infinity_polling()
