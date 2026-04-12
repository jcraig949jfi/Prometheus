from forge_primitives import get_value, append_to_list, increment_number
from forge.amino_acids.proteins import Histidine

class ReasoningTool:
    def __init__(self):
        self.data = []

    def add_data(self, value):
        self.data = append_to_list(self.data, value)

    def get_data(self):
        return get_value(self.data)

    def increment_and_add(self, value):
        new_value = increment_number(value)
        self.add_data(new_value)
        return new_value

    @property
    def protein_code(self):
        return Histidine.code