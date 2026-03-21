# pipeline/pipeline.py

class Pipeline:
    def __init__(self, agents):
        self.agents = agents

    def run(self, state):
        for agent in self.agents:
            state = agent.run(state)
        return state