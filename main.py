from text_structuring.agents import Segmenter, StructureBuilder, Styler, Proofreader
from text_structuring.contracts import Vote
from text_structuring.schemas.text import TextState 
from text_structuring.llm.reader import reader


pipeline = [Segmenter(), StructureBuilder(), Styler(), Proofreader()]

# Загружаем текст из документа
raw_text = reader('./text_structuring/llm/testdox.docx')

# Создаём объект состояния
state = TextState(raw_text=raw_text)

print("ТЕСТИРОВАНИЕ НОВЫХ КОНТРАКТОВ АГЕНТОВ")
print()

# Запускаем pipeline с обработкой новых AgentResponse
for agent in pipeline:
    response = agent.run(state)
    
    # Теперь агент возвращает AgentResponse вместо state
    print(f"Agent: {response.agent_name}")
    print(f"  Vote: {response.vote.value} ({response.vote.name})")
    print(f"  Confidence: {response.confidence:.2%}")
    print(f"  Latency: {response.latency_ms:.2f}ms")
    print(f"  Reasons: {', '.join(response.reasons)}")
    if response.quality_metrics:
        print(f"  Metrics: {response.quality_metrics}")
    if response.error:
        print(f"  Error: {response.error}")
    print()
    
    # Проверяем, не произошла ли критическая ошибка
    if response.vote == Vote.FAILED:
        print(f"Произошла ошибка в агенте {response.agent_name}")
        print(f"   Описание: {response.error}")
        break

print("=" * 70)
print("ФИНАЛЬНОЕ СОСТОЯНИЕ ТЕКСТА")
print(f"Segments: {len(state.segments)} items")
print(f"Structure: {'Готова' if state.structure else 'Не готова'}")
print(f"Styled: {'Готов' if state.styled_text else 'Не готов'} ({len(state.styled_text) if state.styled_text else 0} символов)")
print(f"Final: {'Готов' if state.final_text else 'Не готов'} ({len(state.final_text) if state.final_text else 0} символов)")