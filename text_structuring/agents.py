
from abc import ABC, abstractmethod
from time import time

from text_structuring.llm.prompt import build_segment_prompt, build_structure_prompt, build_style_prompt, build_proofread_prompt
from text_structuring.llm.client import LLMClient
from text_structuring.schemas.contracts import AgentResponse, create_failed_response, create_success_response
from text_structuring.schemas.text import TextState 
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
class BaseAgent(ABC):
    """
    Базовый класс для всех агентов.

    Контракт:
    - принимает state
    - возвращает state
    """
    @abstractmethod
    def run(self, state):
        """
        Выполнить обработку и вернуть AgentResponse.
        
        Args:
            state: Состояние текста в pipeline
            
        Returns:
            AgentResponse - структурированный ответ с результатом работы
        """
        raise NotImplementedError


class Segmenter(BaseAgent):
    """Агент для сегментации текста на части"""

    def run(self, state) -> AgentResponse:
        try:
            start_time = time.time()
            pm = PromptManager()
            prompt = pm.get("segmenter", text=state.raw_text)
            print(f"[DEBUG Segmenter] prompt: {prompt}")
            response_text = LLMClient(prompt["system"], prompt["user"])
            response_data = json.loads(response_text)
            print(f"[DEBUG Segmenter] LLM response text: {response_text}")
            print(f"[DEBUG Segmenter] LLM response data: {response_data}")
            segments = response_data.get("segments", [])
            confidence = response_data.get("confidence", 0.00)
            reasoning = response_data.get("reasoning", "")
            
            latency = (time.time() - start_time) * 1000
            state.segments = segments
            
            return create_success_response(
                agent_name="Segmenter",
                data={"segments": segments, "count": len(segments)},
                confidence=confidence,
                reasons=[
                    f"Успешно выделено {len(segments)} сегментов текста",
                    f"Рассуждение LLM: {reasoning}" if reasoning else ""
                ],
                quality_metrics={
                    "segment_count": len(segments),
                    "avg_segment_length": sum(len(s) for s in segments) / len(segments) if segments else 0,
                    "llm_confidence": confidence
                },
                latency_ms=latency
            )
        except json.JSONDecodeError as e:
            return create_failed_response(
                agent_name="Segmenter",
                error=f"JSON парсинг ошибка: {str(e)}",
                reason="Невалидный JSON в ответе LLM",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )
        except Exception as e:
            return create_failed_response(
                agent_name="Segmenter",
                error=str(e),
                reason="Ошибка при сегментации текста",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )


class StructureBuilder(BaseAgent):
    """Агент для построения структуры из сегментов"""

    def run(self, state) -> AgentResponse:
        try:
            start_time = time.time()
            pm = PromptManager()
            joined = "\n".join(state.segments)
            prompt = pm.get("structurer", segments=joined)
            
            response_text = LLMClient(prompt["system"], prompt["user"])

            print(f"[DEBUG StructureBuilder] prompt: {prompt}")
            response_data = json.loads(response_text)
            print(f"[DEBUG StructureBuilder] LLM response text: {response_text}")
            print(f"[DEBUG StructureBuilder] LLM response data: {response_data}")
            structure = response_data.get("sections", [])
            confidence = response_data.get("confidence", 0.00)
            reasoning = response_data.get("reasoning", "")
            
            latency = (time.time() - start_time) * 1000
            
            state.structure = {"sections": structure} if isinstance(structure, list) else response_data
            
            # Анализ качества структуры
            depth = _calculate_json_depth(state.structure)
            
            return create_success_response(
                agent_name="StructureBuilder",
                data={"structure": state.structure},
                confidence=confidence,  # Получено от LLM
                reasons=[
                    "Структура успешно построена из сегментов",
                    f"Глубина иерархии: {depth}",
                    f"Рассуждение LLM: {reasoning}" if reasoning else ""
                ],
                quality_metrics={
                    "structure_depth": depth,
                    "segments_involved": len(state.segments),
                    "llm_confidence": confidence
                },
                latency_ms=latency
            )
        except json.JSONDecodeError as e:
            return create_failed_response(
                agent_name="StructureBuilder",
                error=f"JSON парсинг ошибка: {str(e)}",
                reason="Невалидный JSON в ответе",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )
        except Exception as e:
            return create_failed_response(
                agent_name="StructureBuilder",
                error=str(e),
                reason="Ошибка при построении структуры",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )


