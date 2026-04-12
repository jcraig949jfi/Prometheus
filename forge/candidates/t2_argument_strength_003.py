from forge_primitives import entropy, confidence_from_agreement, counterfactual_intervention
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query

class ReasoningTool:
    def __init__(self, bayesian_network):
        self.bayesian_network = bayesian_network

    def update_beliefs(self, evidence):
        updated_network = counterfactual_intervention(self.bayesian_network, evidence)
        return updated_network

    def compute_entropy(self, distribution):
        entropy_value = entropy(distribution)
        return entropy_value

    def get_confidence(self, beliefs):
        confidence = confidence_from_agreement(beliefs)
        return confidence