"""TOOL_SAT_SOLVER - SAT solver wrapper for CNF combinatorics.

Interface:
    solve_cnf(clauses, solver='kissat', timeout=None) -> dict

Input clauses use DIMACS-style integer literals: positive i means variable i,
negative -i means not variable i. Variables are 1-indexed. The default backend
is PySAT's bundled Kissat 4.0.4 wrapper when present; Glucose is used as the
portable fallback.

Forged: 2026-04-26 | Tier: 1 (PySAT wrapper) | REQ-026
Backend: python-sat / pysat.solvers. Kissat is bundled as ``kissat404`` in this
environment; no solver binary is committed to the repository.
"""
from __future__ import annotations

import os
from threading import Timer
from time import perf_counter
from typing import Iterable

try:
    from pysat.solvers import Solver
except Exception as exc:  # pragma: no cover - exercised only if dependency is absent
    Solver = None
    _PYSAT_IMPORT_ERROR = exc
else:
    _PYSAT_IMPORT_ERROR = None


_SOLVER_ALIASES = {
    "kissat": ["kissat404", "glucose3"],
    "kissat404": ["kissat404", "glucose3"],
    "glucose": ["glucose3"],
    "glucose3": ["glucose3"],
    "glucose4": ["glucose4", "glucose3"],
    "minisat": ["minisat22", "glucose3"],
    "minisat22": ["minisat22", "glucose3"],
}


def _normalize_clauses(clauses: Iterable[Iterable[int]]) -> list[list[int]]:
    normalized: list[list[int]] = []
    for i, clause in enumerate(clauses):
        try:
            lits = [int(lit) for lit in clause]
        except TypeError as exc:
            raise ValueError(f"clause {i} is not iterable") from exc
        if any(lit == 0 for lit in lits):
            raise ValueError("DIMACS literal 0 is a clause terminator, not a valid literal")
        normalized.append(lits)
    return normalized


def _candidate_backends(solver: str) -> list[str]:
    key = solver.lower()
    candidates = _SOLVER_ALIASES.get(key, [key])
    # PySAT's bundled Kissat wrapper is present on this Windows harness but
    # segfaults on small UNSAT certificates. Prefer the stable fallback here.
    if os.name == "nt" and candidates and candidates[0] == "kissat404":
        return candidates[1:] + candidates[:1]
    return candidates


def _accum_stats(sat) -> dict:
    try:
        return sat.accum_stats()
    except NotImplementedError:
        return {}


def _new_solver(requested: str):
    if Solver is None:
        raise RuntimeError(
            "python-sat is not importable; install with `pip install python-sat[aiger]`"
        ) from _PYSAT_IMPORT_ERROR

    errors: list[str] = []
    for backend in _candidate_backends(requested):
        try:
            return backend, Solver(name=backend)
        except Exception as exc:
            errors.append(f"{backend}: {type(exc).__name__}: {exc}")
    raise RuntimeError(f"no PySAT backend available for {requested!r}; tried {errors}")


def solve_cnf(
    clauses: list[list[int]],
    solver: str = "kissat",
    timeout: float | None = None,
) -> dict:
    """Solve a CNF formula and return a stable Prometheus result dict.

    Parameters
    ----------
    clauses:
        DIMACS-style CNF, e.g. ``[[1, -2], [2, 3], [-1]]``.
    solver:
        Backend alias. ``'kissat'`` maps to PySAT ``kissat404`` with Glucose3
        fallback. ``'glucose'`` maps to Glucose3 directly.
    timeout:
        Optional wall-clock timeout in seconds. If the timeout fires, returns
        ``{'satisfiable': None, 'model': None, 'stats': {'timed_out': True, ...}}``.

    Returns
    -------
    dict
        ``satisfiable`` is True, False, or None when interrupted by timeout.
        ``model`` is a list of signed literals when satisfiable, else None.
        ``stats`` includes backend, requested solver, clause/variable counts,
        elapsed time, timeout state, and raw PySAT accumulator fields.
    """
    if timeout is not None and timeout < 0:
        raise ValueError("timeout must be non-negative or None")

    cnf = _normalize_clauses(clauses)
    num_vars = max((abs(lit) for clause in cnf for lit in clause), default=0)
    backend, sat = _new_solver(solver)
    timer: Timer | None = None
    timed_out = False
    started = perf_counter()

    try:
        for clause in cnf:
            sat.add_clause(clause)

        if timeout is None:
            result = sat.solve()
        else:
            if timeout == 0:
                sat.interrupt()
                result = None
                timed_out = True
            else:
                def _interrupt() -> None:
                    sat.interrupt()

                timer = Timer(timeout, _interrupt)
                timer.daemon = True
                timer.start()
                result = sat.solve_limited(expect_interrupt=True)
                timed_out = result is None
    finally:
        if timer is not None:
            timer.cancel()

    elapsed = perf_counter() - started
    stats = {
        "solver": backend,
        "requested_solver": solver,
        "num_clauses": len(cnf),
        "num_vars": num_vars,
        "elapsed_seconds": elapsed,
        "timeout_seconds": timeout,
        "timed_out": timed_out,
        "pysat_accum_stats": _accum_stats(sat),
    }

    if result is True:
        model = sat.get_model()
        satisfiable: bool | None = True
    elif result is False:
        model = None
        satisfiable = False
    else:
        model = None
        satisfiable = None

    sat.delete()
    return {"satisfiable": satisfiable, "model": model, "stats": stats}


__all__ = ["solve_cnf"]
