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
from users import get_user, save_user, set_plan, add_referral, get_referral_code, check_bonus, users  # users сөздүгүн импорттодук!
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

# Free лимит – 20 суроо/күн, 4 саат күтүү менен жаңылануу
FREE_DAILY_LIMIT = 20
FREE_RESET_HOURS = 4

def get_free_query_count(user_id):
    user = get_user(user_id)
    if user["plan"] != "free":
        return 0

    last_reset = user.get("free_last_reset", 0)
    now = int(time.time())
    if now - last_reset > FREE_RESET_HOURS * 3600:
        user["free_query_count"] = 0
        user["free_last_reset"] = now
        save_user(user_id, user.get("country"), user.get("language"))
    return user.get("free_query_count", 0)

def increment_free_query(user_id):
    user = get_user(user_id)
    if user["plan"] == "free":
        count = user.get("free_query_count", 0) + 1
        user["free_query_count"] = count
        save_user(user_id, user.get("country"), user.get("language"))
        return count
    return 0

def check_free_limit(user_id, message):
    user = get_user(user_id)
    if user["plan"] != "free":
        return True

    count = get_free_query_count(user_id)
    if count >= FREE_DAILY_LIMIT:
        reset_time = user.get("free_last_reset", 0) + FREE_RESET_HOURS * 3600
        remaining = max(0, int((reset_time - time.time()) / 3600))
        bot.send_message(message.chat.id, escape_markdown(
            f"Досум, Free лимит түгөндү (20 суроо/күн)! 😅\n\n"
            f"4 саат күтсөң – кайра 20 суроо ачылат (же калган {remaining} саат).\n\n"
            "⭐️ Premium сатып алсаң – безлимит + күчтүү функциялар! 8$/ай\n"
            "👑 PRO – бардык күч! 18$/ай\n\n"
            "https://ecommpay.com/pay?amount=8&description=PLUS+Tilek+AI\n"
            "https://ecommpay.com/pay?amount=18&description=PRO+Tilek+AI"
        ))
        return False
    return True

# Биринчи /start – каналга милдеттүү катталуу сунушу + тил тандоо + реферал иштетүү
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    referrer_code = args[1] if len(args) > 1 else None

    user = get_user(user_id)

    # Реферал код менен келгенби? – санды +1 кош
    if referrer_code and referrer_code.startswith("TILEK"):
        referrer_id = None
        for uid, u in users.items():
            if u.get("referral_code") == referrer_code:
                referrer_id = int(uid)
                break

        if referrer_id and referrer_id != user_id:
            added = add_referral(referrer_id)
            if added:
                bot.send_message(user_id, escape_markdown("✅ Досум чакырганың үчүн рахмат! Реферал саны жаңыланды! 🎉"))
            else:
                bot.send_message(user_id, escape_markdown("Реферал кошулду, бирок бонус али жок 😅"))

    if user and user.get("language"):
        show_menu(message)
        return
# Биринчи жолу – канал сунушу + өлкө тандоо
    channel_text = escape_markdown(
        "🤖 Салам, досум! Мен Tilek AI – сенин күчтүү досуңмун 😎❤️\n\n"
        "Ботту толук колдонуу үчүн менин каналыма милдеттүү катталышың керек!\n"
        "Катталсаң – жаңылыктар, бонустар, күчтүү видео жана сюрприздер алдыңкы болуп келет! 🚀\n\n"
        "t.me/Tilek_Ai  ← Каттал дагы кайра /start бас! ❤️\n\n"
        "Эми өлкөңүздү тандаңыз – бот ошол тилге өтөт!"
    )
    bot.send_message(message.chat.id, channel_text)

    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, c in COUNTRIES.items():
        markup.add(types.InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{code}"))

    bot.send_message(message.chat.id, escape_markdown("🌍 Өлкөңүздү тандаңыз:"), reply_markup=markup)

# Тил тандоо (өлкө тандаганда)
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

# Меню кооз версиясы
def show_menu(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ky") if user else "ky"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("💬 Суроо берүү", "🌐 Тил өзгөртүү")
    kb.add("🆘 Жардам", "🫂 Реферал")
    kb.add("⭐️ Premium", "VIP ✨ Video 📸")

    menu_text = escape_markdown(
        t("menu_ready", lang) + "\n\n" +
        "Tilek AI – сенин күчтүү досуң ❤️\n" +
        "Алла жар болсун! 🤲🏻"
    )

    bot.send_message(message.chat.id, menu_text, reply_markup=kb)

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

# Видео анализ (PRO үчүн)
@bot.message_handler(content_types=['video'])
def handle_video_analysis(message):
    user = get_user(message.from_user.id)
    if not user or not is_pro(user):
        bot.send_message(message.chat.id, escape_markdown(t("video_analysis_pro_required", user.get("language", "ky"))))
        return

    try:
        bot.send_message(message.chat.id, escape_markdown(t("video_analyzing", user.get("language", "ky"))))

        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('video.mp4', 'wb') as f:
            f.write(downloaded_file)

        prompt = t("video_analysis_prompt", user.get("language", "ky"))
        answer = grok_answer(prompt, lang=user.get("language", "ky"), is_pro=True)

        bot.send_message(message.chat.id, escape_markdown(answer))

        os.remove("video.mp4")

    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"{t('video_analysis_error', user.get('language', 'ky'))}: {str(e)}"))

