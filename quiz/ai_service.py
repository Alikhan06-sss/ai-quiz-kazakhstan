import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def generate_questions_from_text(text, num_questions=5):
    # Безопасно достаем ключ из переменных окружения сервера
    API_KEY = os.environ.get("GEMINI_API_KEY")

    if not API_KEY:
        print("Ошибка: API ключ не найден в переменных окружения!")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

    prompt = f"""
    Прочитай следующий текст:
    {text}

    Создай {num_questions} тестовых вопросов по этому тексту.
    Твой ответ должен быть СТРОГО в формате JSON-массива.
    Структура:
    [
      {{
        "question": "Текст вопроса?",
        "choices": [
          {{"text": "Правильный ответ", "is_correct": true}},
          {{"text": "Неправильный ответ 1", "is_correct": false}},
          {{"text": "Неправильный ответ 2", "is_correct": false}},
          {{"text": "Неправильный ответ 3", "is_correct": false}}
        ]
      }}
    ]
    """

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)

        if response.status_code != 200:
            print(f"ПОДРОБНАЯ ОШИБКА ОТ GOOGLE: {response.text}")

        response.raise_for_status()

        result = response.json()
        ai_response_text = result['candidates'][0]['content']['parts'][0]['text']

        questions_data = json.loads(ai_response_text)
        return questions_data

    except Exception as e:
        print(f"Ошибка при работе с Gemini API: {e}")
        return None