from text_structuring.agents import Segmenter, StructureBuilder, Styler
from text_structuring.pipeline.dag_pipeline import Pipeline
from text_structuring.schemas.text import TextState


pipeline = Pipeline([
    Segmenter(),
    StructureBuilder(),
    Styler()
])

state = TextState("Это первое предложение. Это второе.")

result = pipeline.run(state)

print(result.styled_text)