from forge_primitives import dag_traverse, topological_sort, entropy
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query

class ReasoningTool:
    def __init__(self):
        self.bn = None

    def load_model(self, data):
        self.bn = build_bn(data)

    def query(self, variable, evidence=None):
        return conditional_query(self.bn, variable, evidence)