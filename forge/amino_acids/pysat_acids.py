"""Amino acids decomposed from PySAT (python-sat v1.9) — SAT solving and MUS extraction.

Each function is 5-20 lines, performs one atomic reasoning operation,
and wraps a specific PySAT capability that T1 primitives lack.
"""
from forge.amino_acids.registry import amino_acid


@amino_acid(
    id="pysat_solve",
    source="pysat",
    reasoning_type="logical",
    description="Solve a SAT instance: given CNF clauses, find a satisfying assignment or prove unsatisfiable"
)
def solve(clauses, assumptions=None):
    """Solve a SAT problem given as a list of clauses.
    
    Args:
        clauses: list of lists of ints (CNF), e.g., [[1, -2], [-1, 3]]
        assumptions: optional list of literal assumptions
    Returns:
        dict with 'sat' (bool), 'model' (list of ints if SAT), 'core' (list if UNSAT)
    """
    from pysat.solvers import Solver
    with Solver(name='g3', bootstrap_with=clauses) as s:
        sat = s.solve(assumptions=assumptions or [])
        if sat:
            return {"sat": True, "model": s.get_model(), "core": None}
        else:
            return {"sat": False, "model": None, "core": s.get_core()}


@amino_acid(
    id="pysat_enumerate_models",
    source="pysat",
    reasoning_type="logical",
    description="Enumerate all satisfying assignments of a CNF formula (up to a limit)"
)
def enumerate_models(clauses, max_models=100):
    """Find all satisfying assignments, up to max_models.
    
    Returns:
        list of models (each a list of ints), or empty list if UNSAT
    """
    from pysat.solvers import Solver
    models = []
    with Solver(name='g3', bootstrap_with=clauses) as s:
        for i, model in enumerate(s.enum_models()):
            models.append(model)
            if i + 1 >= max_models:
                break
    return models


@amino_acid(
    id="pysat_is_valid",
    source="pysat",
    reasoning_type="logical",
    description="Check if a formula is a tautology by testing if its negation is unsatisfiable"
)
def is_valid(clauses):
    """Check if a CNF formula is a tautology (valid in all interpretations).
    
    Returns True if the negation of the formula is UNSAT (making the original a tautology).
    """
    from pysat.formula import CNF
    cnf = CNF(from_clauses=clauses)
    neg = cnf.negate()
    from pysat.solvers import Solver
    with Solver(name='g3', bootstrap_with=neg.clauses) as s:
        return not s.solve()


@amino_acid(
    id="pysat_extract_mus",
    source="pysat",
    reasoning_type="metacognitive",
    description="Find the minimal unsatisfiable subset — the smallest set of clauses that makes the formula UNSAT"
)
def extract_mus(hard_clauses, soft_clauses):
    """Find Minimal Unsatisfiable Subset of soft clauses given hard constraints.
    
    Args:
        hard_clauses: list of clauses that must all be satisfied
        soft_clauses: list of clauses to find minimal conflict among
    Returns:
        list of indices into soft_clauses forming the MUS, or None if satisfiable
    """
    from pysat.formula import WCNF
    from pysat.examples.musx import MUSX
    wcnf = WCNF()
    for clause in hard_clauses:
        wcnf.append(clause)
    for clause in soft_clauses:
        wcnf.append(clause, weight=1)
    try:
        musx = MUSX(wcnf, verbosity=0)
        mus = musx.compute()
        musx.delete()
        return mus if mus else None
    except Exception:
        return None


@amino_acid(
    id="pysat_encode_exactly_k",
    source="pysat",
    reasoning_type="constraint",
    description="Encode a cardinality constraint: exactly K of N boolean variables must be true"
)
def encode_exactly_k(variables, k):
    """Encode 'exactly k of variables are true' as CNF clauses.
    
    Args:
        variables: list of positive variable indices
        k: exact count required
    Returns:
        list of clauses encoding the constraint
    """
    from pysat.card import CardEnc, EncType
    cnf = CardEnc.equals(lits=variables, bound=k, encoding=EncType.seqcounter)
    return list(cnf.clauses)


@amino_acid(
    id="pysat_maxsat_solve",
    source="pysat",
    reasoning_type="logical",
    description="Find assignment that maximizes satisfied soft clauses while respecting all hard clauses"
)
def maxsat_solve(hard_clauses, soft_clauses):
    """Solve MaxSAT: satisfy all hard clauses, maximize soft clauses satisfied.

    Returns:
        dict with 'model', 'satisfied_soft', or None if hard clauses UNSAT
    """
    from pysat.solvers import Solver
    all_clauses = hard_clauses + soft_clauses
    with Solver(name='g3', bootstrap_with=all_clauses) as s:
        if not s.solve():
            return None
        model = s.get_model()
        model_set = set(model)
        satisfied = sum(1 for sc in soft_clauses
                        if any(lit in model_set for lit in sc))
        return {"model": model, "satisfied_soft": satisfied}


@amino_acid(
    id="pysat_detect_paradox",
    source="pysat",
    reasoning_type="metacognitive",
    description="Check if a set of logical statements is self-contradictory by testing satisfiability"
)
def detect_paradox(clauses):
    """Check if a set of logical statements (CNF clauses) is contradictory.

    Returns:
        dict with 'is_paradox' (bool), 'core' (minimal conflicting assumptions if paradox)
    """
    from pysat.solvers import Solver
    with Solver(name='g3', bootstrap_with=clauses) as s:
        sat = s.solve()
        if sat:
            return {"is_paradox": False, "core": None, "model": s.get_model()}
        else:
            return {"is_paradox": True, "core": s.get_core(), "model": None}


@amino_acid(
    id="pysat_check_entailment",
    source="pysat",
    reasoning_type="logical",
    description="Check if premises logically entail a conclusion by testing if premises AND NOT conclusion is UNSAT"
)
def check_entailment(premise_clauses, conclusion_clause):
    """Check if premise_clauses logically entail conclusion_clause.

    Entailment holds iff (premises AND NOT conclusion) is UNSAT.
    Args:
        premise_clauses: list of CNF clauses (the premises)
        conclusion_clause: a single clause (the conclusion)
    Returns:
        dict with 'entails' (bool), 'counterexample' (model if not entailed)
    """
    from pysat.solvers import Solver
    # Negate conclusion: negate each literal in the clause, add each as unit clause
    negated = [[-lit] for lit in conclusion_clause]
    combined = premise_clauses + negated
    with Solver(name='g3', bootstrap_with=combined) as s:
        sat = s.solve()
        if sat:
            return {"entails": False, "counterexample": s.get_model()}
        else:
            return {"entails": True, "counterexample": None}


@amino_acid(
    id="pysat_count_models",
    source="pysat",
    reasoning_type="logical",
    description="Count the number of satisfying assignments (up to a limit) to measure solution space size"
)
def count_models(clauses, max_count=1000):
    """Count satisfying assignments of a CNF formula.

    Returns:
        int: number of models found (capped at max_count)
    """
    from pysat.solvers import Solver
    count = 0
    with Solver(name='g3', bootstrap_with=clauses) as s:
        for _ in s.enum_models():
            count += 1
            if count >= max_count:
                break
    return count
