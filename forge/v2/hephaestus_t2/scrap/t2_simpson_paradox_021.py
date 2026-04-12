from forge_primitives import add, subtract, multiply
from forge.amino_acids.basic import Alanine

class ReasoningTool:
    def __init__(self):
        pass

    def add_numbers(self, a, b):
        return add(a, b)

    def subtract_numbers(self, a, b):
        return subtract(a, b)

    def multiply_numbers(self, a, b):
        return multiply(a, b)

    def get_amino_acid_mass(self, amino_acid):
        if amino_acid == "Alanine":
            return Alanine.mass
        else:
            return None