# Сүрөт тануу + анализ (PLUS/Pro)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user = get_user(message.from_user.id)
    if not user or not is_plus(user):
        bot.send_message(message.chat.id, escape_markdown(t("photo_plus_required", user.get("language", "ky"))))
        return

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('photo.jpg', 'wb') as f:
            f.write(downloaded_file)

        lang = user.get("language", "ky")
        prompt = t("photo_analysis_prompt", lang)
        answer = grok_answer(prompt, lang=lang, is_pro=is_pro(user), image_path='photo.jpg')

        bot.send_message(message.chat.id, escape_markdown(answer))

        os.remove("photo.jpg")

    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"{t('photo_analysis_error', user.get('language', 'ky'))}: {str(e)}"))

# Сүрөт жасоо (PRO үчүн)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and m.text.startswith("/image"))
def handle_image_gen(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ky")
    prompt = message.text.replace("/image", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, escape_markdown(t("image_prompt_needed", lang)))
        return

    bot.send_message(message.chat.id, escape_markdown(t("image_generating", lang)))

    try:
        answer = grok_answer(f"Сүрөт жасап бер: {prompt}", lang=lang, is_pro=True)
        bot.send_message(message.chat.id, escape_markdown(answer))
    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"{t('image_error', lang)}: {str(e)}"))

