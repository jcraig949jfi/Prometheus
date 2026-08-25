#!/usr/bin/env python3
"""Re-execution oracle: does a submitted witness actually break the claim?

The harness must never take a falsifier's word for it. This module rebuilds the
proposition as a point predicate from the sealed parameters and evaluates it at
the submitted point, checking two things separately:

  1. is the point inside the domain the claim quantified over?
  2. does the proposition actually fail there?

A witness that fails (1) is not a counterexample no matter what it does to (2) —
that is the single most common bogus kill, and it is what drives the
invalid-falsifier rate in PREREG_A0.md section 3.

This is truth-side machinery. It uses `exprlang` for arithmetic, as the
argument-side checks do, but it never consults a derivation step: the predicate
is rebuilt from the claim's own parameters.
"""

from __future__ import annotations

from typing import Any

from exprlang import evaluate


def witness_var(template_id: str) -> str:
    return "g" if template_id.startswith("t3") else "n"


def claim_predicate(template_id: str, params: dict) -> str:
    """An expression that is True exactly where the proposition holds."""
    p = params
    if template_id == "t1_integer_sum_identity":
        return f"sum_k(n,{p['p']}) == {p['formula_expr']}"
    if template_id == "t2_modular_power_cycle":
        return (f"pow({p['a']}, n, {p['m']}) == "
                f"pow({p['a']}, n % {p['d_claimed']}, {p['m']})")
    if template_id == "t3_min_degree_connectivity":
        return (f"(min(graph_degrees(g, {p['v']})) < {p['d']}) or "
                f"(graph_is_connected(g, {p['v']}) == 1)")
    if template_id == "t4_linear_recurrence":
        return (f"lin_rec(n, {p['a0']}, {p['a1']}, {p['p']}, {p['q']}) == "
                f"{p['C']}*{p['r']}**n + {p['D']}*{p['s']}**n")
    if template_id == "t5_collatz_stopping_time":
        return f"stop_time(n) < {p['K']}"
    if template_id == "t6_shortcut_stopping_time":
        return f"shortcut_time(n) < {p['K']}"
    raise ValueError(f"no predicate for template {template_id}")


def domain_bounds(template_id: str, params: dict) -> tuple[int, int]:
    p = params
    if template_id == "t1_integer_sum_identity":
        return 1, p["N"]
    if template_id == "t2_modular_power_cycle":
        return 0, p["N"]
    if template_id == "t3_min_degree_connectivity":
        return 0, (1 << (p["v"] * (p["v"] - 1) // 2)) - 1
    if template_id == "t4_linear_recurrence":
        return 0, p["N"]
    if template_id in ("t5_collatz_stopping_time", "t6_shortcut_stopping_time"):
        return 1, p["N"]
    raise ValueError(f"no domain for template {template_id}")


def verify_witness(sealed: dict, point: Any) -> dict:
    """Adjudicate a submitted counterexample against the claim as stated."""
    tid, params = sealed["template_id"], sealed["params"]
    lo, hi = domain_bounds(tid, params)
    var = witness_var(tid)
    try:
        pt = int(point)
    except (TypeError, ValueError):
        return {"in_domain": False, "claim_holds_at_point": None,
                "is_counterexample": False, "reason": "witness is not an integer"}
    if not (lo <= pt <= hi):
        return {"in_domain": False, "claim_holds_at_point": None,
                "is_counterexample": False,
                "reason": f"witness {pt} lies outside the quantified domain "
                          f"[{lo}, {hi}]"}
    holds = bool(evaluate(claim_predicate(tid, params), {var: pt}))
    return {"in_domain": True, "claim_holds_at_point": holds,
            "is_counterexample": not holds,
            "reason": "" if not holds else
                      f"the proposition holds at {var} = {pt}"}
