"""PHASE 2 REPAIR D3 -- the primary objective carries no relevance shaping.

Phase 1's draft organizer objective was

    fitness = mean[train-exact solved] + 0.01 * mean[best train fitness]

The second term was labelled a tie-break. Two defects were confirmed:

  (a) ARITHMETIC. It is a strict tie-break only while the minimum
      solve-rate increment 1/(N_fit * trials) exceeds 0.01, i.e. only for
      fewer than 100 fitting units. At any realistic fitting-set size it
      can overturn a genuine one-solve difference.
  (b) ONTOLOGY, the serious half. `best_train_fitness` is
      cases_passed / n_train, so the term asserts "an experience is
      relevant to a query if it passes more of that query's train cases"
      -- which is EXACTLY the criterion the privileged PP1 oracle uses to
      rank the corpus. The objective would hand the organizer a smoothed
      copy of the ceiling it is supposed to discover, and being
      query-conditional it does not difference out of the primary
      contrast.

The primary objective is therefore the ENDPOINT ALONE. No shaping term,
no partial credit, no train-fitness proxy, under any name.

Any shaped variant is CONTAMINATED, must be labelled non-primary, and may
never be used to establish a capacity result.
"""
from __future__ import annotations

import inspect

# Names that encode the PP1 relevance criterion, in any disguise.
FORBIDDEN_OBJECTIVE_TERMS = (
    "best_train_fitness", "cases_passed", "partial_credit", "train_fitness",
    "solved_train", "fitness_shaping", "shaping",
)

PRIMARY_METRIC = "test_exact_solve_rate"
PRIMARY_METRIC_DOC = (
    "Fraction of acquisition trials whose first train-exact solution also "
    "reproduces the held-out test split exactly. Oracle-side, never visible "
    "to the search, and carrying no partial credit."
)


def primary_objective(results) -> float:
    """The ONLY objective admissible for a capacity decision."""
    rs = list(results)
    if not rs:
        return 0.0
    return sum(1 for r in rs if r.solved_test) / len(rs)


def audit_no_shaping(*modules) -> list:
    """Fail-closed source audit: no admissible objective path may mention a
    PP1-equivalent relevance proxy. Returns a list of violations."""
    hits = []
    for m in modules:
        try:
            src = inspect.getsource(m)
        except (OSError, TypeError):
            continue
        body = "\n".join(
            ln for ln in src.splitlines()
            if not ln.lstrip().startswith("#"))
        for term in FORBIDDEN_OBJECTIVE_TERMS:
            if term in body:
                hits.append({"module": getattr(m, "__name__", str(m)),
                             "term": term})
    return hits
