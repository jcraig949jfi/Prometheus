from forge_primitives import add, subtract, multiply
from forge.amino_acids.nucleic_acids import DNA

class ReasoningTool:
    def __init__(self):
        pass

    def add_numbers(self, a, b):
        return add(a, b)

    def subtract_numbers(self, a, b):
        return subtract(a, b)

    def multiply_numbers(self, a, b):
        return multiply(a, b)

    def process_dna_sequence(self, sequence):
        return DNA(sequence).process()