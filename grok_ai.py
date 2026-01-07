# grok_ai.py – толук иштей турган акыркы версия

import os
from openai import OpenAI

# API key алуу
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY орнотулган эмес! Render'де Environment Variables'ке кош.")

# xAI клиент түзүү
client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

def grok_answer(text, lang="ky", is_pro=False):
    """
    Grok (xAI) жооп берет
    text – суроо
    lang – тил (ky, ru, en ж.б.)
    is_pro – PRO план болсо эң күчтүү моделди колдонот
    """
    # Модел тандоо
    model = "grok-4" if is_pro else "grok-4-fast"

    # System prompt – Grok стилинде чынчыл жана күчтүү кылуу
    system_prompt = (
        "Сен күчтүү, чынчыл жана акылдуу AI жардамчысың – Grok сыяктуу. "
        "Цензурасыз, түз, күлкүлүү жана пайдалуу жооп бер. "
        f"Жоопту толугу менен {lang} тилинде гана бер."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.9,
            max_tokens=1500
        )
        answer = response.choices[0].message.content.strip()
        return answer

    except Exception as e:
        return f"❌ Ката чыкты: {str(e)}\n\nМүмкүн болгон себептер:\n- GROK_API_KEY туура эмес\n- Интернет байланышы жок\n- xAI сервери убактылуу иштебей жатат"

# Локалда тест үчүн (Render'де керек эмес)
if __name__ == "__main__":
    print("Тест:")
    print(grok_answer("Салам, сен кимсиң? Кандайсың?", lang="ky"))
