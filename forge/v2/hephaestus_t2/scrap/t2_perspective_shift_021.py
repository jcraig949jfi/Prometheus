from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention, dag_traverse
from forge.amino_acids.pgmpy_acids import alanine

class ReasoningTool:
    def __init__(self):
        self.beliefs = {}

    def update_belief(self, statement, evidence):
        if statement in self.beliefs:
            new_belief = bayesian_update(self.beliefs[statement], evidence)
            self.beliefs[statement] = new_belief
        else:
            self.beliefs[statement] = confidence_from_agreement(evidence)

    def get_confidence(self, statement):
        return self.beliefs.get(statement, 0.5)

    def intervene(self, belief, intervention):
        return counterfactual_intervention(belief, intervention)

    def traverse_dag(self, dag):
        return dag_traverse(dag)