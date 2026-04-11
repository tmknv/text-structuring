"""LangGraph Pipeline для структурирования текста"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
from text_structuring.agents import Segmenter, StructureBuilder, Styler, Proofreader, MarkdownConverter
from text_structuring.schemas.contracts import AgentResponse
from text_structuring.schemas.text import TextState


class PipelineState(TypedDict, total=False):
    """Состояние pipeline"""
    text_state: TextState
    # Сохраняем responses агентов
    segmenter_response: Optional[AgentResponse]
    structure_builder_response: Optional[AgentResponse]
    styler_response: Optional[AgentResponse]
    proofreader_response: Optional[AgentResponse]
    markdown_converter_response: Optional[AgentResponse]



# ====================== УЗЛЫ ======================

def segmenter_node(state: PipelineState) -> PipelineState:
    """Сегментация текста"""
    agent = Segmenter()
    response = agent.run(state["text_state"])
    state["segmenter_response"] = response
    return state


def structure_builder_node(state: PipelineState) -> PipelineState:
    """Построение структуры"""
    agent = StructureBuilder()
    response = agent.run(state["text_state"])
    state["structure_builder_response"] = response
    return state


def styler_node(state: PipelineState) -> PipelineState:
    """Форматирование текста"""
    agent = Styler()
    response = agent.run(state["text_state"])
    state["styler_response"] = response
    return state


def proofreader_node(state: PipelineState) -> PipelineState:
    """Проверка и корректировка"""
    agent = Proofreader()
    response = agent.run(state["text_state"])
    state["proofreader_response"] = response
    return state

def markdown_converter_node(state: PipelineState) -> PipelineState:
    """Конвертация в Markdown"""
    agent = MarkdownConverter()
    response = agent.run(state["text_state"])
    state["markdown_converter_response"] = response
    return state

# ====================== ГРАФ ======================

def build_graph():
    """Построить граф Segmenter -> StructureBuilder -> Styler -> Proofreader"""
    graph = StateGraph(PipelineState)
    
    graph.add_node("segmenter", segmenter_node)
    graph.add_node("structure_builder", structure_builder_node)
    graph.add_node("styler", styler_node)
    graph.add_node("proofreader", proofreader_node)
    graph.add_node("markdown_converter", markdown_converter_node)
    
    graph.add_edge(START, "segmenter")
    graph.add_edge("segmenter", "structure_builder")
    graph.add_edge("structure_builder", "styler")
    graph.add_edge("styler", "proofreader")
    graph.add_edge("proofreader", "markdown_converter")
    graph.add_edge("markdown_converter", END)
    
    return graph.compile()


# ====================== РЕЗУЛЬТАТ ======================

class PipelineResult:
    """Результат работы pipeline"""
    
    def __init__(self, state: PipelineState):
        self.text_state = state["text_state"]
        self.final_text = state["text_state"].final_text
        
        # Собираем responses агентов
        self.responses = [
            state.get("segmenter_response"),
            state.get("structure_builder_response"),
            state.get("styler_response"),
            state.get("proofreader_response"),
        ]
    
    @property
    def all_reasoning(self) -> str:
        """Собрать reasoning от всех агентов"""
        reasoning_list = []
        
        for response in self.responses:
            if response:
                agent_name = response.agent_name
                confidence = f"{response.confidence:.0%}"
                reasons = " | ".join(response.reasons)
                
                reasoning_list.append(
                    f"{agent_name} ({confidence}): {reasons}"
                )
        
        return "\n".join(reasoning_list)


# ====================== ЗАПУСК ======================

def run_pipeline(raw_text: str) -> PipelineResult:
    """
    Запустить pipeline на LangGraph
    
    Аргументы:
        raw_text: Текст для обработки
    
    Возвращает:
        PipelineResult: Результат с финальным текстом и reasoning от всех агентов
    """
    text_state = TextState(raw_text=raw_text)
    graph = build_graph()
    
    initial_state: PipelineState = {
        "text_state": text_state
    }
    
    final_state = graph.invoke(initial_state)
    return PipelineResult(final_state)


# ====================== ПРОСТОЙ ИНТЕРФЕЙС ======================

def process_text(text: str) -> PipelineResult:
    """
    "Сделай красиво" — простой интерфейс для обработки текста
    
    Аргументы:
        text: Текст для обработки
    
    Возвращает:
        PipelineResult: Результат с финальным текстом и reasoning
    """
    return run_pipeline(text)
