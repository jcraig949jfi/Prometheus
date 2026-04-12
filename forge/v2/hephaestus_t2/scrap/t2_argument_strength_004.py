from forge_primitives import dag_traverse, topological_sort, bayesian_update
from forge.amino_acids.pgmpy_acids import build_bn, detect_confounders

class ReasoningTool:
    def __init__(self, belief_network):
        self.dag = build_bn(belief_network)
    
    def traverse_dag(self):
        return dag_traverse(self.dag)
    
    def topological_sort_dag(self):
        return topological_sort(self.dag)
    
    def update_beliefs(self, evidence):
        return bayesian_update(self.dag, evidence)
    
    def detect_confounding_variables(self):
        return detect_confounders(self.dag)