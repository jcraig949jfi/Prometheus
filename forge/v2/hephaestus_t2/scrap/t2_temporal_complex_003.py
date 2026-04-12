from forge_primitives import sally_anne_test, solve_sat, detect_confounders
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query

class ReasoningTool:
    def __init__(self):
        pass

    def sally_anne_test_wrapper(self, model, evidence):
        return sally_anne_test(model, evidence)

    def solve_sat_wrapper(self, formula):
        return solve_sat(formula)

    def detect_confounders_wrapper(self, graph, query_vars):
        return detect_confounders(graph, query_vars)