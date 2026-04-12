from forge_primitives import dag_traverse, track_beliefs, solve_constraints, counterfactual_intervention
from forge.amino_acids.pgmpy_acids import detect_confounders

class ReasoningTool:
    @staticmethod
    def infer_causal_structure(data):
        # Use DAG traversal to infer causal structure
        return dag_traverse(data)

    @staticmethod
    def track_reasoning_progress(model, evidence):
        # Track the reasoning progress using belief tracking
        return track_beliefs(model, evidence)

    @staticmethod
    def solve_complex_constraints(constraints):
        # Solve complex constraints using constraint solving
        return solve_constraints(constraints)

    @staticmethod
    def intervene_in_causal_model(model, intervention):
        # Perform a counterfactual intervention in the causal model
        return counterfactual_intervention(model, intervention)

    @staticmethod
    def detect_confounding_variables(model):
        # Detect confounding variables using pgmpy's built-in function
        return detect_confounders(model)