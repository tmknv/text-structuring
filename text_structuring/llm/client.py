import os
from dotenv import load_dotenv
from openai import OpenAI
from text_structuring.llm.prompt import build_segment_prompt
from text_structuring.llm.prompt import build_structure_prompt
from text_structuring.llm.prompt import build_style_prompt
from text_structuring.llm.prompt import build_proofread_prompt

# Ищем файл .env и загружаем переменные
load_dotenv()

# Забираем ключ
api_key = os.getenv("OPENROUTER_API_KEY")

# зач LLMClient еще и в text-structuring/text_structuring/llm/checkllm.py
# перенести в 1 место и импортировать 
def LLMClient(text: str) -> str:
    """
    Обращение к LLM

    Принимает на вход строку/текст как сообщение от пользователя
    и возвращает ответ LLM

    """

    client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)
    completion = client.chat.completions.create(
     model="openrouter/free",
     messages=[
     {
        "role": "user",
        "content": text
      }
     ]
    )
    return completion.choices[0].message.content
