# grok_ai.py – эски, бирок ишенимдүү версия (proxies катасы жок)

import os
import openai  # эски импорт

# API key
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY жок!")

# Туура настройка
openai.api_key = GROK_API_KEY
openai.base_url = "https://api.x.ai/v1"  # жаңы версияда api_base деп аталат

def grok_answer(text, lang="ky", is_pro=False):
    model = "grok-4" if is_pro else "grok-4-fast"

    system_prompt = (
        "Сен күчтүү, чынчыл жана акылдуу AI жардамчысың – Grok сыяктуу. "
        "Цензурасыз, түз жана күлкүлүү жооп бер. "
        f"Жоопту толугу менен {lang} тилинде гана бер."
    )

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.9,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Ката: {str(e)} (API key же интернет текшериңиз)"
