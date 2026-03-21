# пример агента
class Segmenter:
    async def run(self, text):
        # например, запрос к LLM через async API
        await asyncio.sleep(0.1)  # имитация асинхронной работы
        return text.split("\n\n")  # простой сегмент