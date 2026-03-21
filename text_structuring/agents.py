# agents.py

# ========= BASE =========

class BaseAgent:
    def run(self, state):
        raise NotImplementedError


# ========= SEGMENTER =========

class Segmenter(BaseAgent):
    def run(self, state):
        # пока просто заглушка
        return state


# ========= STRUCTURE BUILDER =========

class StructureBuilder(BaseAgent):
    def run(self, state):
        return state


# ========= STYLER =========

class Styler(BaseAgent):
    def run(self, state):
        return state


# ========= PROOFREADER =========

class Proofreader(BaseAgent):
    def run(self, state):
        return state