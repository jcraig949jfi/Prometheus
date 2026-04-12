from forge_primitives import expected_value, confidence_from_agreement, dag_traverse
from forge.amino_acids.pgmpy_acids import alanine

class ReasoningTool:
    def __init__(self, beliefs):
        self.beliefs = beliefs

    def update_belief(self, evidence):
        updated_beliefs = {}
        for key, value in self.beliefs.items():
            updated_beliefs[key] = expected_value(value, evidence)
        return updated_beliefs

    def check_consistency(self):
        return confidence_from_agreement(self.beliefs)

    def traverse_dag(self, dag):
        return dag_traverse(dag, self.beliefs)