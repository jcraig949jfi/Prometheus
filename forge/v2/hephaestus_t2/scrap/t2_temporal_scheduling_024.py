from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention, dag_traverse, check_transitivity, topological_sort, track_beliefs, sally_anne_test, solve_sat, solve_constraints, solve_linear_system, expected_value, information_sufficiency, modus_ponens, temporal_order, modular_arithmetic, fencepost_count, parity_check, negate, pigeonhole_check, coin_flip_independence, bat_and_ball, all_but_n, direction_composition
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, do_calculus, get_adjustment_set, compare_conditional_marginal, active_trails, map_query, find_dseparators, get_markov_blanket

class ReasoningTool:
    @staticmethod
    def bayesian_update(prior, likelihood):
        return bayesian_update(prior, likelihood)

    @staticmethod
    def entropy(data):
        return entropy(data)

    @staticmethod
    def confidence_from_agreement(agreement):
        return confidence_from_agreement(agreement)

    @staticmethod
    def counterfactual_intervention(model, intervention):
        return counterfactual_intervention(model, intervention)

    @staticmethod
    def dag_traverse(graph):
        return dag_traverse(graph)

    @staticmethod
    def check_transitivity(relation):
        return check_transitivity(relation)

    @staticmethod
    def topological_sort(graph):
        return topological_sort(graph)

    @staticmethod
    def track_beliefs(model, evidence):
        return track_beliefs(model, evidence)

    @staticmethod
    def sally_anne_test(test_case):
        return sally_anne_test(test_case)

    @staticmethod
    def solve_sat(formula):
        return solve_sat(formula)

    @staticmethod
    def solve_constraints(constraints):
        return solve_constraints(constraints)

    @staticmethod
    def solve_linear_system(coefficients, constants):
        return solve_linear_system(coefficients, constants)

    @staticmethod
    def expected_value(distribution):
        return expected_value(distribution)

    @staticmethod
    def information_sufficiency(model, data):
        return information_sufficiency(model, data)

    @staticmethod
    def modus_ponens(premise1, premise2):
        return modus_ponens(premise1, premise2)

    @staticmethod
    def temporal_order(events):
        return temporal_order(events)

    @staticmethod
    def modular_arithmetic(operation, operands):
        return modular_arithmetic(operation, operands)

    @staticmethod
    def fencepost_count(length):
        return fencepost_count(length)

    @staticmethod
    def parity_check(number):
        return parity_check(number)

    @staticmethod
    def negate(value):
        return negate(value)

    @staticmethod
    def pigeonhole_check(boxes, items):
        return pigeonhole_check(boxes, items)

    @staticmethod
    def coin_flip_independence(flips):
        return coin_flip_independence(flips)

    @staticmethod
    def bat_and_ball():
        return bat_and_ball()

    @staticmethod
    def all_but_n(n, items):
        return all_but_n(n, items)

    @staticmethod
    def direction_composition(direction1, direction2):
        return direction_composition(direction1, direction2)

    @staticmethod
    def build_bn(data):
        return build_bn(data)

    @staticmethod
    def conditional_query(model, query):
        return conditional_query(model, query)

    @staticmethod
    def detect_confounders(graph, variables):
        return detect_confounders(graph, variables)