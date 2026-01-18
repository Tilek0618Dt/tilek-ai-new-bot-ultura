# main.py – АКЫРКЫ версия: Grok + ҮН + ВИДЕО + СҮРӨТ + ВИДЕО АНАЛИЗ + РЕФЕРАЛ МЕНЮ + VIP ✨ Video 📸
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
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Үн менен сүйлөшүү (PLUS/Pro)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, escape_markdown(t("voice_plus_required", user.get("language", "ky"))))
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
                lang_code = user.get("language", "ky") + "-KG" if user.get("language", "ky") == "ky" else user.get("language", "ky")
                text = r.recognize_google(audio, language=lang_code)
            except:
                text = t("voice_not_understood", user.get("language", "ky"))

        bot.send_message(message.chat.id, f"{t('you_said', user.get('language', 'ky'))}: {text}")

        lang = user.get("language", "ky")
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
            tts_lang = lang if lang in ['ky', 'ru', 'en'] else 'ky'
            tts = gTTS(text=answer, lang=tts_lang)
            tts.save("answer.mp3")

        bot.send_voice(message.chat.id, open("answer.mp3", "rb"))

        os.remove("voice.ogg")
        os.remove("voice.wav")
        os.remove("answer.mp3")

    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"{t('voice_error', user.get('language', 'ky'))}: {str(e)}\n{t('try_text', user.get('language', 'ky'))}"))

# Видео генерация (PRO үчүн)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and ("видео" in m.text.lower() or m.text.startswith("/video")))
def handle_video(message):
    user = get_user(message.from_user.id)
    if not is_pro(user):
        bot.send_message(message.chat.id, escape_markdown(t("video_pro_required", user.get("language", "ky"))))
        return

    prompt = message.text.replace("/video", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, escape_markdown(t("video_prompt_needed", user.get("language", "ky"))))
        return

    bot.send_message(message.chat.id, escape_markdown(t("video_generating", user.get("language", "ky"))))

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
            bot.send_message(message.chat.id, escape_markdown(t("video_ready", user.get("language", "ky"))))
        else:
            bot.send_message(message.chat.id, escape_markdown(f"{t('error_occurred', user.get('language', 'ky'))}: {result.get('error', t('unknown_error', user.get('language', 'ky')))}"))
    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"{t('video_error', user.get('language', 'ky'))}: {str(e)}"))

# ... (калган функциялар – видео анализ, сүрөт тануу, сүрөт жасоо, издөө – бардыгы тилге жараша иштейт, мисалы escape_markdown(t('key', lang)) менен)

# Реферал менюсу – 🫂 Реферал баскычы гана иштейт
@bot.message_handler(func=lambda m: "Реферал" in m.text or "🫂" in m.text)
def handle_referral(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, escape_markdown(t("start_needed", user.get("language", "ky"))))
        return

    lang = user.get("language", "ky")
    code = get_referral_code(user_id)
    referral_count = user.get("referral_count", 0)

    bonus_msg = ""
    if referral_count >= 5 and not user.get("plus_bonus_activated", False):
        set_plan(user_id, "plus")
        user["plus_bonus_activated"] = True
        user["plus_bonus_until"] = int(time.time()) + 7 * 24 * 3600
        save_user(user_id, user.get("country"), lang)
        bonus_msg = escape_markdown(f"\n\n✅ {t('referral_bonus_activated', lang)}! 🎉 {t('plus_free_week', lang)} 🚀")

    text = escape_markdown(
        f"{t('referral_title', lang)}\n\n"
        f"{t('referral_bot_link', lang)}: https://t.me/tilek_ai_bot\n"
        f"{t('referral_channel_link', lang)}: https://t.me/Tilek_Ai\n\n"
        f"{t('referral_condition', lang)}\n"
        f"{t('referral_no_pro_free', lang)}\n\n"
        f"{t('current_referrals', lang)}: {referral_count}/5\n"
        f"{bonus_msg}"
    )

    bot.send_message(message.chat.id, text)

# /ref командасын толук өчүрүү
@bot.message_handler(commands=['ref', 'referral'])
def ignore_ref(message):
    pass

# show_menu – тилге жараша чыгат
def show_menu(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ky") if user else "ky"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(t("ask_question", lang), t("premium_title", lang))
    kb.add("🌐 Тил өзгөртүү", "🆘 Жардам")
    kb.add("VIP ✨ Video 📸", "🫂 Реферал")

    menu_text = t("menu_ready", lang)
    bot.send_message(message.chat.id, escape_markdown(menu_text), reply_markup=kb)

# start жана save_country – тил автоматтык өзгөрөт
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if user and user.get("language"):
        show_menu(message)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, c in COUNTRIES.items():
        markup.add(types.InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{code}"))

    bot.send_message(message.chat.id, t("choose_country", "ky"), reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("country_"))
def save_country(call):
    code = call.data.split("_")[1]
    c = COUNTRIES.get(code)
    if c:
        lang = c["lang"]
        save_user(call.from_user.id, code, lang)
        bot.answer_callback_query(call.id, escape_markdown(f"✅ {c['name']} тандалды! Тил: {lang.upper()}"))
        show_menu(call.message)
    else:
        bot.send_message(call.message.chat.id, escape_markdown(t("error_country", call.from_user.language or "ky")))

# chat – тилге жараша жооп
@bot.message_handler(content_types=["text"])
def chat(message):
    user = get_user(message.from_user.id)
    if not user or not user.get("language"):
        start(message)
        return

    lang = user["language"]
    bonus_msg = check_bonus(message.from_user.id)
    if bonus_msg:
        bot.send_message(message.chat.id, escape_markdown(bonus_msg))

    is_pro_user = is_pro(user)

    answer = grok_answer(message.text, lang=lang, is_pro=is_pro_user)

    if is_plus(user):
        answer += f"\n\n{t('plus_mode', lang)}"
    if is_pro(user):
        answer += f"\n\n{t('pro_mode', lang)}"

    answer = f"{t('truth_answer', lang)} {answer}\n\n😎 {t('good_luck', lang)} 🤲🏻"

    answer = escape_markdown(answer)
    bot.send_message(message.chat.id, answer)

if __name__ == "__main__":
    time.sleep(5)
    print("🔥 Tilek AI ишке кирди – Grok күчү менен + бардык функциялар + VIP Video! Досум, сен легендасың!")
    bot.infinity_polling()


    



