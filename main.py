from text_structuring.agents import Segmenter, StructureBuilder, Styler, Proofreader,  BaselineAgent, EvaluatorAgent, MarkdownConverter
from text_structuring.schemas.text import TextState 
from text_structuring.llm.reader import reader
import json


raw_text = reader('./text_structuring/llm/testdox.docx')
state = TextState(raw_text=raw_text)

multi_state = TextState(raw_text=raw_text)
for agent in [Segmenter(), StructureBuilder(), Styler(), Proofreader(), MarkdownConverter()]:
    multi_state = agent.run(multi_state)

baseline_state = TextState(raw_text=raw_text)
baseline_state = BaselineAgent().run(baseline_state)

state.final_text_multi = multi_state.final_text
state.final_text = baseline_state.final_text   # baseline

evaluator = EvaluatorAgent()
state = evaluator.run(state)

print("\n=== РЕЗУЛЬТАТ СРАВНЕНИЯ ===")
print(json.dumps(state.evaluation, ensure_ascii=False, indent=2))