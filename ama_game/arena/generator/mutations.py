#!/usr/bin/env python3
"""Proof-step mutation operators.

A mutation takes a derivation whose every step passes its check and rewrites
exactly ONE step so that the step becomes locally invalid, while leaving the
proposition untouched. That the conclusion stays true is structural, not
verified after the fact: mutations edit `steps` only and never touch the
statement, so the truth oracle cannot notice a mutation has happened.

Every mutation rewrites the step's prose alongside its machine check. A mutation
that changed only the check would be invisible to a player, who never sees the
checks — the planted defect has to be readable in the argument.

Families M1-M8 are the play pool. M9-M12 are HOLDOUT: they must not appear in
any item a player sees during play, and they are the pool from which defense
promotion tests are drawn. See PREREG_A0.md and MUTATION_SPLIT.json.
"""

from __future__ import annotations

import copy
import random
import re
from typing import Any, Callable

from derivation import INVALID, argument_oracle

PLAY_FAMILIES = ["M1_quantifier_strengthening", "M2_illicit_cancellation",
                 "M3_invalid_converse", "M4_domain_widening",
                 "M5_non_equivalent_rewrite", "M6_case_cover_gap",
                 "M7_unjustified_independence", "M8_off_by_one_boundary"]

HOLDOUT_FAMILIES = ["M9_invalid_transitivity", "M10_vacuous_instantiation",
                    "M11_induction_base_omission", "M12_modulus_confusion"]

ALL_FAMILIES = PLAY_FAMILIES + HOLDOUT_FAMILIES


def _by_kind(steps: list[dict], kind: str) -> list[int]:
    return [i for i, s in enumerate(steps) if s["check"]["kind"] == kind]


def _by_tag(steps: list[dict], tag: str) -> list[int]:
    return [i for i, s in enumerate(steps) if s.get("tag") == tag]


def _single_defect(steps: list[dict], idx: int) -> bool:
    """The mutated step, and only it, must now be INVALID."""
    try:
        res = argument_oracle(steps)
    except Exception:
        # the rewrite pushed an expression outside its domain of definition and
        # the check crashed rather than failing; not a usable planted defect
        return False
    return res.verdict == INVALID and res.invalid_steps == [steps[idx]["id"]]


# --------------------------------------------------------------------------
# play families
# --------------------------------------------------------------------------

def m1_quantifier_strengthening(steps, rng):
    for i in rng.sample(_by_kind(steps, "exists_pred"), len(_by_kind(steps, "exists_pred")) or 0):
        out = copy.deepcopy(steps)
        c = out[i]["check"]
        out[i]["check"] = {"kind": "case_cover", "var": c.get("var", "n"),
                           "lo": c["lo"], "hi": c["hi"], "cases": [c["pred"]]}
        out[i]["text"] = out[i]["text"].replace(
            "There exists an integer n in", "Every integer n in").replace(
            "with n^2 >", "satisfies n^2 >")
        if _single_defect(out, i):
            return out, {"target": out[i]["id"],
                         "mechanism": "an existential established over the range "
                                      "was used as if it were universal"}
    return None


def m2_illicit_cancellation(steps, rng):
    for i in _by_tag(steps, "cancellable"):
        out = copy.deepcopy(steps)
        c = out[i]["check"]
        lhs = re.sub(r"^\(n-3\)\*\((.*)\)$", r"\1", c["lhs"])
        rhs = re.sub(r"^\(n-3\)\*\((.*)\)$", r"\1", c["rhs"])
        if lhs == c["lhs"] or rhs == c["rhs"]:
            continue
        out[i]["check"] = {**c, "lhs": lhs, "rhs": rhs}
        out[i]["text"] = out[i]["text"].replace(
            "Then (n-3)F(n) = (n-3)G(n)",
            "Cancelling the factor (n-3) from (n-3)F(n) = (n-3)G(n) gives F(n) = G(n)")
        if _single_defect(out, i):
            return out, {"target": out[i]["id"],
                         "mechanism": "a factor that vanishes somewhere in the "
                                      "range was cancelled from both sides"}
    return None


def m3_invalid_converse(steps, rng):
    idxs = _by_kind(steps, "forall_implication")
    rng.shuffle(idxs)
    for i in idxs:
        out = copy.deepcopy(steps)
        c = out[i]["check"]
        out[i]["check"] = {**c, "ante": c["cons"], "cons": c["ante"]}
        out[i]["text"] = out[i]["text"].replace("if ", "CONVERSE: if ", 1) + \
            " (the implication is used in the reverse direction below)"
        if _single_defect(out, i):
            return out, {"target": out[i]["id"],
                         "mechanism": "an implication was applied as its converse"}
    return None


