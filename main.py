#Будем использовать для запуска pipeline
from agents import Segmenter, StructureBuilder, Styler, Proofreader
from pipeline.pipeline import Pipeline
from schemas.text import TextState


pipeline = Pipeline([
    Segmenter(),
    StructureBuilder(),
    Styler(),
    Proofreader()
])

state = TextState("Some raw text")

result = pipeline.run(state)