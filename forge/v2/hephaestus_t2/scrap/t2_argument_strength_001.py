from forge_primitives import add, subtract, multiply
from forge.amino_acids.basic_amino_acids import Alanine

class ReasoningTool:
    def __init__(self):
        self.value = 0

    def add_value(self, amount):
        self.value = add(self.value, amount)
        return self

    def subtract_value(self, amount):
        self.value = subtract(self.value, amount)
        return self

    def multiply_value(self, factor):
        self.value = multiply(self.value, factor)
        return self

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
        return self

    def reset_value(self):
        self.value = 0
        return self

    def add_amino_acid(self, acid_count):
        self.value += Alanine() * acid_count
        return self

    def subtract_amino_acid(self, acid_count):
        self.value -= Alanine() * acid_count
        return self