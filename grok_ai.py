import os
import openai

# 🔑 Grok API Key (xAI'дан алган key'иңди кой)
GROK_API_KEY = os.getenv("GROK_API_KEY")  # терминалда: export GROK_API_KEY="xai-..."

# Grok API'нин endpoint'и (OpenAI форматы менен шайкеш)
openai.api_key = GROK_API_KEY
openai.api_base = "https://api.x.ai/v1"  # Бул эң маанилүүсү!

def grok_answer(text, lang="ky"):
    """
    Grok (xAI) жооп берет.
    text — суроо
    lang — тил (ky, ru, en, ж.б.)
    """
    try:
        response = openai.ChatCompletion.create(
            model="grok-4",  # же "grok-4-fast" (тезирээк), "grok-3" же "grok-3-mini"
            messages=[
                {"role": "system", "content": f"Сен күчтүү жана чынчыл AI жардамчысың. Жоопту {lang} тилинде гана бер."},
                {"role": "user", "content": text}
            ],
            temperature=0.8,
            max_tokens=1000,  # Grok көбүрөөк токенди колдойт
            # топ_reasoning=True  # эгер Thinking режим керек болсо (кээ бир моделдерде бар)
        )

        answer = response.choices[0].message.content.strip()
        return f"🤖 Grok жооп берди:\n\n{answer}"

    except Exception as e:
        return f"❌ Ката чыкты: {str(e)}"

# Тест үчүн
if name == "main":
    savol = input("Сурооңузду жазыңыз: ")
    print(grok_answer(savol, lang="ky"))
