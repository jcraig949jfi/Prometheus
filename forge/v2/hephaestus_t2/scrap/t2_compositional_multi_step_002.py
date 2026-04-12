from forge_primitives import confidence_from_agreement, dag_traverse, solve_constraints
from forge.amino_acids.pgmpy_acids import alanine

class ReasoningTool:
    def __init__(self):
        pass

    def analyze_confidence(self, beliefs):
        return confidence_from_agreement(beliefs)

    def traverse_dag(self, graph):
        return dag_traverse(graph)

    def constraint_solver(self, constraints):
        return solve_constraints(constraints)