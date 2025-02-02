class Context:
    def __init__(self):
        self.context_variables = {}

    def add_context(self, key, value):
        self.context_variables[key] = value