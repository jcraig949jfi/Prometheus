from forge_primitives import counterfactual_intervention, dag_traverse, solve_constraints, expected_value, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import Alanine

class ReasoningTool:
    def __init__(self):
        self.model = None

    def set_model(self, model):
        self.model = model

    def infer_counterfactual(self, intervention, observation):
        return counterfactual_intervention(self.model, intervention, observation)

    def traverse_dag(self):
        return dag_traverse(self.model)

    def solve_model_constraints(self, constraints):
        return solve_constraints(self.model, constraints)

    def calculate_expected_value(self, values):
        return expected_value(self.model, values)

    def get_confidence_from_agreement(self, agreement_data):
        return confidence_from_agreement(agreement_data)