from forge_primitives import get, add, subtract
from forge.amino_acids.basic import Alanine

class ReasoningTool:
    def __init__(self):
        pass
    
    def infer_from_data(self, data1, data2):
        return add(data1, data2)
    
    def analyze_difference(self, value1, value2):
        return subtract(value1, value2)
    
    def fetch_information(self, key):
        return get(key)