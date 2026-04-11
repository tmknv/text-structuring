
from text_structuring.llm.prompt import build_segment_prompt, build_structure_prompt, build_style_prompt, build_proofread_prompt
from text_structuring.llm.client import LLMClient
import json
import yaml
import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
# ====================== Prompt Manager ======================

class PromptManager:
    """Класс для удобной работы с промптами из YAML"""
    _instance = None
    _prompts = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_prompts()
        return cls._instance

    def _load_prompts(self):
        # Берём путь из .env
        prompts_path = os.getenv("PROMPTS_PATH")

        project_root = Path(__file__).parent.parent.parent
        filepath = (project_root / prompts_path).resolve()

        with open(filepath, encoding="utf-8") as f:
            self._prompts = yaml.safe_load(f)

        print(f"Промпты успешно загружены из: {filepath}")

    def get(self, prompt_name: str, **kwargs) -> Dict[str, str]:
        """Возвращает system и user промпты"""
        if self._prompts is None:
            self._load_prompts()
            
        if prompt_name not in self._prompts:
            raise ValueError(f"Промпт '{prompt_name}' не найден в prompts.yaml")

        config = self._prompts[prompt_name]
        
        system = config["system"]
        user = config["user"].format(**kwargs)
        
        return {"system": system, "user": user}

# ----- Agents -----
class BaseAgent:
    """
    Базовый класс для всех агентов.

    Контракт:
    - принимает state
    - возвращает state
    """

    def run(self, state):
        raise NotImplementedError


class Segmenter(BaseAgent):
    def run(self, state):
        pm = PromptManager()
        prompt = pm.get("segmenter", text=state.raw_text)
        
        response = LLMClient(prompt["system"], prompt["user"])  
        
        state.segments = [s.strip() for s in response.split("\n") if s.strip()]
        return state


class StructureBuilder(BaseAgent):
    def run(self, state):
        pm = PromptManager()
        joined = "\n".join(state.segments)
        prompt = pm.get("structurer", segments=joined)
        
        response = LLMClient(prompt["system"], prompt["user"])  
        
        state.structure = json.loads(response)
        return state


class Styler(BaseAgent):
    def run(self, state):
        pm = PromptManager()
        json_structure = json.dumps(state.structure, ensure_ascii=False, indent=2)
        prompt = pm.get("styler", json_structure=json_structure)
        
        response = LLMClient(prompt["system"], prompt["user"])  
        
        state.styled_text = response
        return state


class Proofreader(BaseAgent):
    def run(self, state):
        pm = PromptManager()
        prompt = pm.get("proofreader", text=state.styled_text)
        
        response = LLMClient(prompt["system"], prompt["user"])   
        
        state.final_text = response
        return state


class MarkdownConverter(BaseAgent):
    """
    Агент для конвертации финального текста в хорошо структурированный Markdown.
    """

    def run(self, state):
        pm = PromptManager()
        
        # Используем final_text после proofreader
        prompt = pm.get("markdown_converter", text=state.final_text)
        
        response = LLMClient(prompt["system"], prompt["user"])
        
        state.markdown_text = response.strip()
        
        return state


class BaselineAgent(BaseAgent):
    """
    Baseline версия: всё в одном промпте.
    Заменяет всю цепочку segmenter → structure_builder → styler → proofreader.
    """

    def run(self, state):
        pm = PromptManager()
        
        # Получаем промпт baseline
        prompt = pm.get("baseline", text=state.raw_text)
        
        # Один единственный вызов LLM
        response = LLMClient(prompt["system"], prompt["user"])
        
        # Сохраняем результат
        state.final_text = response
        state.is_baseline = True  # метка, что использовался baseline
        
        print("✓ BaselineAgent выполнен (один промпт)")
        
        return state


class EvaluatorAgent(BaseAgent):
    """
    Агент для сравнения качества Multi-Agent и Baseline подходов
    относительно оригинального текста.
    """

    def run(self, state):
        pm = PromptManager()
        
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
            print("✓ Оценка качества выполнена")
        except json.JSONDecodeError:
            state.evaluation = {"error": "Failed to parse evaluation", "raw": response}
            print("✗ Не удалось распарсить оценку")
        
        return state