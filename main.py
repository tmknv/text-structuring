from text_structuring.agents import Segmenter, StructureBuilder, Styler, Proofreader
from text_structuring.schemas.text import TextState 
from text_structuring.llm.reader import reader


pipeline = [Segmenter(), StructureBuilder(), Styler(), Proofreader()]

# Загружаем текст из документа
raw_text = reader('./text_structuring/llm/testdox.docx')

# Создаём объект состояния
state = TextState(raw_text=raw_text)

for agent in pipeline:
    state = agent.run(state)

print("Segments:", state.segments)
print("Structure:", state.structure)
print("Styled:", state.styled_text)
print("Final:", state.final_text)