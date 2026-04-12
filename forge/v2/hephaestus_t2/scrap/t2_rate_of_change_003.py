from forge_primitives import solve_sat, dag_traverse, counterfactual_intervention
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query

class ReasoningTool:
    def __init__(self):
        self.dag = None

    def load_dag(self, edges):
        self.dag = build_bn(edges)

    def query_counterfactual(self, evidence, intervention_node, intervention_value):
        return counterfactual_intervention(self.dag, evidence, intervention_node, intervention_value)

    def solve_sat_problem(self, clause_set):
        return solve_sat(clause_set)