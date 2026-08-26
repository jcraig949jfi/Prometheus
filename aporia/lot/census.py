"""census.py — REACHABILITY_CENSUS. A reusable preflight for any synthetic task family.

Generalised from the attainable-range rule after world v1 died at a level the rule did not
cover (reviewer, 2026-08-26):

    Before interpreting any measured signal, prove that the target phenomenon is REACHABLE
    and NON-VACUOUS in the population that could generate it.

    threshold -> instrument reading -> oracle identifiability -> task-population label support

World v1 failed at the last level, and it failed before any model behaviour entered the picture.
That is the cheapest place to fail and this module exists to make failing there routine.

THREE PROGRESSIVELY STRONGER CHEAP TESTS, run before any expensive counterfeit solver:

    T1 REACHABILITY          both labels exist; the (r_a, r_b) occupancy table has healthy mass
                             in ALL FOUR cells. "Alien surface" is not enough -- cross-domain
                             transport needs a different surface AND shared REALIZABLE structure,
                             and world v1 showed the algebra of a domain can forbid the target
                             outright rather than merely make it rare.
    T2 MARGINAL LEAKAGE      P(r_i | y=0) ~= P(r_i | y=1) for EVERY primitive. No single relation
                             may carry substantial marginal label information; the target must be
                             recoverable only from the composition.
    T3 ALT-COMPOSITION LEAK  no unintended shallow pair r_j,r_k predicts the target nearly as
                             well as the intended rule.

Only a family passing all three earns the expensive gate.
"""
from __future__ import annotations

from itertools import combinations


def occupancy(data, ra, rb, relations):
    """Four-cell table over (ra, rb). The criterion is healthy mass in ALL FOUR cells."""
    fa, fb = relations[ra], relations[rb]
    cells = {"00": 0, "01": 0, "10": 0, "11": 0}
    for o in data:
        cells[f"{int(bool(fa(o)))}{int(bool(fb(o)))}"] += 1
    n = max(len(data), 1)
    return {k: {"n": v, "frac": round(v / n, 4)} for k, v in cells.items()}


def marginals(data, relations):
    """P(r_i | y=1) and P(r_i | y=0) for every primitive, plus the absolute gap.

    A large gap means the primitive alone carries label information, which is exactly what
    a composition-mandatory world must not allow.
    """
    pos = [o for o in data if o["label"] == 1]
    neg = [o for o in data if o["label"] == 0]
    out = {}
    for name, f in relations.items():
        p1 = sum(1 for o in pos if f(o)) / max(len(pos), 1)
        p0 = sum(1 for o in neg if f(o)) / max(len(neg), 1)
        out[name] = {"P_given_y1": round(p1, 4), "P_given_y0": round(p0, 4),
                     "gap": round(abs(p1 - p0), 4)}
    return out


def alt_compositions(data, relations, exclude):
    """Best unintended shallow pair, as accuracy against the label.

    `exclude` is the intended pair; every other ordered pair is tried in both the AND and the
    ANDNOT shape, which are the two shallow forms the intended rule itself uses.
    """
    best = []
    for a, b in combinations(relations, 2):
        if {a, b} == set(exclude):
            continue
        fa, fb = relations[a], relations[b]
        for shape, fn in (("AND", lambda o: fa(o) and fb(o)),
                          ("ANDNOT", lambda o: fa(o) and not fb(o)),
                          ("NOTAND", lambda o: (not fa(o)) and fb(o))):
            acc = sum(1 for o in data if int(bool(fn(o))) == o["label"]) / max(len(data), 1)
            best.append((f"{a}_{shape}_{b}", round(acc, 4)))
    best.sort(key=lambda kv: -kv[1])
    return best


def census(data, relations, target_pair, target_fn, family,
           min_cell_frac=0.05, max_marginal_gap=0.15, max_alt_acc=0.70):
    """Run T1/T2/T3. Every threshold is stated here with the input that fails it."""
    n = len(data)
    pos = sum(1 for o in data if o["label"] == 1)
    occ = occupancy(data, target_pair[0], target_pair[1], relations)
    marg = marginals(data, relations)
    alts = alt_compositions(data, relations, target_pair)
    tgt_acc = sum(1 for o in data if int(bool(target_fn(o))) == o["label"]) / max(n, 1)

    worst_marg = max(marg.items(), key=lambda kv: kv[1]["gap"])
    empty_cells = [k for k, v in occ.items() if v["frac"] < min_cell_frac]

    r = {
        "family": family, "n": n, "label_pos": pos, "label_neg": n - pos,
        "target_accuracy": round(tgt_acc, 4),
        "occupancy": occ, "empty_or_thin_cells": empty_cells,
        "marginals": marg,
        "worst_marginal": {"relation": worst_marg[0], **worst_marg[1]},
        "best_alt_composition": alts[0] if alts else None,
        "alt_top5": alts[:5],
        # FAILING INPUTS, stated:
        #   T1 fails if any of the four (r_a, r_b) cells is below min_cell_frac
        #   T2 fails if ANY primitive marginal gap exceeds max_marginal_gap
        #   T3 fails if the best unintended shallow pair exceeds max_alt_acc
        "T1_reachability": len(empty_cells) == 0,
        "T2_no_marginal_leakage": worst_marg[1]["gap"] <= max_marginal_gap,
        "T3_no_alt_composition_leak": (alts[0][1] if alts else 0.0) <= max_alt_acc,
        "thresholds": {"min_cell_frac": min_cell_frac,
                       "max_marginal_gap": max_marginal_gap,
                       "max_alt_acc": max_alt_acc},
    }
    r["PASSES"] = r["T1_reachability"] and r["T2_no_marginal_leakage"] and r["T3_no_alt_composition_leak"]
    r["verdict"] = "FAMILY_ADMISSIBLE" if r["PASSES"] else "FAMILY_REJECTED"
    return r
