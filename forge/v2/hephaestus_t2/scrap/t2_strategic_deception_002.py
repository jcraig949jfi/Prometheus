from forge_primitives import bayesian_update, entropy, confidence_from_agreement
from forge.amino_acids.pgmpy_acids import alanine

class ReasoningTool:
    def __init__(self):
        self.beliefs = {}

    def update_belief(self, evidence):
        for hypothesis, belief in evidence.items():
            updated_belief = bayesian_update(belief, self.beliefs.get(hypothesis, 0.5))
            self.beliefs[hypothesis] = updated_belief

    def calculate_entropy(self):
        return entropy(list(self.beliefs.values()))

    def get_confidence(self, hypothesis):
        return confidence_from_agreement(self.beliefs[hypothesis])

    def add_counterfactual_intervention(self, intervention):
        counterfactual_intervention(intervention, self.beliefs)