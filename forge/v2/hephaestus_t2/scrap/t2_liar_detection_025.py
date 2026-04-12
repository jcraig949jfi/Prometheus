from forge_primitives import sally_anne_test, solve_sat, track_beliefs
from forge.amino_acids.pgmpy_acids import build_bn

class ReasoningTool:
    def __init__(self):
        pass

    def perform_reasoning(self, belief_system, query, constraints=None):
        # Use Sally Anne test to update beliefs
        updated_beliefs = sally_anne_test(belief_system, query)
        
        if constraints is not None:
            # Solve constraints using SAT solver
            solution = solve_sat(constraints)
            if solution:
                # Apply the solution to update beliefs further
                updated_beliefs = track_beliefs(updated_beliefs, solution)
        
        return updated_beliefs

    def build_causal_model(self, variables, edges):
        # Build a Bayesian network from variables and edges
        bn = build_bn(variables, edges)
        return bn

    def query_causal_model(self, bn, evidence):
        # Query the causal model with evidence
        result = conditional_query(bn, evidence)
        return result

    def detect_confounding_variables(self, bn, outcome, treatment):
        # Detect confounders in a causal model
        confounders = detect_confounders(bn, outcome, treatment)
        return confounders