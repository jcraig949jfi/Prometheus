#!/usr/bin/env python3
"""Derivation steps and the ARGUMENT-VALIDITY oracle.

This is one of the two independent oracles. It answers exactly one question:

    does the submitted argument contain a locally invalid transition?

It does NOT answer whether the proposition is true. It never calls the truth
oracle, and the truth oracle never calls it. A false claim can carry an argument
whose every step passes here only if our step-check granularity is too coarse —
which is precisely why `pilot.py` asserts that no FALSE claim has a fully VALID
argument. That assertion is a test of this module, not of the players.

Per-step verdicts:

  VALID       the step's check passed over its declared range
  INVALID     the step's check failed; a concrete failing point is recorded
  INCOMPLETE  the step asserts a range strictly wider than its dependencies
              established, without an inductive or closed-form justification.
              This is bounded-search-as-proof, mechanically detected.

Argument verdict is INVALID if any step is INVALID, else INCOMPLETE if any step
is INCOMPLETE, else VALID.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from exprlang import evaluate

# kinds that establish a step relation, and so can carry a finite
# check past its endpoint. A bounded sweep is deliberately absent.
INDUCTIVE_KINDS = {"forall_identity", "congruence"}

VALID = "VALID"
INVALID = "INVALID"
INCOMPLETE = "INCOMPLETE"


@dataclass
class StepResult:
    step_id: str
    verdict: str
    detail: str = ""
    first_failure: Any = None
    evaluations: int = 0


@dataclass
class ArgumentResult:
    verdict: str
    steps: list[StepResult] = field(default_factory=list)
    invalid_steps: list[str] = field(default_factory=list)
    incomplete_steps: list[str] = field(default_factory=list)
    evaluations: int = 0


def _points(check: dict) -> list[int]:
    lo, hi = int(check["lo"]), int(check["hi"])
    step = int(check.get("step", 1))
    return list(range(lo, hi + 1, step))


def _bind(check: dict, value: int) -> dict:
    b = {check.get("var", "n"): value}
    b.update(check.get("consts", {}))
    return b


def run_check(check: dict) -> StepResult:
    """Evaluate one step's machine check. Returns a StepResult without an id."""
    kind = check["kind"]
    evals = 0

    if kind == "subset":
        inner = (int(check["lo"]), int(check["hi"]))
        outer = (int(check["outer_lo"]), int(check["outer_hi"]))
        ok = inner[0] >= outer[0] and inner[1] <= outer[1]
        return StepResult("", VALID if ok else INVALID,
                          f"[{inner[0]},{inner[1]}] subset of [{outer[0]},{outer[1]}]",
                          None if ok else inner, 1)

    if kind == "instantiation":
        pt = int(check["point"])
        lo, hi = int(check["lo"]), int(check["hi"])
        if not (lo <= pt <= hi):
            return StepResult("", INVALID,
                              f"instantiated at {pt}, outside declared domain "
                              f"[{lo},{hi}]", pt, 1)
        val = evaluate(check["pred"], _bind(check, pt))
        return StepResult("", VALID if val else INVALID,
                          f"pred at {pt} = {val}", None if val else pt, 1)

    if kind == "exists_pred":
        for v in _points(check):
            evals += 1
            if evaluate(check["pred"], _bind(check, v)):
                return StepResult("", VALID, f"witness {v}", None, evals)
        return StepResult("", INVALID, "no witness in range", None, evals)

    if kind == "generalization":
        established_hi = int(check["established_hi"])
        asserted_hi = int(check["asserted_hi"])
        if asserted_hi <= established_hi:
            return StepResult("", VALID,
                              f"asserted to {asserted_hi}, established to "
                              f"{established_hi}", None, 1)
        # Beyond the established range, `justified` is not a claim the author
        # gets to make by fiat. It must name a step in this same derivation
        # whose check establishes a step relation (an identity or congruence
        # linking n to n+1), which is what lets a finite check extend. A
        # bounded sweep is not such a step, however far it reached.
        by = check.get("justified_by")
        kinds = check.get("_context", {})
        if check.get("justified") and by in kinds and kinds[by] in INDUCTIVE_KINDS:
            return StepResult("", VALID,
                              f"asserted to {asserted_hi} from {established_hi}, "
                              f"carried by the step relation in {by}", None, 1)
        why = ("no justifying step named" if not by else
               f"{by} is not in this derivation" if by not in kinds else
               f"{by} is a {kinds[by]}, which establishes no step relation")
        return StepResult("", INCOMPLETE,
                          f"asserts range up to {asserted_hi} from a check that "
                          f"reached only {established_hi}; {why}. Bounded search "
                          "is not a proof", asserted_hi, 1)

    # --- pointwise kinds over a range ------------------------------------
    for v in _points(check):
        evals += 1
        b = _bind(check, v)
        if kind == "forall_identity":
            ok = evaluate(check["lhs"], b) == evaluate(check["rhs"], b)
        elif kind == "forall_inequality":
            lhs, rhs = evaluate(check["lhs"], b), evaluate(check["rhs"], b)
            op = check.get("op", "<=")
            ok = {"<=": lhs <= rhs, "<": lhs < rhs,
                  ">=": lhs >= rhs, ">": lhs > rhs}[op]
        elif kind == "forall_implication":
            ok = (not evaluate(check["ante"], b)) or bool(evaluate(check["cons"], b))
        elif kind == "forall_equivalence":
            ok = bool(evaluate(check["ante"], b)) == bool(evaluate(check["cons"], b))
        elif kind == "congruence":
            m = int(check["modulus"])
            ok = (evaluate(check["lhs"], b) - evaluate(check["rhs"], b)) % m == 0
        elif kind == "case_cover":
            ok = any(bool(evaluate(p, b)) for p in check["cases"])
        else:
            raise ValueError(f"unknown check kind: {kind}")

        if not ok:
            return StepResult("", INVALID, f"fails at {check.get('var','n')}={v}",
                              v, evals)

    return StepResult("", VALID, f"holds over {evals} points", None, evals)


def argument_oracle(steps: list[dict]) -> ArgumentResult:
    """Run every step's check. Independent of the truth oracle."""
    results: list[StepResult] = []
    total = 0
    kinds = {s["id"]: s["check"]["kind"] for s in steps if s.get("check")}
    for step in steps:
        check = step.get("check")
        if check is None:
            raise ValueError(f"step {step.get('id')} has no machine check; "
                             "unchecked steps are not admissible")
        if check["kind"] == "generalization":
            check = {**check, "_context": kinds}
        r = run_check(check)
        r.step_id = step["id"]
        results.append(r)
        total += r.evaluations

    invalid = [r.step_id for r in results if r.verdict == INVALID]
    incomplete = [r.step_id for r in results if r.verdict == INCOMPLETE]
    verdict = INVALID if invalid else (INCOMPLETE if incomplete else VALID)
    return ArgumentResult(verdict, results, invalid, incomplete, total)


def public_steps(steps: list[dict]) -> list[dict]:
    """Strip everything a player must not see: the machine checks.

    The player receives prose only. Shipping the checks would hand over the
    location of the planted defect, since running them prints it.
    """
    return [{"id": s["id"], "text": s["text"],
             "depends_on": list(s.get("depends_on", []))} for s in steps]
