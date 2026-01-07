# grok_ai.py – акыркы, ишенимдүү версия (proxies катасы жок!)

import os
import httpx
from openai import OpenAI

# API key
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY жок! Render'де Environment Variables'ке кош.")

# httpx клиентти өзүбүз түзөбүз – proxies параметрин алып салат
http_client = httpx.Client(timeout=60.0)

client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1",
    http_client=http_client  # бул сап proxies катасын толук жок кылат!
)

def grok_answer(text, lang="ky", is_pro=False):
    model = "grok-4" if is_pro else "grok-4-fast"

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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Ката: {str(e)}\n\nСебептер:\n- API key туура эмес\n- Интернет жок\n- xAI сервери убактылуу иштебейт"

if __name__ == "__main__":
    print("Тест:")
    print(grok_answer("Салам, сен кимсиң?", lang="ky"))
