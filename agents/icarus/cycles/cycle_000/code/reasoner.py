"""
Icarus reasoner -- BOOTSTRAP (template level). MUTABLE: this is what Icarus
evolves, cycle by cycle, to climb Harmonia B's testable reasoning ladder.

Interface (required by the tier oracle):
    reason(probe) -> (answer, trace_dict)
where `probe` is a harmonia.experiments.reasoning_phase0.Probe.

The substrate is Python + sympy. Icarus builds the REASONING DISCIPLINE on top
of that substrate -- it does NOT reimplement sympy, and it cannot cheat: the
verifier lens grades by substitution into the original problem, so returning a
remembered answer fails. Real reasoning moves (handle perturbation, track
domain, reject extraneous roots, search counterexamples, locate the failing
proof step) are the only way up.

Bootstrap capability: clean linear equations only. Everything else returns
None. The whole point is that this is the BOTTOM of the ladder -- Icarus climbs.

Climbing targets (from the reference staircase):
  R0  survive isomorphism / rename / fractional-coeff perturbations of linear
  R1  quadratics incl. no-real-root cases (do NOT hallucinate roots)
  R2  sqrt(x+a)=x-b : square, then REJECT extraneous roots via domain/substitution
  R3  rational identity with an excluded value: cancel but EXCLUDE the singularity
  R5  invariant (parity) detection on tiling problems          [open frontier]
  R6  conjecture: search counterexamples, don't overgeneralize
  R7  proof repair: locate the first invalid step              [open frontier]
"""
from __future__ import annotations

from typing import Any, Tuple

import sympy as sp


def _solve_real_clean_linear(expr) -> list:
    syms = list(getattr(expr, "free_symbols", []))
    var = syms[0] if syms else sp.Symbol("x")
    return sorted({s for s in sp.solve(expr, var) if s.is_real}, key=float)


def reason(probe) -> Tuple[Any, dict]:
    """Bootstrap template reasoner. Solves only CLEAN LINEAR equations by
    direct pattern; returns None (with a trace) for everything else."""
    trace = {"operations_used": ["pattern_match"]}

    if probe.kind == "linear" and probe.version == "clean":
        trace["operations_used"] = ["solve_linear"]
        return _solve_real_clean_linear(probe.data["expr"]), trace

    # Everything else is beyond the bootstrap: perturbed linear, quadratics,
    # sqrt-with-domain, rationals, invariants, conjectures, proof-repair.
    return None, trace
