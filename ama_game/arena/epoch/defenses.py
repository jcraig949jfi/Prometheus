#!/usr/bin/env python3
"""Executable defenses, and the honest measurement of what they actually catch.

A defense here is a program over a derivation's step checks. It is deliberately
NOT the argument oracle: it does not evaluate predicates over a domain, it
inspects structure. That is what makes a defense cheaper than verification and
therefore worth having.

Two rules the rulebook insists on, both enforced mechanically:

  * a defense's DECLARED coverage is not believed. `measure_coverage` runs it
    over generated items with known planted families and reports what it really
    catches, plus what valid reasoning it wrongly flags.
  * promotion requires catching an attack the defense was not designed against,
    drawn from a pool frozen before the defense existed (`PROMOTION_POOL`,
    holdout families M9-M12).

## The fingerprint hazard

The mutation operators rewrite a step's prose as well as its check. A "defense"
that greps that prose would score perfectly while detecting nothing
mathematical — the mirror image of the rulebook's kill condition about attacks
exploiting model fingerprints.

So structural defenses here are forbidden from reading `text`, and
`TEXT_FINGERPRINT` exists only as a measured upper bound: it is what a cheating
defense would score. If a structural defense ever approaches it, check why.
"""

from __future__ import annotations

import re
from typing import Callable

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "generator"))
from exprlang import evaluate  # noqa: E402

# --------------------------------------------------------------------------
# structural detectors: they see `check` dicts only, never `text`
# --------------------------------------------------------------------------


def d_out_of_domain_instantiation(steps: list[dict]) -> list[str]:
    """A universal instantiated at a point outside its own declared domain."""
    out = []
    for s in steps:
        c = s["check"]
        if c["kind"] == "instantiation" and not (c["lo"] <= c["point"] <= c["hi"]):
            out.append(s["id"])
    return out


def d_unjustified_generalization(steps: list[dict]) -> list[str]:
    """A conclusion asserted past the range any step established.

    This is CANARY-001's family. `justified` must name a step in the same
    derivation whose check establishes a step relation; a bounded sweep does not.
    """
    kinds = {s["id"]: s["check"]["kind"] for s in steps}
    inductive = {"forall_identity", "congruence"}
    out = []
    for s in steps:
        c = s["check"]
        if c["kind"] != "generalization":
            continue
        if c["asserted_hi"] <= c["established_hi"]:
            continue
        by = c.get("justified_by")
        if not (c.get("justified") and by in kinds and kinds[by] in inductive):
            out.append(s["id"])
    return out


def d_case_cover_arity(steps: list[dict]) -> list[str]:
    """A residue case split with fewer branches than its own modulus.

    `n % 5 == 0` .. `n % 5 == 3` is four cases for a modulus of five. Purely
    structural: no point in the range is ever evaluated.
    """
    out = []
    for s in steps:
        c = s["check"]
        if c["kind"] != "case_cover":
            continue
        mods = set()
        for case in c["cases"]:
            m = re.search(r"%\s*(\d+)\s*==", case)
            if m:
                mods.add(int(m.group(1)))
        if len(mods) == 1:
            m = mods.pop()
            if len(c["cases"]) < m:
                out.append(s["id"])
    return out


def d_range_start_outlier(steps: list[dict]) -> list[str]:
    """A ranged step starting below every other ranged step of its kind.

    Domain widening moves one step's lower bound down while its siblings keep
    theirs. Structural, and deliberately weak — it is here to have a defense
    that overfits, so the promotion test has something to reject.
    """
    ranged = [s for s in steps
              if s["check"]["kind"] in ("forall_inequality", "forall_identity",
                                        "congruence", "forall_implication")
              and "lo" in s["check"]]
    if len(ranged) < 3:
        return []
    los = sorted(s["check"]["lo"] for s in ranged)
    if los[0] == los[1]:
        return []
    return [s["id"] for s in ranged if s["check"]["lo"] == los[0]]


def d_instantiation_spotcheck(steps: list[dict]) -> list[str]:
    """Evaluate every instantiation at its own point. One evaluation per step.

    Not structural — it evaluates — but the cost is the number of instantiation
    steps, against O(domain x steps) for full verification. That gap is what a
    defense is for. Mechanism: a point assertion that does not hold at its point.
    """
    out = []
    for s in steps:
        c = s["check"]
        if c["kind"] != "instantiation":
            continue
        if not (c["lo"] <= c["point"] <= c["hi"]):
            out.append(s["id"])
            continue
        try:
            if not evaluate(c["pred"], {c.get("var", "n"): c["point"]}):
                out.append(s["id"])
        except Exception:
            out.append(s["id"])
    return out


