
from text_structuring.llm.prompt import build_segment_prompt, build_structure_prompt, build_style_prompt, build_proofread_prompt
from text_structuring.llm.client import LLMClient
import json

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
        prompt = build_segment_prompt(state.raw_text) 
        response = LLMClient(prompt)               
        state.segments = [s.strip() for s in response.split("\n") if s.strip()]
        return state


class StructureBuilder(BaseAgent):
    def run(self, state):
        prompt = build_structure_prompt(state.segments)
        response = LLMClient(prompt)
    
        state.structure = json.loads(response)

        return state

class Styler(BaseAgent):
    def run(self, state):
        prompt = build_style_prompt(state.structure)
        response = LLMClient(prompt)
        state.styled_text = response
        return state


class Proofreader(BaseAgent):
    def run(self, state):
        prompt = build_proofread_prompt(state.styled_text)
        response = LLMClient(prompt)
        state.final_text = response
        return state