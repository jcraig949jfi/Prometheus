from forge_primitives import dag_traverse, topological_sort, solve_constraints
from forge.amino_acids.pgmpy_acids import build_bn

class ReasoningTool:
    def __init__(self):
        self.dag = None

    def load_model(self, model_data):
        self.dag = build_bn(model_data)

    def traverse_dag(self):
        return dag_traverse(self.dag)

    def sort_nodes(self):
        return topological_sort(self.dag)
    
    def solve_constraints_in_model(self, constraints):
        return solve_constraints(self.dag, constraints)