def m4_domain_widening(steps, rng):
    idxs = [i for i in range(len(steps))
            if steps[i]["check"]["kind"] in
            ("forall_inequality", "forall_identity", "congruence",
             "forall_implication") and steps[i]["check"].get("lo", 0) > 0]
    rng.shuffle(idxs)
    for i in idxs:
        for new_lo in (steps[i]["check"]["lo"] - 1, 0):
            out = copy.deepcopy(steps)
            c = out[i]["check"]
            if new_lo >= c["lo"]:
                continue
            out[i]["check"] = {**c, "lo": new_lo}
            out[i]["text"] = re.sub(r"\b%d <= n\b" % c["lo"], f"{new_lo} <= n",
                                    out[i]["text"])
            out[i]["text"] += (f" (the same estimate is taken to hold from "
                               f"n = {new_lo} onward)")
            if _single_defect(out, i):
                return out, {"target": out[i]["id"],
                             "mechanism": f"a step valid from {c['lo']} was "
                                          f"restated from {new_lo}"}
    return None


_REWRITES: list[tuple[str, str, str]] = [
    (r"\(n\+1\)\*\*(\d+)", r"n**\1 + 1", "(n+1)^k expanded as n^k + 1"),
    (r"(\d+)\*\*\(n\+1\)", r"\1**n + 1", "b^(n+1) expanded as b^n + 1"),
    (r"(\d+)\*\*\(n\+2\)", r"\1**n + 2", "b^(n+2) expanded as b^n + 2"),
    (r"n\*\(n\+1\)//2", "n*n//2", "n(n+1)/2 replaced by n^2/2"),
    (r"\(n-3\)\*\(n\*\*2\)", "(n-3)*(2*n)", "n^2 replaced by 2n"),
    (r"n\*\*3", "n*3", "n^3 replaced by 3n"),
]


def m5_non_equivalent_rewrite(steps, rng):
    idxs = _by_kind(steps, "forall_identity") + _by_kind(steps, "congruence")
    rng.shuffle(idxs)
    for i in idxs:
        for pat, rep, desc in _REWRITES:
            for side in ("rhs", "lhs"):
                c = steps[i]["check"]
                if not re.search(pat, c[side]):
                    continue
                out = copy.deepcopy(steps)
                out[i]["check"] = {**c, side: re.sub(pat, rep, c[side], count=1)}
                out[i]["text"] += f" (expanding by {desc})"
                if _single_defect(out, i):
                    return out, {"target": out[i]["id"],
                                 "mechanism": f"non-equivalent rewrite: {desc}"}
    return None


def m6_case_cover_gap(steps, rng):
    idxs = [i for i in _by_kind(steps, "case_cover")
            if len(steps[i]["check"]["cases"]) >= 2]
    rng.shuffle(idxs)
    for i in idxs:
        c = steps[i]["check"]
        for drop in range(len(c["cases"])):
            out = copy.deepcopy(steps)
            kept = [x for j, x in enumerate(c["cases"]) if j != drop]
            out[i]["check"] = {**c, "cases": kept}
            out[i]["text"] += (f" (the analysis below treats only {len(kept)} of "
                               f"the {len(c['cases'])} cases)")
            if _single_defect(out, i):
                return out, {"target": out[i]["id"],
                             "mechanism": "a case split no longer covers its range"}
    return None


def m7_unjustified_independence(steps, rng):
    idxs = _by_kind(steps, "congruence")
    rng.shuffle(idxs)
    for i in idxs:
        c = steps[i]["check"]
        for m2 in (24, 8, 12, 16):
            if m2 == c["modulus"]:
                continue
            out = copy.deepcopy(steps)
            out[i]["check"] = {**c, "modulus": m2}
            out[i]["text"] += (f" (the congruence holds modulo each factor "
                               f"separately, so it is taken to hold modulo {m2})")
            if _single_defect(out, i):
                return out, {"target": out[i]["id"],
                             "mechanism": "congruences modulo two non-coprime "
                                          "factors combined as if independent"}
    return None


def m8_off_by_one_boundary(steps, rng):
    idxs = _by_kind(steps, "instantiation")
    rng.shuffle(idxs)
    for i in idxs:
        c = steps[i]["check"]
        for delta in (1, -1):
            pt = c["point"] + delta
            if not (c["lo"] <= pt <= c["hi"]):
                continue
            out = copy.deepcopy(steps)
            out[i]["check"] = {**c, "point": pt}
            out[i]["text"] = out[i]["text"].replace(f"n = {c['point']}", f"n = {pt}")
            if _single_defect(out, i):
                return out, {"target": out[i]["id"],
                             "mechanism": f"the base case was checked at n = {pt} "
                                          f"but is used at n = {c['point']}"}
    return None