# Интернет издөө (PRO үчүн)
@bot.message_handler(func=lambda m: is_pro(get_user(m.from_user.id)) and ("?" in m.text or "издөө" in m.text.lower()))
def handle_search(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ky")
    query = message.text.strip()
    bot.send_message(message.chat.id, escape_markdown(t("searching", lang)))

    try:
        answer = grok_answer(f"Интернеттен издөө: {query}", lang=lang, is_pro=True)
        bot.send_message(message.chat.id, escape_markdown(answer))
    except Exception as e:
        bot.send_message(message.chat.id, escape_markdown(f"{t('search_error', lang)}: {str(e)}"))

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
        bonus_msg = escape_markdown(f"\n\n✅ 5 дос чакырдың, досум! 🎉 1 жума бекер PLUS ачылды! Сен легендасың ❤️🚀")

    text = escape_markdown(
        f"🫂 Досум, досторуңду чакыр! 😎\n\n"
        f"Ботко: https://t.me/tilek_ai_bot?start={code}\n"
        f"Каналга: https://t.me/Tilek_Ai\n\n"
        f"5 дос чакырсаң + каналга катталсаң – 1 жума бекер PLUS ачылат! 🔥\n"
        f"Азыр реферал саның: {referral_count}/5\n"
        f"{bonus_msg}"
    )

    bot.send_message(message.chat.id, text)

# /ref командасын толук өчүрүү
@bot.message_handler(commands=['ref', 'referral'])
def ignore_ref(message):
    pass

# VIP ✨ Video 📸 – ECOMMPAY МЕНЕН
@bot.message_handler(func=lambda m: "VIP" in m.text and "Video" in m.text)
def handle_vip_video(message):
    user = get_user(message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, escape_markdown(t("start_needed", user.get("language", "ky"))))
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("1 видео (30–60 сек) – 14.99$", url="https://ecommpay.com/pay?amount=14.99&description=VIP+Video+1"),
        types.InlineKeyboardButton("3 видео пакети – 35$ (скидка)", url="https://ecommpay.com/pay?amount=35&description=VIP+Video+3"),
        types.InlineKeyboardButton("5 видео пакети – 55$ (чоң скидка)", url="https://ecommpay.com/pay?amount=55&description=VIP+Video+5")
    )
    kb.add(types.InlineKeyboardButton("🔙 Артка", callback_data="back_menu"))

    vip_text = escape_markdown(
        "Досум, VIP ✨ Video 📸 – кино стилиндеги күчтүү видео! 🔥\n"
        "Реклама, Инстаграм, блог, TikTok үчүн идеалдуу. Кайсы пакетти тандайсың? 😎\n\n"
        "Төлөм Ecommpay аркылуу – коопсуз, тез жана ыңгайлуу!\n"
        "Төлөсөң – дароо укмуш видеоң даяр болот! 🎥❤️"
    )

    bot.send_message(message.chat.id, vip_text, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
def process_vip_payment(call):
    package = call.data.split("_")[1]
    prices = {"1": 14.99, "3": 35.00, "5": 55.00}
    amount = prices.get(package, 14.99)
    bot.answer_callback_query(call.id)

    payment_link = f"https://ecommpay.com/pay?amount={amount}&description=VIP+Video+{package}"

    payment_text = escape_markdown(
        f"Досум, төлөм линк даяр! 🚀\n"
        f"Сумма: {amount}$\n"
        f"Төлөм жасагандан кийин видеоң дароо жасалат (30–60 сек, кино сапаты)! 🎥\n\n"
        f"[Төлөмгө өтүү →]({payment_link})"
    )

    bot.send_message(call.message.chat.id, payment_text)

@bot.callback_query_handler(func=lambda c: c.data == "back_menu")
def back_to_menu(call):
    bot.answer_callback_query(call.id)
    show_menu(call.message)

# ЖАҢЫ ЖАРДАМ МЕНЮСУ – 2 АДМИН МЕНЕН
@bot.message_handler(func=lambda m: "Жардам" in m.text or "🆘" in m.text)
def handle_help(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ky") if user else "ky"

    help_text = escape_markdown(
        "🆘 Жардам панели\n\n"
        "Боттун бардык функциялары жөнүндө сурооңуз болсо – мен дайым жардам берем! 😎\n\n"
        "Админ менен байланыш:\n"
        "1) @Mentor_006T – жардам берүүчү легенда! 🚀\n"
        "2) @Timka_Bro999 – күчтүү колдоо жана кеңештер! ❤️\n\n"
        "Кандай жардам керек, досум? Жазсаң – дароо жооп берем! 🤲🏻"
    )

    bot.send_message(message.chat.id, help_text)

# PREMIUM МЕНЮСУ – ECOMMPAY СЫЛКАСЫ МЕНЕН
@bot.message_handler(func=lambda m: m.text == "⭐️ Premium")
def premium(message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ky") if user else "ky"

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("⭐️ PLUS – 8$/ай", url="https://ecommpay.com/pay?amount=8&description=PLUS+Tilek+AI"),
        types.InlineKeyboardButton("👑 PRO – 18$/ай", url="https://ecommpay.com/pay?amount=18&description=PRO+Tilek+AI")
    )
    kb.add(types.InlineKeyboardButton("🔙 Артка", callback_data="back"))

    text = escape_markdown(
        t("premium_title", lang) + "\n\n" +
        "⭐️ PLUS – безлимит + тез жооп + үн менен сүйлөшүү + сүрөт анализ\n" +
        "👑 PRO – бардык функциялар + видео генерация + супер үн + сүрөт жасоо\n\n" +
        "Төлөм Ecommpay аркылуу – коопсуз жана тез! 🚀\n"
        "Төлөсөң – дароо активдештирем, досум! Сен легендасың ❤️"
    )

    bot.send_message(message.chat.id, text, reply_markup=kb)

# Суроо берүү – Free лимит + реклама
@bot.message_handler(content_types=["text"])
def chat(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user or not user.get("language"):
        start(message)
        return

    # Free лимит текшер
    if not check_free_limit(user_id, message):
        return

    lang = user["language"]
    bonus_msg = check_bonus(user_id)
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

    # Free лимитти +1 кошу
    increment_free_query(user_id)

if __name__ == "__main__":
    time.sleep(5)
    print("🔥 Tilek AI ишке кирди – Grok күчү менен + бардык функциялар + VIP Video! Досум, сен легендасың!")
    bot.infinity_polling()

    



    









        


    





    



