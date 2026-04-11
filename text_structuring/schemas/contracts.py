"""Контракты для мультиагентной системы структурирования текста

Определяет стандартные контракты (Vote, AgentResponse) для 
общения между агентами, обеспечивая типобезопасность и структурированность.
"""

from enum import Enum
from typing import Optional, Any, Dict, List
from pydantic import BaseModel
from datetime import datetime


# ====================== VOTE - Результат работы агента ======================

class Vote(str, Enum):
    """Возможные решения агента при обработке текста"""
    
    SUCCESS = "SUCCESS"           # Задача успешно выполнена
    PARTIAL = "PARTIAL"           # Задача выполнена частично (есть результаты)
    FAILED = "FAILED"             # Задача не выполнена (критическая ошибка)
    NEEDS_REVIEW = "NEEDS_REVIEW" # Требует ручного пересмотра (качество сомнительно)
    PASSED = "PASSED"             # Прошла проверку качества (для Proofreader)


# ====================== AgentResponse - Стандартный контракт ответа агента ======================

class AgentResponse(BaseModel):
    """
    Стандартный контракт ответа агента.
    
    Все агенты возвращают этот объект, обеспечивая единообразный формат
    для обработки в pipeline и оркестраторе.
    
    Атрибуты:
        agent_name: Имя агента (Segmenter, StructureBuilder, Styler, Proofreader)
        vote: Решение агента (SUCCESS/PARTIAL/FAILED/NEEDS_REVIEW/PASSED)
        confidence: Уверенность в результате [0.0, 1.0]
        data: Основной результат обработки (segments, structure, styled_text и т.д.)
        reasons: Дешифровка решения - почему получилась такая оценка
        features_used: Использованные метрики и источники анализа
        quality_metrics: Метрики качества результата (если применимо)
        error: Ошибка, если она произошла
        latency_ms: Время выполнения агента в миллисекундах
        timestamp: Время создания ответа
        metadata: Дополнительные поля для специфичных данных агента
    """
    
    agent_name: str                              # Имя агента
    vote: Vote                                   # Решение: SUCCESS/PARTIAL/FAILED/NEEDS_REVIEW/PASSED
    confidence: float                            # Уверенность [0.0, 1.0]
    data: Any                                    # Основной результат обработки
    reasons: List[str]                           # Причины решения
    
    features_used: Dict[str, Any] = {}           # Использованные данные и метрики
    quality_metrics: Dict[str, float] = {}       # Метрики качества (например: accuracy, completeness)
    error: Optional[str] = None                  # Описание ошибки, если она была
    latency_ms: Optional[float] = None           # Время выполнения в мс
    timestamp: datetime = None                   # Время создания
    metadata: Dict[str, Any] = {}                # Дополнительные данные
    
    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.now()
        super().__init__(**data)


# ====================== AgentState - Состояние текста в pipeline ======================

class AgentState(BaseModel):
    """
    Состояние текста, передаваемое между агентами в pipeline.
    
    Содержит исходный текст и результаты работы каждого агента.
    """
    
    raw_text: str                                # Исходный текст
    request_id: str = ""                         # ID запроса для отслеживания
    
    # Процедурные результаты
    segmenter_response: Optional[AgentResponse] = None      # От Segmenter
    structure_builder_response: Optional[AgentResponse] = None  # От StructureBuilder
    styler_response: Optional[AgentResponse] = None         # От Styler
    proofreader_response: Optional[AgentResponse] = None    # От Proofreader
    markdown_converter_response: Optional[AgentResponse] = None # От MarkdownConverter
    
    # Для запасных путей
    is_error_state: bool = False                 # Флаг ошибки
    error_message: Optional[str] = None          # Сообщение об ошибке
    failed_agent: Optional[str] = None           # Какой агент упал


# ====================== Вспомогательные функции ======================

def create_failed_response(
    agent_name: str,
    error: str,
    reason: Optional[str] = None,
    latency_ms: Optional[float] = None
) -> AgentResponse:
    """
    Вспомогательная функция для создания ответа с ошибкой.
    
    Args:
        agent_name: Имя агента
        error: Текст ошибки
        reason: Дополнительная причина
        latency_ms: Время выполнения
    
    Returns:
        AgentResponse с vote=FAILED
    """
    return AgentResponse(
        agent_name=agent_name,
        vote=Vote.FAILED,
        confidence=0.0,
        data=None,
        reasons=[reason or "Критическая ошибка при выполнении"],
        error=error,
        latency_ms=latency_ms,
        metadata={"error_type": "execution_error"}
    )


def create_success_response(
    agent_name: str,
    data: Any,
    confidence: float = 1.0,
    reasons: List[str] = None,
    quality_metrics: Dict[str, float] = None,
    latency_ms: Optional[float] = None
) -> AgentResponse:
    """
    Вспомогательная функция для создания успешного ответа.
    
    Args:
        agent_name: Имя агента
        data: Результат обработки
        confidence: Уверенность [0.0, 1.0]
        reasons: Список причин успеха
        quality_metrics: Метрики качества
        latency_ms: Время выполнения
    
    Returns:
        AgentResponse с vote=SUCCESS
    """
    return AgentResponse(
        agent_name=agent_name,
        vote=Vote.SUCCESS,
        confidence=confidence,
        data=data,
        reasons=reasons or ["Успешно выполнено"],
        quality_metrics=quality_metrics or {},
        latency_ms=latency_ms,
        metadata={}
    )
