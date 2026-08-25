"""Diomedes cycle 005 Arm B — hand-checkable rows, emitted at full precision.

Charter S20.4 requires rows a human can verify without running the code. The runner's
first emission rounded features and weights to 6 dp, which is fine for the T4 chart but
NOT for the raw chart, where features reach magnitude ~3200: a weight rounded at 1e-6
times a feature of 3216 leaves ~3e-3 of slack, so the arithmetic did not close and the
rows were not in fact hand-checkable.

This re-emits the SAME rows at 17 significant digits (exact float64 round-trip) and asserts
the recomputation closes to a RELATIVE 1e-12. The first attempt used an ABSOLUTE 1e-9, which
is the wrong unit: on a raw-chart score of magnitude ~3200 that demands 6e-13 relative, more
than 12 digits can deliver. Wrong unit on a tolerance, same family of mistake as a per-row SE
on a per-cell decision. Nothing measured changes: the identity check below requires the per-state AUCs to
equal the ones the runner already wrote, so this is proved to be the same selection and
the same arithmetic, only printed with enough digits to be checked.

    python roles/Diomedes/cycle005_armB_handcheck.py
"""
import json
import pathlib
import random

import numpy as np

import cycle001_run as R
import cycle002_run as C2
import cycle005_armB_run as AB
from harvest_cache import load_verified, digest as pop_digest

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "cycle005_armB_handcheck_rows.json"
PRIOR = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None


