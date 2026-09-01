"""EXPERIMENT 1 -- TX-004: does the `bottleneck` coordinate earn its place?

    python -m techne.cartography.exp1_tx004

THE RULING IS NOT "DID PLACEMENT GO UP". Removing a constraint always raises coverage, so a
REMOVE mutation is the easy kind to pass by accident. The frozen TX-004 test, written at cycle
035 before any of these numbers existed, requires the removal to be checked for what it
DESTROYS:

    C1  placement strictly higher                                    (necessary, not sufficient)
    C2  no pair of papers in DIFFERENT 4-tuple cells collapsing into ONE 3-tuple cell while
        having different observed failure behaviour
    C3  neighbour quality not degraded
    C4  cross-field neighbour quality not degraded

Plus the crucible's added question, which is the decisive one:

    C5  can the bottleneck be PREDICTED from the retained three coordinates? If yes, it carries
        no independent information and its cost in placement buys nothing.

C5 is the strongest form of the argument. assign_bottleneck() votes over MECHANISM_BOTTLENECK
for the same mechanism set descriptors_from() reads, so the coordinate is derived by
construction -- but "derived by construction" is a claim about the code, and this measures it
against the corpus instead.

RULINGS
    RETAIN               the coordinate carries information the others do not, and removing it
                         destroys distinctions that matter
    OPTIONAL-ANNOTATION  it is predictable from the others (so not a coordinate) but is still
                         worth carrying as a derived label for reporting
    REMOVE               predictable AND its removal destroys nothing
"""
from __future__ import annotations

import collections
import json
import pathlib
import random
from typing import Optional

from . import store, taxonomy

AXES3 = ("representation_family", "selection_family", "evaluation_regime")
K_NEIGHBOURS = 5
SEED = 20260901


# ------------------------------------------------------------------ corpus and coordinates

def has_abstract(g: dict) -> bool:
    return any(s.get("scope") == "abstract" for s in (g.get("evidence_spans") or []))


def corpus() -> list:
    return [g for g in sorted(store.current("genomes").values(),
                              key=lambda x: x["research_genome_id"])
            if not g.get("duplicate_of") and has_abstract(g)]


def cell4(g: dict) -> tuple:
    d = g.get("descriptors") or {}
    return (g.get("bottleneck", "B_UNASSIGNED"),) + tuple(d.get(a, "unknown") for a in AXES3)


def cell3(g: dict) -> tuple:
    d = g.get("descriptors") or {}
    return tuple(d.get(a, "unknown") for a in AXES3)


def placed4(g: dict) -> bool:
    c = cell4(g)
    return c[0] != "B_UNASSIGNED" and all(x != "unknown" for x in c[1:])


def placed3(g: dict) -> bool:
    return all(x != "unknown" for x in cell3(g))


# ------------------------------------------------------------------------------ C1 placement

def c1_placement(pool: list) -> dict:
    p4 = sum(1 for g in pool if placed4(g))
    p3 = sum(1 for g in pool if placed3(g))
    return {"n": len(pool), "placed_4tuple": p4, "rate_4tuple": p4 / len(pool),
            "placed_3tuple": p3, "rate_3tuple": p3 / len(pool),
            "PASS": p3 > p4}


# ------------------------------------------------------- C2 distinctions erased by removal

