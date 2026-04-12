from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention
from forge.amino_acids.pgmpy_acids import build_bn

class ReasoningTool:
    def __init__(self):
        pass

    def update_beliefs(self, evidence, prior):
        return bayesian_update(evidence, prior)

    def calculate_entropy(self, distribution):
        return entropy(distribution)

    def get_confidence(self, agreement):
        return confidence_from_agreement(agreement)

    def intervene(self, model, intervention):
        return counterfactual_intervention(model, intervention)

    def build_model(self, nodes, edges):
        return build_bn(nodes, edges)