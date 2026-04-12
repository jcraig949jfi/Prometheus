from forge_primitives import identity, add_one, subtract_one
from forge.amino_acids.basic import alanine

class ReasoningTool:
    def __init__(self):
        self.primitive_set = [identity, add_one, subtract_one]
        self.amino_acid = alanine

    def process_input(self, input_data):
        result = identity(input_data)
        for primitive in self.primitive_set:
            result = primitive(result)
        return result + self.amino_acid