from text_structuring.llm.client import LLMClient
from text_structuring.agents import PromptManager
from text_structuring.schemas.text import TextState
import json


class Baseline:
    """
    Самостоятельный Baseline-класс.

    Выполняет всю обработку конспекта одним промптом.
    """

    def __init__(self):
        self.prompt_manager = PromptManager()

    def run(self, raw_text: str) -> TextState:
        """
        Основной метод: принимает сырой текст и возвращает обработанный TextState
        """
        state = TextState(raw_text=raw_text)

        # Получаем промпт baseline
        prompt = self.prompt_manager.get("baseline", text=raw_text)

        # Один запрос к LLM
        response = LLMClient(prompt["system"], prompt["user"])

        # Сохраняем результат
        state.final_text = response.strip()

        return state


    def run_and_save(self, raw_text: str, output_path: str = "baseline_output.md"):
        """
        Удобный метод: запускает baseline и сразу сохраняет результат в файл
        """
        state = self.run(raw_text)

        if state.final_text:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(state.final_text)
            print(f"✓ Результат сохранён в файл: {output_path}")

        return state