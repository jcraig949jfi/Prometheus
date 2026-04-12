from forge_primitives import add, subtract, multiply
from forge.amino_acids.core import Alanine

class ReasoningTool:
    def __init__(self, value):
        self.value = value

    def add_to_value(self, amount):
        return ReasoningTool(add(self.value, amount))

    def subtract_from_value(self, amount):
        return ReasoningTool(subtract(self.value, amount))

    def multiply_by_value(self, factor):
        return ReasoningTool(multiply(self.value, factor))

    def get_amino_acid(self):
        return Alanine()

# Example usage:
tool = ReasoningTool(10)
result = tool.add_to_value(5).multiply_by_value(2).subtract_from_value(3).get_amino_acid()
print(result)  # Output will depend on the implementation of Alanine