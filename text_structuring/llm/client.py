import os
from dotenv import load_dotenv
from openai import OpenAI

# Ищем файл .env и загружаем переменные
load_dotenv()

# Забираем ключ
api_key = os.getenv("OPENROUTER_API_KEY")

# зач LLMClient еще и в text-structuring/text_structuring/llm/checkllm.py
# перенести в 1 место и импортировать 
def LLMClient(system: str, user: str) -> str:
    """
    Обращение к LLM с раздельными system и user промптами.
    
    Теперь принимает два аргумента:
        system — системный промпт (инструкции)
        user   — пользовательский промпт (данные)
    """
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=30.0,  # 30 сек таймаут
        )

        completion = client.chat.completions.create(
            model="openrouter/free",   
                                      
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
        )

        result = completion.choices[0].message.content.strip()
        return result
    except Exception as e:
        print(f"ERROR: LLMClient failed - {type(e).__name__}: {str(e)}")
        raise
