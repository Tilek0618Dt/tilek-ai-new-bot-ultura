import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def ai_answer(text, mode="default"):
    if not OPENROUTER_API_KEY:
        return "❌ AI API KEY табылган жок"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/TilekAIBot",
        "X-Title": "Tilek AI Bot"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Сен Tilek AI аттуу акылдуу ассистентсиң. "
                    "Колдонуучуга түшүнүктүү, жылуу, пайдалуу жооп бер. "
                    "Кыска, так, логикалуу сүйлө."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )

        result = r.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ AI ката: {e}"
