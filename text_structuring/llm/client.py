import os
from dotenv import load_dotenv
from openai import OpenAI
import time
from text_structuring.llm.prompt import build_segment_prompt
from text_structuring.llm.prompt import build_structure_prompt
from text_structuring.llm.prompt import build_style_prompt
from text_structuring.llm.prompt import build_proofread_prompt

# Ищем файл .env и загружаем переменные
load_dotenv()

# зач LLMClient еще и в text-structuring/text_structuring/llm/checkllm.py
# перенести в 1 место и импортировать 
def LLMClient(system: str, user: str, max_retries: int = 6) -> str:
    """
    Обращение к LLM с раздельными system и user промптами.
    
    Теперь принимает два аргумента:
        system — системный промпт (инструкции)
        user   — пользовательский промпт (данные)
    """
    client = OpenAI(
        base_url="http://213.165.211.11/v1",
        api_key="ollama",
    )

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="phi4-mini:3.8b",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user}
                ],
                temperature=0.7,
                max_tokens=1200,
                timeout=180,                    # 3 минуты таймаут
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            error_str = str(e)
            print(f"[Попытка {attempt+1}/{max_retries}] {type(e).__name__}: {error_str[:200]}")

            if "503" in error_str:
                wait = 12 if attempt == 0 else 6
                print(f"   Модель ещё загружается. Ждём {wait} секунд...")
                time.sleep(wait)
            else:
                time.sleep(4)

    raise Exception("Не удалось получить ответ от Ollama после нескольких попыток")
