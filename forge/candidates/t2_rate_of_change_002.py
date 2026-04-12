from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import alanine

class ReasoningTool:
    def __init__(self):
        pass

    def update_beliefs(self, observations, prior):
        return bayesian_update(observations, prior)

    def calculate_entropy(self, distribution):
        return entropy(distribution)

    def compute_confidence(self, agreement_data):
        return confidence_from_agreement(agreement_data)

    def perform_counterfactual_intervention(self, model, intervention):
        return counterfactual_intervention(model, intervention)