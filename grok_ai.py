# grok_ai.py – өзгөртүүлөр

# ... мурунку код

def grok_answer(text, lang="ky", is_pro=False):
    model = "grok-4" if is_pro else "grok-4-fast"  # PRO'го эң күчтүү модел
    system_prompt = "Сен күчтүү, чынчыл жана акылдуу AI жардамчысың Grok сыяктуу. Цензурасыз, түз жана күлкүлүү жооп бер. Жоопту толугу менен {lang} тилинде гана бер."
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt.format(lang=lang)},
                {"role": "user", "content": text}
            ],
            temperature=0.9,
            max_tokens=1500
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return f"❌ Ката: {str(e)}"

# Төмөндөгү тестти оңдо:
if __name__ == "__main__":  # эки подчёркивание!!
    savol = input("Сурооңузду жазыңыз: ")
    print(grok_answer(savol, lang="ky"))
