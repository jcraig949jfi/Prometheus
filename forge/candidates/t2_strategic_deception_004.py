from forge_primitives import counterfactual_intervention, dag_traverse, solve_constraints
from forge.amino_acids.pgmpy_acids import build_bn

class ReasoningTool:
    def __init__(self):
        pass

    def intervene(self, model, intervention):
        return counterfactual_intervention(model, intervention)

    def traverse_dag(self, graph):
        return dag_traverse(graph)

    def solve_model_constraints(self, constraints):
        return solve_constraints(constraints)

    def build_bayesian_network(self, data):
        return build_bn(data)