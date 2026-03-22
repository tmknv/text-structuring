class BaseAgent:
    """
    Базовый класс для всех агентов.

    Контракт:
    - принимает state
    - возвращает state
    """

    def run(self, state):
        raise NotImplementedError


def fake_llm_call(prompt: str) -> str:
    """
    Заглушка вместо LLM.

    В будущем:
    - будет заменена на LLMClient (llm/client.py)

    Сейчас:
    - просто имитирует ответ модели
    """
    segments = prompt.split(".")
    segments = [s.strip() for s in segments if s.strip()]

    return "\n".join(segments)


class Segmenter(BaseAgent):
    """
    Агент для разбиения текста на сегменты.

    Использует:
    - raw_text из state

    Заполняет:
    - state.segments
    """

    def run(self, state):
        prompt = state.raw_text
        response = fake_llm_call(prompt)
        segments = response.split("\n")
        state.segments = segments

        return state


class StructureBuilder(BaseAgent):
    """
    Агент для построения структуры текста.

    Использует:
    - state.segments

    Заполняет:
    - state.structure
    """

    def run(self, state):
        prompt = "\n".join(state.segments)
        response = fake_llm_call(prompt)
        structure = {
            "sections": [
                {
                    "title": "Section 1",
                    "content": state.segments
                }
            ]
        }
        state.structure = structure

        return state


class Styler(BaseAgent):
    """
    Агент для стилизации текста.

    Использует:
    - state.structure

    Заполняет:
    - state.styled_text
    """

    def run(self, state):
        # --- 1. Формируем "prompt" ---
        # (пока просто собираем структуру в текст)

        sections = state.structure.get("sections", [])

        text_parts = []

        for section in sections:
            title = section.get("title", "")
            content = section.get("content", [])

            if title:
                text_parts.append(title)

            text_parts.extend(content)

        prompt = "\n".join(text_parts)

        # --- 2. LLM вызов (заглушка) ---
        response = fake_llm_call(prompt)

        # --- 3. Результат ---
        # пока просто используем response как есть
        state.styled_text = response

        return state


# ========= PROOFREADER =========

class Proofreader(BaseAgent):
    """
    Пока заглушка.

    В будущем:
    - будет исправлять ошибки
    """

    def run(self, state):
        return state