def c2_collapses(pool: list) -> dict:
    """Which papers occupied DIFFERENT 4-tuple cells and now share a 3-tuple cell?

    A collapse only matters if the merged papers behave differently. With no observed failure
    modes recorded in this corpus (nothing populates observed_failures), the strongest
    available proxy is DIFFERENT MECHANISM SETS: two papers merged into one cell while being
    tagged with disjoint mechanisms are a distinction the archive can no longer express.
    That proxy is weaker than the frozen test asked for and is reported as such.
    """
    by3 = collections.defaultdict(list)
    for g in pool:
        if placed3(g):
            by3[cell3(g)].append(g)

    collapses = []
    for c3, members in by3.items():
        cells4 = {cell4(g) for g in members}
        if len(cells4) <= 1:
            continue
        # different 4-cells, same 3-cell: the bottleneck was the only separator
        mech = [set(g.get("claimed_mechanism") or []) for g in members]
        disjoint_pairs = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                if cell4(members[i]) != cell4(members[j]) and not (mech[i] & mech[j]):
                    disjoint_pairs.append((members[i], members[j]))
        collapses.append({
            "cell3": list(c3),
            "n_members": len(members),
            "distinct_4cells_merged": len(cells4),
            "bottlenecks_merged": sorted({cell4(g)[0] for g in members}),
            "n_pairs_with_disjoint_mechanisms": len(disjoint_pairs),
            "example_pairs": [
                {"a": (p[0].get("title") or "")[:70], "a_bottleneck": cell4(p[0])[0],
                 "a_mechanisms": sorted(p[0].get("claimed_mechanism") or []),
                 "b": (p[1].get("title") or "")[:70], "b_bottleneck": cell4(p[1])[0],
                 "b_mechanisms": sorted(p[1].get("claimed_mechanism") or [])}
                for p in disjoint_pairs[:3]],
        })
    total_bad = sum(c["n_pairs_with_disjoint_mechanisms"] for c in collapses)
    return {"cells3_merging_multiple_4cells": len(collapses),
            "total_disjoint_mechanism_pairs_merged": total_bad,
            "PASS": total_bad == 0,
            "proxy_note": ("observed_failures is empty across this corpus, so 'different "
                           "observed failure behaviour' is proxied by DISJOINT MECHANISM SETS. "
                           "Weaker than the frozen test specified; reported as such."),
            "detail": collapses}


# ------------------------------------------------ C3/C4 neighbour and cross-field quality

def _neighbours(held: dict, train: list, use3: bool, k: int = K_NEIGHBOURS) -> list:
    """Neighbours = papers sharing the most coordinates with `held`. Ties broken by id so the
    comparison between arms is deterministic."""
    hc = cell3(held) if use3 else cell4(held)
    scored = []
    for t in train:
        tc = cell3(t) if use3 else cell4(t)
        shared = sum(1 for a, b in zip(hc, tc) if a == b and a != "unknown"
                     and a != "B_UNASSIGNED")
        if shared:
            scored.append((-shared, t["research_genome_id"], t))
    scored.sort()
    return [t for _s, _i, t in scored[:k]]


def _cross_field_hit(held: dict, nbrs: list) -> bool:
    """Frozen criterion: at least one neighbour shares a mechanism tag ABSENT from held's
    title. A tag printed in both titles proves vocabulary overlap, not mechanism overlap."""
    hm = set(held.get("claimed_mechanism") or [])
    if not hm:
        return False
    title = held.get("title") or ""
    for nb in nbrs:
        for m in hm & set(nb.get("claimed_mechanism") or []):
            pats = taxonomy._COMPILED.get(m, ())
            if not any(p.search(title) for p in pats):
                return True
    return False


def c3_c4_quality(pool: list) -> dict:
    """Leave-one-out over papers placed in the arm being measured."""
    out = {}
    for label, use3 in (("four_tuple", False), ("three_tuple", True)):
        held_set = [g for g in pool if (placed3(g) if use3 else placed4(g))]
        nq = cf = 0
        for h in held_set:
            train = [t for t in pool if t["research_genome_id"] != h["research_genome_id"]]
            nbrs = _neighbours(h, train, use3)
            if nbrs:
                nq += 1
            if _cross_field_hit(h, nbrs):
                cf += 1
        n = len(held_set)
        out[label] = {"n_placed": n,
                      "had_any_neighbour": nq, "neighbour_rate": (nq / n) if n else 0.0,
                      "cross_field_hits": cf, "cross_field_rate": (cf / n) if n else 0.0}
    # Paired comparison on the papers placed under BOTH arms -- the only clean comparison.
    both = [g for g in pool if placed4(g) and placed3(g)]
    deg_nb = deg_cf = 0
    for h in both:
        train = [t for t in pool if t["research_genome_id"] != h["research_genome_id"]]
        n4, n3 = _neighbours(h, train, False), _neighbours(h, train, True)
        if bool(n4) and not bool(n3):
            deg_nb += 1
        if _cross_field_hit(h, n4) and not _cross_field_hit(h, n3):
            deg_cf += 1
    out["paired"] = {"n_comparable": len(both), "neighbour_degraded": deg_nb,
                     "cross_field_degraded": deg_cf,
                     "PASS": deg_nb == 0 and deg_cf == 0,
                     "power_note": ("with n_comparable this small, 0 degraded is consistent "
                                    "with a real degradation rate of up to roughly 3/n by the "
                                    "rule of three. Reported, not hidden.")}
    return out


