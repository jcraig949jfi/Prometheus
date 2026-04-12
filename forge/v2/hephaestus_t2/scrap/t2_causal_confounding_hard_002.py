from forge_primitives import load_fact, get_user_input, verify

class ReasoningTool:
    def __init__(self):
        self.facts = []

    def add_fact(self, fact):
        if not verify(fact):
            raise ValueError("Invalid fact")
        self.facts.append(fact)

    def query(self, question):
        user_input = get_user_input(question)
        for fact in self.facts:
            if user_input in fact:
                return load_fact(fact)
        return "No answer found"

# Example usage
tool = ReasoningTool()
tool.add_fact("The sky is blue.")
tool.add_fact("Water boils at 100 degrees Celsius.")
print(tool.query("What color is the sky?"))
print(tool.query("What temperature does water boil at?"))