import os
from dotenv import load_dotenv
from openai import OpenAI
import time


load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

def LLMClient(system: str, user: str) -> str:
    """
    Обращение к OpenRouter
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,           
    )
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        if completion.choices and completion.choices[0].message.content:
            return completion.choices[0].message.content.strip()
        else:
            raise Exception("Модель вернула пустой ответ")

    except Exception as e:
        print(f"Ошибка при обращении к OpenRouter: {type(e).__name__}: {e}")
        # Возвращаем понятное сообщение, чтобы программа не падала
        return f"[Ошибка OpenRouter: {str(e)[:200]}]"


def LLMClient_Baseline(text: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {"role": "system", "content": prompts["baseline"]["system"]},
            {"role": "user",   "content": prompts["baseline"]["user"].format(text=text)}
        ],
        temperature=0.7,
        max_tokens=3000,
    )

    return completion.choices[0].message.content.strip()
