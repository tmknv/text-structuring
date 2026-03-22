from typing import List


class Pipeline:
    """
    Pipeline управляет выполнением агентов.

    Использование:
    - создаётся в main.py
    - получает список агентов
    - прогоняет state через них
    """

    def __init__(self, agents: List):
        # список агентов (Segmenter, StructureBuilder, и т.д.)
        self.agents = agents

    def run(self, state):
        """
        Основной метод выполнения pipeline.

        Использование:
        - вызывается в main.py
        - принимает TextState
        - возвращает изменённый TextState
        """

        for agent in self.agents:
            # --- ЛОГИКА ВЫПОЛНЕНИЯ ---

            # (в будущем тут можно добавить логирование)
            print(f"[Pipeline] Running: {agent.__class__.__name__}")

            # каждый агент получает state и возвращает его же
            state = agent.run(state)

        return state