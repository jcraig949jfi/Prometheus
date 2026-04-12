from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention, dag_traverse
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders

class ReasoningTool:
    def __init__(self):
        pass

    def update_beliefs(self, evidence, beliefs):
        return bayesian_update(evidence, beliefs)

    def calculate_entropy(self, distribution):
        return entropy(distribution)

    def compute_confidence(self, agreement):
        return confidence_from_agreement(agreement)

    def intervene_counterfactually(self, model, intervention):
        return counterfactual_intervention(model, intervention)

    def traverse_dag(self, graph):
        return dag_traverse(graph)

    def build_bayesian_network(self, nodes, edges):
        return build_bn(nodes, edges)

    def query_conditional_probability(self, bn, query_node, evidence_nodes):
        return conditional_query(bn, query_node, evidence_nodes)

    def detect_confounders_in_model(self, model):
        return detect_confounders(model)