# --------------------------------------------- C5 is the bottleneck predictable from the rest

def c5_predictability(pool: list, seed: int = SEED) -> dict:
    """Predict bottleneck from (rep, sel, eval) by majority vote, leave-one-out.

    Compared against two baselines: the majority class, and a random draw from the observed
    bottleneck distribution. A coordinate that a lookup table reproduces from the other three
    is not an independent observation.
    """
    rows = [g for g in pool if g.get("bottleneck") not in (None, "B_UNASSIGNED")
            and placed3(g)]
    if len(rows) < 5:
        return {"n": len(rows), "VERDICT": "INSUFFICIENT_DATA",
                "note": "fewer than 5 papers have both a bottleneck and all three axes"}
    dist = collections.Counter(g["bottleneck"] for g in rows)
    majority = dist.most_common(1)[0][0]
    rng = random.Random(seed)

    correct = maj_correct = rnd_correct = abstain = 0
    for i, h in enumerate(rows):
        train = rows[:i] + rows[i + 1:]
        table = collections.defaultdict(collections.Counter)
        for t in train:
            table[cell3(t)][t["bottleneck"]] += 1
        votes = table.get(cell3(h))
        if votes:
            pred = votes.most_common(1)[0][0]
            correct += (pred == h["bottleneck"])
        else:
            abstain += 1
        maj_correct += (majority == h["bottleneck"])
        pool_b = [t["bottleneck"] for t in train]
        rnd_correct += (rng.choice(pool_b) == h["bottleneck"])

    n = len(rows)
    acc = correct / n
    cov = (n - abstain) / n
    acc_when_answers = (correct / (n - abstain)) if (n - abstain) else 0.0
    maj = maj_correct / n
    rnd = rnd_correct / n
    return {"n": n, "distribution": dict(dist),
            "lookup_accuracy_overall": acc,
            "lookup_coverage": cov,
            "lookup_accuracy_when_it_answers": acc_when_answers,
            "majority_class_baseline": maj,
            "random_draw_baseline": rnd,
            "beats_majority": acc > maj,
            "PREDICTABLE": acc_when_answers >= 0.9 and cov >= 0.8,
            "note": ("PREDICTABLE means a lookup table over the other three coordinates "
                     "reproduces the bottleneck on >=90% of the cases it can answer, while "
                     "answering >=80% of them. That is the operational form of 'carries no "
                     "independent information'.")}


# ------------------------------------------------------------------------------------ ruling

def run() -> dict:
    pool = corpus()
    c1 = c1_placement(pool)
    c2 = c2_collapses(pool)
    q = c3_c4_quality(pool)
    c5 = c5_predictability(pool)

    c3_pass = q["paired"]["neighbour_degraded"] == 0
    c4_pass = q["paired"]["cross_field_degraded"] == 0

    # ---- POWER GATE, checked BEFORE any ruling ----------------------------------------
    #
    # Added after the first run of this harness emitted REMOVE on n=11. Every clause rests on
    # the papers the 4-tuple can place, and at n=11 the C5 comparison was 4 correct against a
    # 6-correct majority baseline -- Wilson intervals [0.15,0.65] and [0.28,0.79], overlapping
    # almost entirely. Two papers cannot separate "carries no information" from "carries
    # information". A harness that returns a confident ruling from that is the LIM-003 error
    # class (a gate that cannot fire) inverted: a gate that fires regardless.
    n_paired = q["paired"]["n_comparable"]
    n_c5 = c5.get("n", 0)
    MIN_FOR_RULING = 30
    if min(n_paired, n_c5) < MIN_FOR_RULING:
        return {"experiment": "EXP1_TX004", "seed": SEED, "n_pool": len(pool),
                "C1_placement": c1, "C2_distinctions_erased": c2,
                "C3_C4_quality": q, "C5_predictability": c5,
                "RULING": "NOT_ADJUDICABLE",
                "rationale": (
                    "insufficient placed papers. C3/C4 rest on n_comparable=" + str(n_paired)
                    + " and C5 on n=" + str(n_c5) + ", against a minimum of "
                    + str(MIN_FOR_RULING) + ". By the rule of three, 0 degraded out of "
                    + str(n_paired) + " is consistent with a true degradation rate up to "
                    + "{:.0f}%".format(100 * 3 / max(1, n_paired)) + ", and the C5 accuracy "
                    "interval overlaps its own majority baseline. No clause can be resolved."),
                "power_gate": {"n_paired": n_paired, "n_c5": n_c5,
                               "minimum_required": MIN_FOR_RULING,
                               "binding_constraint": "the 4-tuple places only "
                                                     + str(c1["placed_4tuple"]) + " of "
                                                     + str(c1["n"]) + " papers"}}

    if not c1["PASS"]:
        ruling = "RETAIN"
        why = "removal did not raise placement, so it buys nothing at any cost"
    elif not c2["PASS"]:
        ruling = "RETAIN"
        why = ("removal merges papers with disjoint mechanism sets into one cell -- the "
               "coordinate was separating experiments the archive can no longer tell apart")
    elif not (c3_pass and c4_pass):
        ruling = "RETAIN"
        why = "removal degrades neighbour or cross-field quality on the paired comparison"
    elif c5["PREDICTABLE"]:
        ruling = "OPTIONAL-ANNOTATION"
        why = ("removal is safe on every destruction check AND the bottleneck is reproducible "
               "from the retained three, so it is a derived label rather than a coordinate. "
               "Keep it on the record for reporting; stop letting a paper fail to occupy a "
               "cell because of it")
    else:
        ruling = "REMOVE"
        why = ("removal destroys nothing measurable and the coordinate is NOT reproducible "
               "from the others -- it was carrying noise, not information")

    return {"experiment": "EXP1_TX004", "seed": SEED, "n_pool": len(pool),
            "C1_placement": c1, "C2_distinctions_erased": c2,
            "C3_C4_quality": q, "C5_predictability": c5,
            "RULING": ruling, "rationale": why}


