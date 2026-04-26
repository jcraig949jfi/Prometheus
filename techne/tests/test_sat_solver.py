"""Test TOOL_SAT_SOLVER."""
import itertools
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.sat_solver import solve_cnf


def _model_assignment(model):
    return {abs(lit): lit > 0 for lit in model}


def _satisfies(clauses, model):
    assignment = _model_assignment(model)
    return all(any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
               for clause in clauses)


def _ch_no_short_cycle_cnf(n, min_outdegree, max_cycle_len):
    """Small Caccetta-Haggkvist SAT certificate encoding.

    Variables x_{i,j} mean directed edge i -> j for i != j. The formula asks
    for a digraph on n vertices with outdegree >= min_outdegree and no directed
    cycle of length <= max_cycle_len. For n=5, min_outdegree=2, max_cycle_len=3,
    CH predicts impossibility because ceil(5/2)=3.
    """
    var = {}
    next_var = 1
    for i in range(n):
        for j in range(n):
            if i != j:
                var[(i, j)] = next_var
                next_var += 1

    clauses = []

    # No directed 2-cycles.
    if max_cycle_len >= 2:
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var[(i, j)], -var[(j, i)]])

    # No directed 3-cycles.
    if max_cycle_len >= 3:
        for i, j, k in itertools.permutations(range(n), 3):
            clauses.append([-var[(i, j)], -var[(j, k)], -var[(k, i)]])

    # Outdegree >= 2 for the calibration case. Encoding: every triple of the
    # four possible outgoing edges has at least one selected edge.
    if min_outdegree != 2:
        raise ValueError("test helper currently encodes only min_outdegree=2")
    for i in range(n):
        outgoing = [var[(i, j)] for j in range(n) if j != i]
        for triple in itertools.combinations(outgoing, len(outgoing) - min_outdegree + 1):
            clauses.append(list(triple))

    return clauses


def test_3sat_satisfiable_model_verifies():
    clauses = [
        [1, 2, 3],
        [-1, 2, -3],
        [1, -2, 3],
        [-1, -2, 3],
    ]
    result = solve_cnf(clauses, solver='kissat')

    assert result['satisfiable'] is True
    assert result['model'] is not None
    assert _satisfies(clauses, result['model'])
    assert result['stats']['solver'] in {'kissat404', 'glucose3'}
    assert result['stats']['num_vars'] == 3
    assert result['stats']['num_clauses'] == 4


def test_3sat_unsatisfiable():
    clauses = [[1, 2, 3], [-1], [-2], [-3]]
    result = solve_cnf(clauses, solver='glucose')

    assert result['satisfiable'] is False
    assert result['model'] is None
    assert result['stats']['solver'] == 'glucose3'


def test_caccetta_haggkvist_small_certificate_unsat():
    clauses = _ch_no_short_cycle_cnf(n=5, min_outdegree=2, max_cycle_len=3)
    result = solve_cnf(clauses, solver='kissat')

    assert result['satisfiable'] is False
    assert result['model'] is None
    assert result['stats']['num_vars'] == 20


def test_timeout_behavior():
    result = solve_cnf([[1]], solver='glucose', timeout=0)

    assert result['satisfiable'] is None
    assert result['model'] is None
    assert result['stats']['timed_out'] is True
    assert result['stats']['timeout_seconds'] == 0


if __name__ == '__main__':
    test_3sat_satisfiable_model_verifies()
    test_3sat_unsatisfiable()
    test_caccetta_haggkvist_small_certificate_unsat()
    test_timeout_behavior()
    print("\nALL SAT_SOLVER TESTS PASS")