# --------------------------------------------------------------------------
# holdout families
# --------------------------------------------------------------------------

def m9_invalid_transitivity(steps, rng):
    idxs = [i for i in range(len(steps))
            if steps[i]["check"]["kind"] in ("forall_inequality", "forall_identity")
            and steps[i]["check"].get("lo", 0) > 0]
    rng.shuffle(idxs)
    for i in idxs:
        c = steps[i]["check"]
        out = copy.deepcopy(steps)
        fused = {**c, "lo": c["lo"] - 1}
        new = {"id": "", "tag": "fused",
               "text": (f"The previous estimate holds on [{c['lo']}, {c['hi']}] and "
                        f"the boundary value n = {c['lo'] - 1} was handled "
                        "separately above, so by transitivity the estimate holds "
                        f"on the whole of [{c['lo'] - 1}, {c['hi']}]."),
               "check": fused, "depends_on": [out[i]["id"]]}
        out.insert(i + 1, new)
        for k, s in enumerate(out, start=1):
            s["id"] = f"s{k}"
        if _single_defect(out, i + 1):
            return out, {"target": out[i + 1]["id"],
                         "mechanism": "two results established on ranges that do "
                                      "not overlap were chained as if they did"}
    return None


def m10_vacuous_instantiation(steps, rng):
    idxs = _by_kind(steps, "instantiation")
    rng.shuffle(idxs)
    for i in idxs:
        c = steps[i]["check"]
        out = copy.deepcopy(steps)
        pt = c["lo"] - 1
        out[i]["check"] = {**c, "point": pt}
        out[i]["text"] = out[i]["text"].replace(f"n = {c['point']}", f"n = {pt}")
        out[i]["text"] += (f" (n = {pt} lies outside the stated range but the "
                           "identity is applied there)")
        if _single_defect(out, i):
            return out, {"target": out[i]["id"],
                         "mechanism": "a universal statement was instantiated "
                                      "outside its declared domain"}
    return None


def m11_induction_base_omission(steps, rng):
    idxs = _by_tag(steps, "base") + _by_tag(steps, "base2")
    rng.shuffle(idxs)
    for i in idxs:
        if steps[i]["check"]["kind"] != "instantiation":
            continue
        c = steps[i]["check"]
        for pt in (c["point"] + 2, c["point"] + 3):
            if not (c["lo"] <= pt <= c["hi"]):
                continue
            out = copy.deepcopy(steps)
            out[i]["check"] = {**c, "point": pt}
            out[i]["text"] = (f"The induction is anchored by checking the case "
                              f"n = {pt}, from which the remaining cases follow.")
            if _single_defect(out, i):
                return out, {"target": out[i]["id"],
                             "mechanism": "the induction is anchored at a point "
                                          "that does not establish its base case"}
    return None


def m12_modulus_confusion(steps, rng):
    idxs = _by_kind(steps, "congruence")
    rng.shuffle(idxs)
    for i in idxs:
        c = steps[i]["check"]
        for m2 in (4, 9, 10, 14, 15):
            if m2 == c["modulus"]:
                continue
            out = copy.deepcopy(steps)
            out[i]["check"] = {**c, "modulus": m2}
            out[i]["text"] = re.sub(r"modulo \d+", f"modulo {m2}", out[i]["text"])
            out[i]["text"] += (f" (the congruence established modulo "
                               f"{c['modulus']} is carried over to modulo {m2})")
            if _single_defect(out, i):
                return out, {"target": out[i]["id"],
                             "mechanism": f"a congruence proved modulo "
                                          f"{c['modulus']} was reused modulo {m2}"}
    return None


OPERATORS: dict[str, Callable[[list[dict], random.Random], Any]] = {
    "M1_quantifier_strengthening": m1_quantifier_strengthening,
    "M2_illicit_cancellation": m2_illicit_cancellation,
    "M3_invalid_converse": m3_invalid_converse,
    "M4_domain_widening": m4_domain_widening,
    "M5_non_equivalent_rewrite": m5_non_equivalent_rewrite,
    "M6_case_cover_gap": m6_case_cover_gap,
    "M7_unjustified_independence": m7_unjustified_independence,
    "M8_off_by_one_boundary": m8_off_by_one_boundary,
    "M9_invalid_transitivity": m9_invalid_transitivity,
    "M10_vacuous_instantiation": m10_vacuous_instantiation,
    "M11_induction_base_omission": m11_induction_base_omission,
    "M12_modulus_confusion": m12_modulus_confusion,
}


def apply_mutation(family: str, steps: list[dict], rng: random.Random):
    """Return (mutated_steps, record) or None if the family does not apply."""
    got = OPERATORS[family](steps, rng)
    if got is None:
        return None
    out, rec = got
    rec["family"] = family
    return out, rec
