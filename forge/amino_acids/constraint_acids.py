"""Amino acids decomposed from python-constraint (v2.5.0) — constraint satisfaction.

Each function is 5-20 lines, performs one atomic reasoning operation,
and wraps a specific python-constraint capability that T1 primitives lack.
"""
from forge.amino_acids.registry import amino_acid


@amino_acid(
    id="csp_solve_first",
    source="python_constraint",
    reasoning_type="constraint",
    description="Find the first solution to a constraint satisfaction problem"
)
def solve_first(variables_domains, constraints):
    """Find one solution to a CSP.
    
    Args:
        variables_domains: dict of {var_name: list_of_domain_values}
        constraints: list of (func, var_names_tuple) where func returns bool
    Returns:
        dict mapping variable names to values, or None if no solution exists
    """
    from constraint import Problem
    p = Problem()
    for var, domain in variables_domains.items():
        p.addVariable(var, domain)
    for func, var_names in constraints:
        p.addConstraint(func, var_names)
    return p.getSolution()


@amino_acid(
    id="csp_solve_all",
    source="python_constraint",
    reasoning_type="constraint",
    description="Find ALL solutions to a CSP to check uniqueness or enumerate possibilities"
)
def solve_all(variables_domains, constraints, max_solutions=1000):
    """Find all solutions to a CSP.
    
    Returns:
        list of dicts, each mapping variable names to values
    """
    from constraint import Problem
    p = Problem()
    for var, domain in variables_domains.items():
        p.addVariable(var, domain)
    for func, var_names in constraints:
        p.addConstraint(func, var_names)
    solutions = p.getSolutions()
    return solutions[:max_solutions]


@amino_acid(
    id="csp_is_uniquely_solvable",
    source="python_constraint",
    reasoning_type="constraint",
    description="Check if a CSP has exactly one solution (uniqueness test)"
)
def is_uniquely_solvable(variables_domains, constraints):
    """Check if a CSP has exactly one solution.
    
    Returns:
        dict with 'unique' (bool), 'count' (int), 'solution' (dict or None)
    """
    from constraint import Problem
    p = Problem()
    for var, domain in variables_domains.items():
        p.addVariable(var, domain)
    for func, var_names in constraints:
        p.addConstraint(func, var_names)
    solutions = p.getSolutions()
    count = len(solutions)
    return {
        "unique": count == 1,
        "count": count,
        "solution": solutions[0] if count == 1 else None,
    }


@amino_acid(
    id="csp_count_solutions",
    source="python_constraint",
    reasoning_type="constraint",
    description="Count the number of valid solutions to a CSP"
)
def count_solutions(variables_domains, constraints):
    """Count solutions without returning them all (though internally it enumerates).
    
    Returns:
        int: number of solutions
    """
    from constraint import Problem
    p = Problem()
    for var, domain in variables_domains.items():
        p.addVariable(var, domain)
    for func, var_names in constraints:
        p.addConstraint(func, var_names)
    return len(p.getSolutions())


@amino_acid(
    id="csp_check_consistency",
    source="python_constraint",
    reasoning_type="constraint",
    description="Check if a CSP has ANY solution (consistency check)"
)
def check_consistency(variables_domains, constraints):
    """Check if a CSP is consistent (has at least one solution).
    
    Returns:
        bool: True if at least one solution exists
    """
    from constraint import Problem
    p = Problem()
    for var, domain in variables_domains.items():
        p.addVariable(var, domain)
    for func, var_names in constraints:
        p.addConstraint(func, var_names)
    return p.getSolution() is not None


@amino_acid(
    id="csp_find_conflicts",
    source="python_constraint",
    reasoning_type="metacognitive",
    description="Identify which constraints conflict by testing each subset"
)
def find_conflicts(variables_domains, constraints):
    """Find which constraints are in conflict by testing satisfiability
    with each constraint removed.
    
    Returns:
        list of indices of constraints that, when removed, make the problem solvable.
        These are the 'conflict participants'.
    """
    from constraint import Problem
    conflict_indices = []
    for i in range(len(constraints)):
        p = Problem()
        for var, domain in variables_domains.items():
            p.addVariable(var, domain)
        for j, (func, var_names) in enumerate(constraints):
            if j != i:
                p.addConstraint(func, var_names)
        if p.getSolution() is not None:
            conflict_indices.append(i)
    return conflict_indices
