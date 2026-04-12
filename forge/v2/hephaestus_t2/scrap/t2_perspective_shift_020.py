from forge_primitives import add, subtract, multiply
from forge.amino_acids.leucine import code

class ReasoningTool:
    def __init__(self):
        self.add = add
        self.subtract = subtract
        self.multiply = multiply
        self.code = code

    def evaluate_expression(self, expression):
        try:
            return eval(expression, {"__builtins__": None}, {"add": self.add, "subtract": self.subtract, "multiply": self.multiply})
        except Exception as e:
            return str(e)

    def translate_code_to_amino_acid(self, code_sequence):
        amino_acids = []
        for i in range(0, len(code_sequence), 3):
            codon = code_sequence[i:i+3]
            amino_acid = self.code.get(codon)
            if amino_acid:
                amino_acids.append(amino_acid)
            else:
                return "Invalid codon sequence"
        return ".join(amino_acids)"