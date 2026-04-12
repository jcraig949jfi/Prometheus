from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention, dag_traverse, check_transitivity, topological_sort, track_beliefs, sally_anne_test, solve_sat, solve_constraints, solve_linear_system, expected_value, information_sufficiency, modus_ponens, temporal_order, modular_arithmetic, fencepost_count, parity_check, negate, pigeonhole_check, coin_flip_independence, bat_and_ball, all_but_n, direction_composition
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, do_calculus, get_adjustment_set, compare_conditional_marginal, active_trails, map_query, find_dseparators, get_markov_blanket

class ReasoningTool:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def update_beliefs(self, new_evidence):
        return bayesian_update(self.knowledge_base, new_evidence)

    def calculate_entropy(self, distribution):
        return entropy(distribution)

    def get_confidence(self, agreement):
        return confidence_from_agreement(agreement)

    def infer_counterfactual(self, intervention):
        return counterfactual_intervention(self.knowledge_base, intervention)

    def traverse_dag(self, graph):
        return dag_traverse(graph)

    def check_transitivity(self, relation):
        return check_transitivity(relation)

    def topologically_sort(self, dag):
        return topological_sort(dag)

    def track_inference(self, initial_state, actions):
        return track_beliefs(initial_state, actions)

    def sally_anne_test_case(self, scenario):
        return sally_anne_test(scenario)

    def solve_satisfiability(self, formula):
        return solve_sat(formula)

    def solve_constraints(self, system):
        return solve_constraints(system)

    def solve_linear_system(self, coefficients, constants):
        return solve_linear_system(coefficients, constants)

    def expected_value_calculation(self, outcomes):
        return expected_value(outcomes)

    def information_sufficiency_check(self, data, model):
        return information_sufficiency(data, model)

    def apply_modus_ponens(self, premise, conclusion):
        return modus_ponens(premise, conclusion)

    def determine_temporal_order(self, events):
        return temporal_order(events)

    def perform_modular_arithmetic(self, operands, operator):
        return modular_arithmetic(operands, operator)

    def count_fencepost_errors(self, n):
        return fencepost_count(n)

    def verify_parity(self, number):
        return parity_check(number)

    def negate_statement(self, statement):
        return negate(statement)

    def check_pigeonhole Principle(self, items, containers):
        return pigeonhole_check(items, containers)

    def assess_coin_flip_independence(self, flip1, flip2):
        return coin_flip_independence(flip1, flip2)

    def solve_bat_and_ball_problem(self, setup):
        return bat_and_ball(setup)

    def apply_all_but_n_rule(self, selection, n):
        return all_but_n(selection, n)

    def compose_directions(self, direction1, direction2):
        return direction_composition(direction1, direction2)

    def build_bayesian_network(self, structure, probabilities):
        return build_bn(structure, probabilities)

    def query_conditional_probability(self, network, variables, evidence):
        return conditional_query(network, variables, evidence)

    def detect_confounding_variables(self, network, target, confounders):
        return detect_confounders(network, target, confounders)