def main():
    bundle = load_verified()
    assert pop_digest(bundle) == AB.POP_DIGEST
    values, parents, osee, obrk, ocel, orel = bundle
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)

    seed = AB.SEEDS[0]
    states = AB.states_aug(values, parents, osee, obrk, ocel, orel,
                           inv_cat, by_cat, sortedvals, random.Random(seed))
    cell = {}
    for s in states:
        cell.setdefault((s["key"], s["rel"]), []).append(s)
    pairs = {}
    for (k, rel), ss in cell.items():
        if len(ss) >= AB.MIN_CELL:
            pairs.setdefault(k, set()).add(rel)
    mixed = sorted([k for k, rs in pairs.items() if len(rs) >= 2])
    rels = sorted(R.RELATIONS)
    cells = [(k, r) for k in mixed for r in rels if len(cell.get((k, r), [])) >= AB.MIN_CELL]

    j0 = cells[0]
    i0 = next(i for i in cells if i[0] != j0[0] and i[1] == j0[1])

    def train_pack(c):
        ss = cell[c]
        tri, _ = AB.split_idx(seed, c, len(ss))
        return AB.pack([ss[t] for t in tri])

    TRi = train_pack(i0)
    m0 = AB.fit(AB.chart(TRi, "T0", i0[1]), TRi["y"])
    m4 = AB.fit(AB.chart(TRi, "T4", i0[1]), TRi["y"])

    ss = cell[j0]
    _, evi = AB.split_idx(seed, j0, len(ss))
    s = ss[evi[0]]
    P = AB.pack([s])
    X0, X4 = AB.chart(P, "T0", j0[1]), AB.chart(P, "T4", j0[1])
    sc0, sc4 = X0 @ m0["v"], X4 @ m4["v"]
    lab = np.array(s["labels"], dtype=float)
    seg = np.array([len(s["labels"])], dtype=np.int64)
    a0 = float(AB.batched_auc(lab, sc0, seg)[0])
    a4 = float(AB.batched_auc(lab, sc4, seg)[0])

    # ---- identity check: this must be the very same selection the runner emitted ----
    if PRIOR and "auc_this_state_T0" in PRIOR:
        assert abs(a0 - PRIOR["auc_this_state_T0"]) < 1e-12, "different state selected"
        assert abs(a4 - PRIOR["auc_this_state_T4"]) < 1e-12, "different state selected"
        assert PRIOR["source_cell_i"] == AB.cellname(i0)
        assert PRIOR["target_cell_j"] == AB.cellname(j0)

    r0 = np.argsort(np.argsort(-sc0)) + 1
    r4 = np.argsort(np.argsort(-sc4)) + 1

    def g(x):
        # 17 significant digits = exact float64 round-trip, so the printed values ARE the
        # values used. The residual below is then only float summation order.
        return float(f"{x:.17g}")

    rows, worst0, worst4 = [], 0.0, 0.0
    for t in range(min(20, len(s["labels"]))):
        f0 = {n: g(X0[t, AB.IX[n]]) for n in AB.FEATS}
        f4 = {n: g(X4[t, AB.IX[n]]) for n in AB.FEATS}
        w0 = {n: g(m0["v"][AB.IX[n]]) for n in AB.FEATS}
        w4 = {n: g(m4["v"][AB.IX[n]]) for n in AB.FEATS}
        chk0 = sum(f0[n] * w0[n] for n in AB.FEATS)
        chk4 = sum(f4[n] * w4[n] for n in AB.FEATS)
        worst0 = max(worst0, abs(chk0 - float(sc0[t])))
        worst4 = max(worst4, abs(chk4 - float(sc4[t])))
        rows.append({"candidate": s["cands"][t], "label_broke": int(s["labels"][t]),
                     "raw_features": f0, "T4_features": f4,
                     "score_T0": g(sc0[t]), "rank_T0_desc": int(r0[t]),
                     "score_T4": g(sc4[t]), "rank_T4_desc": int(r4[t])})

    # Relative tolerance: an absolute bound is the wrong unit when raw-chart scores reach
    # magnitude ~3200 while T4-chart scores are ~1. That mis-specification is what the first
    # emission got wrong.
    mag0 = max(abs(float(x)) for x in sc0[:20]) or 1.0
    mag4 = max(abs(float(x)) for x in sc4[:20]) or 1.0
    rel0, rel4 = worst0 / mag0, worst4 / mag4
    assert rel0 < 1e-12 and rel4 < 1e-12, (
        f"rows do not close by hand: relative error T0 {rel0:.3e}, T4 {rel4:.3e}")

    out = {
        "note": "score = sum over the 18 features of feature[n] * effective_weight[n]. "
                "Rank 1 = highest score. AUC ranks candidates by score within this ONE state; "
                "label_broke=1 is the positive class. Every value is printed at 17 significant "
                "digits (exact float64 round-trip) so the multiplication closes; the emitter "
                "asserts it closes to a RELATIVE 1e-12.",
        "how_to_check": [
            "1. pick any row; multiply each raw_features value by the matching "
            "effective_weights_T0 value and sum the 18 products -> score_T0",
            "2. sort the 20 rows by score_T0 descending -> rank_T0_desc",
            "3. repeat with T4_features and effective_weights_T4 -> score_T4",
            "4. T4 replaces delta/absdelta/absdiff_target/rank_delta with quantile-ranked "
            "versions and leaves parity_match and absdiff_le3 alone (amendment D4)",
        ],
        "arithmetic_self_check": {"worst_abs_error_T0": worst0, "worst_abs_error_T4": worst4,
                                  "score_magnitude_T0": mag0, "score_magnitude_T4": mag4,
                                  "worst_relative_error_T0": rel0,
                                  "worst_relative_error_T4": rel4,
                                  "relative_tolerance": 1e-12,
                                  "note": "values printed at 17 significant digits = exact "
                                          "float64; residual is float summation order only",
                                  "pass": True},
        "source_cell_i": AB.cellname(i0), "target_cell_j": AB.cellname(j0),
        "seed": seed,
        "state_tested_invariant": s["tested"], "state_target_value": s["target"],
        "state_parent_object": s["pobj"], "state_relation": s["rel"],
        "state_companion_invariants": s["comp"],
        "n_candidates_in_state": len(s["labels"]),
        "n_rows_shown": len(rows),
        "auc_this_state_T0": a0, "auc_this_state_T4": a4,
        "effective_weights_T0": {n: g(m0["v"][AB.IX[n]]) for n in AB.FEATS},
        "effective_weights_T4": {n: g(m4["v"][AB.IX[n]]) for n in AB.FEATS},
        "rows": rows,
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"source {out['source_cell_i']} -> target {out['target_cell_j']}")
    print(f"state: tested={s['tested']} target_value={s['target']} parent={s['pobj']} "
          f"k={len(s['labels'])}")
    print(f"AUC this state: T0 {a0:.6f}  T4 {a4:.6f}")
    print(f"arithmetic closes: relative error T0 {rel0:.3e}, T4 {rel4:.3e} (tol 1e-12)")
    print("->", OUT)


if __name__ == "__main__":
    main()
