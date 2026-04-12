from forge_primitives import add, subtract, multiply
from forge.amino_acids.protein import Alanine

class ReasoningTool:
    def __init__(self):
        pass

    def perform_addition(self, a, b):
        return add(a, b)

    def perform_subtraction(self, a, b):
        return subtract(a, b)

    def perform_multiplication(self, a, b):
        return multiply(a, b)

    def generate_protein_sequence(self, count):
        sequence = [Alanine()] * count
        return sequence

# Example usage:
tool = ReasoningTool()
result_addition = tool.perform_addition(5, 3)
result_subtraction = tool.perform_subtraction(10, 4)
result_multiplication = tool.perform_multiplication(2, 6)
protein_sequence = tool.generate_protein_sequence(3)

print("Addition Result:", result_addition)
print("Subtraction Result:", result_subtraction)
print("Multiplication Result:", result_multiplication)
print("Protein Sequence:", [type(aa) for aa in protein_sequence])