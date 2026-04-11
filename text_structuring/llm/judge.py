# text_structuring/agents/evaluator.py

from text_structuring.llm.client import LLMClient
from text_structuring.agents import PromptManager
from text_structuring.schemas.text import TextState
import json


class Evaluator:
    """
    Оценивает качество двух подходов 
    (Multi-Agent и Baseline) относительно оригинального текста.
    """

    def __init__(self):
        self.prompt_manager = PromptManager()

    def run(self, state: TextState) -> TextState:
        """
        Сравнивает Multi-Agent и Baseline версии.
        Ожидает, что в state есть:
        - raw_text
        - final_text_multi (результат мультиагента)
        - final_text (результат baseline)
        """
        
        pm = self.prompt_manager
        
        prompt = pm.get(
            "evaluator",
            original_text=state.raw_text,
            multi_agent_text=getattr(state, 'final_text_multi', ''),
            baseline_text=getattr(state, 'final_text', '')
        )

        response = LLMClient(prompt["system"], prompt["user"])

        try:
            evaluation = json.loads(response)
            state.evaluation = evaluation
            
        except json.JSONDecodeError:
            state.evaluation = {
                "error": "Failed to parse evaluation JSON",
                "raw_response": response[:500]
            }

        return state


    def run_comparison(self, original_text: str, multi_agent_text: str, baseline_text: str) -> dict:
        """
        Удобный метод для прямого сравнения без использования TextState.
        Возвращает словарь с оценкой.
        """
        prompt = self.prompt_manager.get(
            "evaluator",
            original_text=original_text,
            multi_agent_text=multi_agent_text,
            baseline_text=baseline_text
        )

        response = LLMClient(prompt["system"], prompt["user"])

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "error": "JSON parse failed",
                "raw": response
            }