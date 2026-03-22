from text_structuring.agents import Segmenter, StructureBuilder, Styler, Proofreader
from text_structuring.schemas.text import TextState 


pipeline = [Segmenter(), StructureBuilder(), Styler(), Proofreader()]

state = TextState("Это первое предложение. Это второе.")

for agent in pipeline:
    state = agent.run(state)

print("Segments:", state.segments)
print("Structure:", state.structure)
print("Styled:", state.styled_text)
print("Final:", state.final_text)