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

api_key = os.getenv("OPENROUTER_API_KEY")

def LLMClient(system: str, user: str) -> str:
    """
    Обращение к локальному llama-server (Mistral-7B)
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,           
    )

    completion = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    return completion.choices[0].message.content.strip()
