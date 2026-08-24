"""Diomedes cycle 004 — RUNNER: the relation-type confound, as a 2x2.

Executes exactly the design frozen in CYCLE_004_PREREG_relation_type_confound.md.
Same frozen feature family / scorer / seeds / identity-proved cache as cycles 002-003;
only the train/eval cell assignment changes.

    python roles/Diomedes/cycle004_run.py
"""
import collections
import json
import math
import pathlib
import random

import numpy as np

import cycle001_run as R
import cycle002_run as C2
import cycle003_run as C3
from harvest_cache import load_verified

OUT = pathlib.Path(__file__).resolve().parent / "cycle004_result.json"
SEEDS = C2.SEEDS
MIN_CELL = 150          # frozen: min states per (pair, relation) to be usable


def main():
    values, parents, osee, obrk, ocel, orel = load_verified()
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    FEATS, CARRY = [], ["B1_break_rate", "B2_freq", "n_cells", "n_rels"]
    for i in range(C2.N_COMPANIONS):
        FEATS += [f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}",
                  f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"]

    per_seed = []
    for seed in SEEDS:
        rng = random.Random(seed)
        states = C3.C2_states(values, parents, osee, obrk, ocel, orel,
                              inv_cat, by_cat, sortedvals, rng, FEATS, CARRY)
        cell = collections.defaultdict(list)
        for s in states:
            cell[(s["key"], s["rel"])].append(s)

        # mixed pairs with >= MIN_CELL states in EACH relation type
        pairs = collections.defaultdict(set)
        for (k, rel), ss in cell.items():
            if len(ss) >= MIN_CELL:
                pairs[k].add(rel)
        mixed = sorted([k for k, rs in pairs.items() if len(rs) >= 2])
        if len(mixed) < 4:
            continue
        rels = sorted(R.RELATIONS)

        arms = collections.defaultdict(list)
        b1 = collections.defaultdict(list)
        train_n = collections.defaultdict(list)
        coef_by_pair_rel = {}

        for k in mixed:
            for rel in rels:
                ss = cell[(k, rel)]
                if len(ss) < MIN_CELL:
                    continue
                idx = list(range(len(ss))); rng.shuffle(idx)
                c = max(1, int(0.6 * len(idx)))
                tr = [ss[i] for i in idx[:c]]
                he = [ss[i] for i in idx[c:]] or tr   # held-out, same pair same rel
                train_n[(k, rel)] = len(tr)

                a, cf = C3.fit_eval(tr, he, FEATS, rng)
                if a:
                    arms["A_same_pair_same_rel"] += a
                    coef_by_pair_rel[(k, rel)] = cf
                    for s in he:
                        v = R.auc(s["labels"], [f["B1_break_rate"] for f in s["F"]])
                        if v is not None:
                            b1["A"].append(v)

                # B: same pair, other relation
                other = [r for r in rels if r != rel]
                for orl in other:
                    tgt = cell.get((k, orl), [])
                    if len(tgt) >= MIN_CELL:
                        a2, _ = C3.fit_eval(tr, tgt, FEATS, rng)
                        if a2:
                            arms["B_same_pair_diff_rel"] += a2
                            for s in tgt:
                                v = R.auc(s["labels"], [f["B1_break_rate"] for f in s["F"]])
                                if v is not None:
                                    b1["B"].append(v)

                # C: different pair, same relation
                others = [k2 for k2 in mixed if k2 != k and len(cell.get((k2, rel), [])) >= MIN_CELL]
                if others:
                    k2 = rng.choice(others)
                    a3, _ = C3.fit_eval(tr, cell[(k2, rel)], FEATS, rng)
                    if a3:
                        arms["C_diff_pair_same_rel"] += a3
                        for s in cell[(k2, rel)]:
                            v = R.auc(s["labels"], [f["B1_break_rate"] for f in s["F"]])
                            if v is not None:
                                b1["C"].append(v)

                # D: different pair, different relation
                for orl in other:
                    others2 = [k2 for k2 in mixed
                               if k2 != k and len(cell.get((k2, orl), [])) >= MIN_CELL]
                    if others2:
                        k2 = rng.choice(others2)
                        a4, _ = C3.fit_eval(tr, cell[(k2, orl)], FEATS, rng)
                        if a4:
                            arms["D_diff_pair_diff_rel"] += a4

        # standing controls on the A held-out material
        allA = [s for k in mixed for rel in rels for s in cell.get((k, rel), [])]
        orc, shf, rnd = [], [], []
        for s in rng.sample(allA, min(3000, len(allA))):
            orc.append(R.auc(s["labels"], s["oracle"]))
            rnd.append(R.auc(s["labels"], [rng.random() for _ in s["labels"]]))
            shf.append(R.auc(rng.sample(s["labels"], len(s["labels"])),
                             [f["B1_break_rate"] for f in s["F"]]))

        # cosine two ways
        def cos_over(groups):
            out = []
            for g in groups:
                ks = [x for x in g if x in coef_by_pair_rel]
                for i in range(len(ks)):
                    for j in range(i + 1, len(ks)):
                        a, b = coef_by_pair_rel[ks[i]], coef_by_pair_rel[ks[j]]
                        na, nb = np.linalg.norm(a), np.linalg.norm(b)
                        if na > 1e-9 and nb > 1e-9:
                            out.append(float(a @ b / (na * nb)))
            return round(float(np.mean(out)), 4) if out else None, len(out)

        cos_within_rel, n1 = cos_over([[(k, r) for k in mixed] for r in rels])
        cos_within_pair, n2 = cos_over([[(k, r) for r in rels] for k in mixed])

        row = {"seed": seed, "n_mixed_pairs": len(mixed),
               "median_train_states_per_cell": int(np.median(list(train_n.values()))) if train_n else 0,
               "cos_within_relation_across_pairs": cos_within_rel, "n_cos_within_rel": n1,
               "cos_within_pair_across_relations": cos_within_pair, "n_cos_within_pair": n2,
               "arms": {a: C3.stat(v) for a, v in arms.items()},
               "b1_control": {a: C3.stat(v) for a, v in b1.items()},
               "controls": {"ORACLE": C3.stat(orc), "SHUFFLE_cheat": C3.stat(shf),
                            "RANDOM": C3.stat(rnd)}}
        per_seed.append(row)

    def agg(tag):
        v = [r["arms"][tag]["mean_auc"] for r in per_seed if r["arms"].get(tag)]
        return round(float(np.mean(v)), 4) if v else None

    A, B, C, D = (agg("A_same_pair_same_rel"), agg("B_same_pair_diff_rel"),
                  agg("C_diff_pair_same_rel"), agg("D_diff_pair_diff_rel"))
    gap = round(A - D, 4) if (A is not None and D is not None) else None
    recB = round((B - D) / gap, 4) if (gap and B is not None) else None
    recC = round((C - D) / gap, 4) if (gap and C is not None) else None

    if recB is None or recC is None:
        band = "NO_DATA"
    elif recC >= 0.50 and recC > recB:
        band = "RELATION-TYPE-EXPLAINS"
    elif recB >= 0.50 and recC < 0.25:
        band = "PAIR-SPECIFICITY-REAL"
    elif recB < 0.25 and recC < 0.25:
        band = "BOTH-AXES-MATTER"
    elif recB >= 0.50 and recC >= 0.50:
        band = "NEITHER-AXIS-MATTERS"
    else:
        band = "AMBIGUOUS-NEEDS-POWER"

    rep = {"prereg": "CYCLE_004_PREREG_relation_type_confound.md", "band": band,
           "cells": {"A_same_pair_same_rel": A, "B_same_pair_diff_rel": B,
                     "C_diff_pair_same_rel": C, "D_diff_pair_diff_rel": D},
           "gap_A_minus_D": gap, "recovery_B": recB, "recovery_C": recC,
           "cycle003_anchors": {"T2": 0.6600, "T3": 0.5444},
           "per_seed": per_seed}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("BAND:", band)
    print(json.dumps({k: rep[k] for k in ("cells", "gap_A_minus_D", "recovery_B", "recovery_C")},
                     indent=1))
    if per_seed:
        p = per_seed[0]
        print("cos within relation (across pairs):", p["cos_within_relation_across_pairs"],
              "| cos within pair (across relations):", p["cos_within_pair_across_relations"])
        print("controls:", {k: v["mean_auc"] for k, v in p["controls"].items()})
        print("B1 control by cell:", {k: v["mean_auc"] for k, v in p["b1_control"].items()})
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