def d_endpoint_spotcheck(steps: list[dict]) -> list[str]:
    """Evaluate every ranged step at its endpoints only: lo, lo+1, hi.

    Three evaluations per step rather than the whole range. Mechanism: a range
    assertion that fails at the boundary it was just extended to.
    """
    out = []
    for s in steps:
        c = s["check"]
        if c["kind"] not in ("forall_identity", "forall_inequality",
                             "forall_implication", "congruence"):
            continue
        var = c.get("var", "n")
        for v in {c["lo"], c["lo"] + 1, c["hi"]}:
            if not (c["lo"] <= v <= c["hi"]):
                continue
            try:
                b = {var: v}
                if c["kind"] == "forall_identity":
                    ok = evaluate(c["lhs"], b) == evaluate(c["rhs"], b)
                elif c["kind"] == "forall_inequality":
                    lhs, rhs = evaluate(c["lhs"], b), evaluate(c["rhs"], b)
                    op = c.get("op", "<=")
                    ok = {"<=": lhs <= rhs, "<": lhs < rhs,
                          ">=": lhs >= rhs, ">": lhs > rhs}[op]
                elif c["kind"] == "forall_implication":
                    ok = (not evaluate(c["ante"], b)) or bool(evaluate(c["cons"], b))
                else:
                    ok = (evaluate(c["lhs"], b) - evaluate(c["rhs"], b)) % int(c["modulus"]) == 0
            except Exception:
                ok = False
            if not ok:
                out.append(s["id"])
                break
    return out


STRUCTURAL: dict[str, Callable[[list[dict]], list[str]]] = {
    "D_instantiation_spotcheck": d_instantiation_spotcheck,
    "D_endpoint_spotcheck": d_endpoint_spotcheck,
    "D_out_of_domain_instantiation": d_out_of_domain_instantiation,
    "D_unjustified_generalization": d_unjustified_generalization,
    "D_case_cover_arity": d_case_cover_arity,
    "D_range_start_outlier": d_range_start_outlier,
}

# what each defense's author CLAIMS it catches. Never believed; measured.
DECLARED = {
    "D_instantiation_spotcheck": ["M8_off_by_one_boundary"],
    "D_endpoint_spotcheck": ["M4_domain_widening"],
    "D_out_of_domain_instantiation": ["M10_vacuous_instantiation"],
    "D_unjustified_generalization": ["bounded_search_as_proof"],
    "D_case_cover_arity": ["M6_case_cover_gap"],
    "D_range_start_outlier": ["M4_domain_widening"],
}


def text_fingerprint(steps: list[dict]) -> list[str]:
    """NOT a defense. The score a prose-matching cheat would get.

    Every mutation operator appends a tell to the step it rewrites. Measuring
    this bounds how much of any real defense's success could be string matching.
    """
    tells = ["CONVERSE:", "Cancelling the factor", "the same estimate is taken",
             "treats only", "expanding by", "carried over to modulo",
             "holds modulo each factor", "lies outside the stated range",
             "is anchored by checking", "by transitivity", "satisfies n^2 >"]
    return [s["id"] for s in steps
            if any(t in s.get("text", "") for t in tells)]


# --------------------------------------------------------------------------


def measure_coverage(defense_id: str, items: list[dict]) -> dict:
    """Run a defense over items whose planted family is known.

    `items` are dicts of {steps, planted_family, target_step, sealed_class}.
    Returns true positives per family and the false-positive rate on clean
    reasoning — the negative regression examples the rulebook requires.
    """
    fn = STRUCTURAL[defense_id]
    caught: dict[str, int] = {}
    seen: dict[str, int] = {}
    false_pos = 0
    clean = 0
    for it in items:
        flagged = fn(it["steps"])
        fam = it["planted_family"]
        if fam:
            seen[fam] = seen.get(fam, 0) + 1
            if it["target_step"] in flagged:
                caught[fam] = caught.get(fam, 0) + 1
        elif it["sealed_class"] == "TRUE_VALID_ARGUMENT":
            clean += 1
            if flagged:
                false_pos += 1
    return {
        "defense": defense_id,
        "declared": DECLARED[defense_id],
        "caught_by_family": caught,
        "seen_by_family": seen,
        "false_positive_rate": (false_pos / clean) if clean else None,
        "clean_items_tested": clean,
    }


def promotion_test(defense_id: str, designed_against: set[str],
                   holdout_items: list[dict]) -> dict:
    """Promote only on an attack the defense was not built for.

    Catching the exploit that inspired a defense is a fit statistic. The pool
    here is sealed and frozen before the defense was written, so independence is
    a property of the protocol rather than something the auditor asserts.
    """
    fn = STRUCTURAL[defense_id]
    independent_hits, fp, clean = [], 0, 0
    for it in holdout_items:
        flagged = fn(it["steps"])
        fam = it["planted_family"]
        if fam and fam not in designed_against and it["target_step"] in flagged:
            independent_hits.append((it["claim_id"], fam))
        if it["sealed_class"] == "TRUE_VALID_ARGUMENT":
            clean += 1
            if flagged:
                fp += 1
    promoted = bool(independent_hits) and fp == 0
    return {
        "defense": defense_id,
        "designed_against": sorted(designed_against),
        "independent_hits": independent_hits,
        "false_positives_on_clean": fp,
        "clean_tested": clean,
        "promoted": promoted,
        "reason": ("caught an attack it was not designed against, and flagged "
                   "nothing clean" if promoted else
                   "flagged valid reasoning" if fp else
                   "caught only what it was designed for"),
    }
