from forge_primitives import bayesian_update, entropy, sally_anne_test, topological_sort, check_transitivity
from forge.amino_acids.pgmpy_acids import build_bn, do_calculus

class ReasoningTool:
    def __init__(self):
        pass

    def update_beliefs(self, evidence, prior):
        return bayesian_update(evidence, prior)

    def calculate_entropy(self, distribution):
        return entropy(distribution)

    def sally_anne_test_check(self, hypothesis1, hypothesis2, evidence):
        return sally_anne_test(hypothesis1, hypothesis2, evidence)

    def topological_sort_graph(self, graph):
        return topological_sort(graph)

    def check_confidence_consistency(self, beliefs):
        return check_transitivity(beliefs)