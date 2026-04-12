from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention, dag_traverse, check_transitivity, topological_sort, track_beliefs, sally_anne_test, solve_sat, solve_constraints, solve_linear_system, expected_value, information_sufficiency, modus_ponens, temporal_order, modular_arithmetic, fencepost_count, parity_check, negate, pigeonhole_check, coin_flip_independence, bat_and_ball, all_but_n, direction_composition
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, do_calculus, get_adjustment_set, compare_conditional_marginal, active_trails, map_query, find_dseparators, get_markov_blanket

class ReasoningTool:
    def __init__(self):
        pass

    def bayesian_update(self, prior, likelihood, evidence):
        return bayesian_update(prior, likelihood, evidence)

    def entropy(self, probabilities):
        return entropy(probabilities)

    def confidence_from_agreement(self, agreements):
        return confidence_from_agreement(agreements)

    def counterfactual_intervention(self, model, intervention):
        return counterfactual_intervention(model, intervention)

    def dag_traverse(self, graph):
        return dag_traverse(graph)

    def check_transitivity(self, relations):
        return check_transitivity(relations)

    def topological_sort(self, graph):
        return topological_sort(graph)

    def track_beliefs(self, agents, evidence):
        return track_beliefs(agents, evidence)

    def sally_anne_test(self, test_cases):
        return sally_anne_test(test_cases)

    def solve_sat(self, formula):
        return solve_sat(formula)

    def solve_constraints(self, constraints):
        return solve_constraints(constraints)

    def solve_linear_system(self, equations):
        return solve_linear_system(equations)

    def expected_value(self, distribution):
        return expected_value(distribution)

    def information_sufficiency(self, data, parameters):
        return information_sufficiency(data, parameters)

    def modus_ponens(self, premise, hypothesis):
        return modus_ponens(premise, hypothesis)

    def temporal_order(self, events):
        return temporal_order(events)

    def modular_arithmetic(self, number, modulus):
        return modular_arithmetic(number, modulus)

    def fencepost_count(self, intervals):
        return fencepost_count(intervals)

    def parity_check(self, number):
        return parity_check(number)

    def negate(self, statement):
        return negate(statement)

    def pigeonhole_check(self, pigeons, holes):
        return pigeonhole_check(pigeons, holes)

    def coin_flip_independence(self, flip1, flip2):
        return coin_flip_independence(flip1, flip2)

    def bat_and_ball(self, bat_weight, ball_weight):
        return bat_and_ball(bat_weight, ball_weight)

    def all_but_n(self, items, n):
        return all_but_n(items, n)

    def direction_composition(self, direction1, direction2):
        return direction_composition(direction1, direction2)

    def build_bn(self, nodes, edges):
        return build_bn(nodes, edges)

    def conditional_query(self, bn, query, evidence):
        return conditional_query(bn, query, evidence)

    def detect_confounders(self, bn, variables):
        return detect_confounders(bn, variables)

    def do_calculus(self, bn, intervention):
        return do_calculus(bn, intervention)

    def get_adjustment_set(self, bn, treatment, outcome):
        return get_adjustment_set(bn, treatment, outcome)

    def compare_conditional_marginal(self, bn, variable1, variable2, evidence):
        return compare_conditional_marginal(bn, variable1, variable2, evidence)

    def active_trails(self, bn, start, end):
        return active_trails(bn, start, end)

    def map_query(self, bn, query, evidence):
        return map_query(bn, query, evidence)

    def find_dseparators(self, bn, variables):
        return find_dseparators(bn, variables)

    def get_markov_blanket(self, bn, node):
        return get_markov_blanket(bn, node)