class Styler(BaseAgent):
    """Агент для стилизации и форматирования структурированного текста"""
    
    def run(self, state) -> AgentResponse:
        try:
            start_time = time.time()
            pm = PromptManager()
            json_structure = json.dumps(state.structure, ensure_ascii=False, indent=2)
            prompt = pm.get("formatter", json_structure=json_structure)
            
            response_text = LLMClient(prompt["system"], prompt["user"])
            print(f"[DEBUG Styler] prompt: {prompt}")
            response_data = json.loads(response_text)
            print(f"[DEBUG Styler] LLM response text: {response_text}")
            print(f"[DEBUG Styler] LLM response data: {response_data}")

            styled_text = response_data.get("formatted_text", "")
            confidence = response_data.get("confidence", 0.00)
            reasoning = response_data.get("reasoning", "")
            
            latency = (time.time() - start_time) * 1000
            
            state.styled_text = styled_text
            
            return create_success_response(
                agent_name="Styler",
                data={"styled_text": styled_text, "length": len(styled_text)},
                confidence=confidence,
                reasons=[
                    "Текст успешно отформатирован и стилизован",
                    f"Итоговый размер: {len(styled_text)} символов",
                    f"Рассуждение LLM: {reasoning}" if reasoning else ""
                ],
                quality_metrics={
                    "output_length": len(styled_text),
                    "formatting_ratio": len(styled_text) / (len(json_structure) + 1),
                    "llm_confidence": confidence
                },
                latency_ms=latency
            )
        except json.JSONDecodeError as e:
            return create_failed_response(
                agent_name="Styler",
                error=f"JSON парсинг ошибка: {str(e)}",
                reason="Ошибка при парсинге JSON от LLM",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )
        except Exception as e:
            return create_failed_response(
                agent_name="Styler",
                error=str(e),
                reason="Ошибка при стилизации текста",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )



class Proofreader(BaseAgent):
    """Агент для проверки качества и финализации текста"""
    
    def run(self, state) -> AgentResponse:
        try:
            start_time = time.time()
            pm = PromptManager()
            prompt = pm.get("proofreader", text=state.styled_text)
            
            response_text = LLMClient(prompt["system"], prompt["user"])
            print(f"[DEBUG Proofreader] prompt: {prompt}")
            response_data = json.loads(response_text)
            print(f"[DEBUG Proofreader] LLM response text: {response_text}")
            print(f"[DEBUG Proofreader] LLM response data: {response_data}")


            final_text = response_data.get("corrected_text", "")
            confidence = response_data.get("confidence", 0.00)
            corrections = response_data.get("corrections_made", [])
            reasoning = response_data.get("reasoning", "")
            
            latency = (time.time() - start_time) * 1000
            
            state.final_text = final_text
            
            return create_success_response(
                agent_name="Proofreader",
                data={"final_text": final_text, "length": len(final_text)},
                confidence=confidence,  # Получено от LLM
                reasons=[
                    "Текст успешно проверен и финализирован",
                    f"Исправлений: {len(corrections) if isinstance(corrections, list) else 0}",
                    f"Рассуждение LLM: {reasoning}" if reasoning else ""
                ],
                quality_metrics={
                    "final_length": len(final_text),
                    "correction_ratio": abs(len(state.styled_text) - len(final_text)) / (len(state.styled_text) + 1) if state.styled_text else 0,
                    "corrections_count": len(corrections) if isinstance(corrections, list) else 0,
                    "llm_confidence": confidence
                },
                latency_ms=latency
            )
        except json.JSONDecodeError as e:
            return create_failed_response(
                agent_name="Proofreader",
                error=f"JSON парсинг ошибка: {str(e)}",
                reason="Ошибка при парсинге JSON от LLM",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )
        except Exception as e:
            return create_failed_response(
                agent_name="Proofreader",
                error=str(e),
                reason="Ошибка при проверке и финализации",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )



class MarkdownConverter(BaseAgent):
    """
    Агент для конвертации финального текста в хорошо структурированный Markdown.
    """
    def run(self, state) -> AgentResponse:
        try:
            start_time = time.time()
            pm = PromptManager()
            prompt = pm.get("markdown_converter", text=state.final_text)
            
            response_text = LLMClient(prompt["system"], prompt["user"])
            print(f"[DEBUG MarkdownConverter] prompt: {prompt}")
            response_data = json.loads(response_text)
            print(f"[DEBUG MarkdownConverter] LLM response text: {response_text}")
            print(f"[DEBUG MarkdownConverter] LLM response data: {response_data}")


            final_text = response_data.get("markdown_text", "")
            
            latency = (time.time() - start_time) * 1000
            
            state.final_text = final_text
            
            return create_success_response(
                agent_name="MarkdownConverter",
                data={"markdown_text": final_text, "length": len(final_text)},
                confidence=1,  # Получено от LLM
                reasons=[
                    "Текст успешно конвертирован в Markdown",
                ],
                quality_metrics={
                    "final_length": len(final_text),
                    "llm_confidence": 1
                },
                latency_ms=latency
            )
        except json.JSONDecodeError as e:
            return create_failed_response(
                agent_name="MarkdownConverter",
                error=f"JSON парсинг ошибка: {str(e)}",
                reason="Ошибка при парсинге JSON от LLM",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )
        except Exception as e:
            return create_failed_response(
                agent_name="MarkdownConverter",
                error=str(e),
                reason="Ошибка при конвертации в Markdown",
                latency_ms=(time.time() - start_time) * 1000 if 'start_time' in locals() else None
            )

    def run(self, state):
        pm = PromptManager()
        
        # Используем final_text после proofreader
        prompt = pm.get("markdown_converter", text=state.final_text)
        
        response = LLMClient(prompt["system"], prompt["user"])
        
        state.markdown_text = response.strip()
        
        return state


def _calculate_json_depth(obj, current_depth=0) -> int:
    """Вычислить глубину JSON структуры"""
    if isinstance(obj, dict):
        if not obj:
            return current_depth
        return max(_calculate_json_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, (list, tuple)):
        if not obj:
            return current_depth
        return max(_calculate_json_depth(item, current_depth + 1) for item in obj)
    else:
        return current_depth