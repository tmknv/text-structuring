# src/pipeline/dag_pipeline.py
import asyncio

class Pipeline:
    def __init__(self, segmenter, structure, styler, proofreader):
        self.segmenter = segmenter
        self.structure = structure
        self.styler = styler
        self.proofreader = proofreader

    async def run(self, text):
        # Шаг 1: сегментация
        x1 = await self.segmenter.run(text)
        # Шаг 2: построение структуры
        x2 = await self.structure.run(x1)
        # Шаг 3: стиль
        x3 = await self.styler.run(x2)
        # Шаг 4: исправление / proofread
        final = await self.proofreader.run(x3)

        return final