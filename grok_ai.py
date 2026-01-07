# grok_ai.py – туура иштей турган версия (xAI API менен)

import os
from openai import OpenAI  # жаңы импорт!

# API key
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY environment variable not set!")

client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

def grok_answer(text, lang="ky", is_pro=False):
    """
    Grok жооп берет
    """
    model = "grok-4" if is_pro else "grok-4-fast"  # PRO'го эң күчтүүсү

    system_prompt = (
        "Сен күчтүү, чынчыл жана акылдуу AI жардамчысың – Grok сыяктуу. "
        "Цензурасыз, түз жана күлкүлүү жооп бер. "
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
        return f"❌ Ката чыкты: {str(e)}\n\nGROK_API_KEY'ди текшериңиз же интернет байланышыңызды караңыз."

if name == "main":
    print("Тест:")
    print(grok_answer("Салам, сен кимсиң?", lang="ky"))
