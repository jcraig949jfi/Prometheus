from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention, dag_traverse, check_transitivity, topological_sort, track_beliefs, sally_anne_test, solve_sat, solve_constraints, solve_linear_system, expected_value, information_sufficiency, modus_ponens, temporal_order, modular_arithmetic, fencepost_count, parity_check, negate, pigeonhole_check, coin_flip_independence, bat_and_ball, all_but_n, direction_composition
from forge.amino_acids.pgmpy_acids import build_bn

class ReasoningTool:
    def __init__(self):
        pass

    def bayesian_update(self, prior, likelihood, evidence):
        return bayesian_update(prior, likelihood, evidence)

    def entropy(self, distribution):
        return entropy(distribution)

    def confidence_from_agreement(self, agreements):
        return confidence_from_agreement(agreements)

    def counterfactual_intervention(self, model, intervention):
        return counterfactual_intervention(model, intervention)

    def dag_traverse(self, dag):
        return dag_traverse(dag)

    def check_transitivity(self, relations):
        return check_transitivity(relations)

    def topological_sort(self, graph):
        return topological_sort(graph)

    def track_beliefs(self, beliefs):
        return track_beliefs(beliefs)

    def sally_anne_test(self, agent1, agent2):
        return sally_anne_test(agent1, agent2)

    def solve_sat(self, formula):
        return solve_sat(formula)

    def solve_constraints(self, constraints):
        return solve_constraints(constraints)

    def solve_linear_system(self, matrix, vector):
        return solve_linear_system(matrix, vector)

    def expected_value(self, distribution, values):
        return expected_value(distribution, values)

    def information_sufficiency(self, data, parameter):
        return information_sufficiency(data, parameter)

    def modus_ponens(self, premise1, premise2):
        return modus_ponens(premise1, premise2)

    def temporal_order(self, events):
        return temporal_order(events)

    def modular_arithmetic(self, number, modulus):
        return modular_arithmetic(number, modulus)

    def fencepost_count(self, length):
        return fencepost_count(length)

    def parity_check(self, number):
        return parity_check(number)

    def negate(self, statement):
        return negate(statement)

    def pigeonhole_check(self, items, holes):
        return pigeonhole_check(items, holes)

    def coin_flip_independence(self, flip1, flip2):
        return coin_flip_independence(flip1, flip2)

    def bat_and_ball(self, bat_weight, ball_weight):
        return bat_and_ball(bat_weight, ball_weight)

    def all_but_n(self, list, n):
        return all_but_n(list, n)

    def direction_composition(self, vector1, vector2):
        return direction_composition(vector1, vector2)

    def build_bn(self, structure, factors):
        return build_bn(structure, factors)