import os
from dotenv import load_dotenv
from openai import OpenAI
from prompt import build_segment_prompt
from prompt import build_structure_prompt
from prompt import build_style_prompt
from prompt import build_proofread_prompt

# Ищем файл .env и загружаем переменные
load_dotenv()

# Забираем ключ
api_key = os.getenv("OPENROUTER_API_KEY")

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

print(LLMClient(build_proofread_prompt(LLMClient(build_style_prompt(LLMClient(build_structure_prompt(LLMClient(build_segment_prompt(f'''Криптография с открытым ключом строится на асимметричных алгоритмах, где используются два разных ключа: публичный и приватный. Это база для цифровых подписей. В то же время блокчейн — это распределенный реестр, где данные хранятся в цепочке блоков, и каждый блок содержит хеш предыдущего. Кстати, хеш-функция (например, SHA-256) — это математический алгоритм, который превращает любой объем данных в строку фиксированной длины, причем это необратимый процесс. Безопасность сети обеспечивается механизмами консенсуса. Самый известный — Proof of Work (PoW), где майнеры решают сложные задачи. Но есть и Proof of Stake (PoS), который гораздо энергоэффективнее. Важно понимать, что если изменить хотя бы один бит в блоке, его хеш полностью изменится, и цепочка разрушится. Блокчейн бывает публичным (как Bitcoin) и приватным (корпоративным). Смарт-контракты — это еще один уровень, это программный код, который исполняется автоматически при наступлении условий, их популяризировал Ethereum. Основные свойства технологии: децентрализация, прозрачность и неизменяемость данных. Асимметричное шифрование позволяет Алисе отправить зашифрованное сообщение Бобу, используя его публичный ключ, а расшифровать его сможет только Боб своим секретным ключом. В узлах сети (нодах) хранится полная копия базы данных, что исключает единую точку отказа.''')))))))))