def main() -> int:
    r = run()
    c1, c2, q, c5 = r["C1_placement"], r["C2_distinctions_erased"], r["C3_C4_quality"], r["C5_predictability"]
    print("EXPERIMENT 1 -- TX-004  (n_pool=%d)" % r["n_pool"])
    print("\nC1 PLACEMENT")
    print("  4-tuple %d/%d = %.1f%%   3-tuple %d/%d = %.1f%%   PASS=%s" % (
        c1["placed_4tuple"], c1["n"], 100 * c1["rate_4tuple"],
        c1["placed_3tuple"], c1["n"], 100 * c1["rate_3tuple"], c1["PASS"]))
    print("\nC2 DISTINCTIONS ERASED")
    print("  3-cells merging multiple 4-cells: %d" % c2["cells3_merging_multiple_4cells"])
    print("  merged pairs with DISJOINT mechanisms: %d   PASS=%s" % (
        c2["total_disjoint_mechanism_pairs_merged"], c2["PASS"]))
    for d in c2["detail"][:3]:
        print("   cell3 %s  merges %d 4-cells %s" % (d["cell3"], d["distinct_4cells_merged"],
                                                     d["bottlenecks_merged"]))
        for ex in d["example_pairs"][:1]:
            print("      A[%s] %s" % (ex["a_bottleneck"], ex["a"][:56]))
            print("      B[%s] %s" % (ex["b_bottleneck"], ex["b"][:56]))
    print("\nC3/C4 QUALITY")
    for k in ("four_tuple", "three_tuple"):
        v = q[k]
        print("  %-12s placed %3d  neighbour %.2f  cross-field %.2f" % (
            k, v["n_placed"], v["neighbour_rate"], v["cross_field_rate"]))
    p = q["paired"]
    print("  paired n=%d  neighbour_degraded=%d  cross_field_degraded=%d" % (
        p["n_comparable"], p["neighbour_degraded"], p["cross_field_degraded"]))
    print("\nC5 PREDICTABILITY OF THE BOTTLENECK FROM THE OTHER THREE")
    print("  n=%d  lookup acc %.2f (coverage %.2f, acc-when-answering %.2f)" % (
        c5.get("n", 0), c5.get("lookup_accuracy_overall", 0), c5.get("lookup_coverage", 0),
        c5.get("lookup_accuracy_when_it_answers", 0)))
    print("  majority baseline %.2f | random baseline %.2f | PREDICTABLE=%s" % (
        c5.get("majority_class_baseline", 0), c5.get("random_draw_baseline", 0),
        c5.get("PREDICTABLE")))
    print("\nRULING: %s" % r["RULING"])
    print("  %s" % r["rationale"])
    out = pathlib.Path("techne/cartography/exp1_tx004_results.json")
    out.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
    print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
