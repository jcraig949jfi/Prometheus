#!/usr/bin/env python
"""GEN-3G -- validity boundary, per FREEZE_3G.txt."""

import json
import sys

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260908
W = 8
K_EDITS = 128
OBJECTS_PER_SEED = 12
BALANCE_BAND = (0.05, 0.95)


def legal_refs(g):
    """Inputs always; plus the W most recent gate wires."""
    lo = max(cm.N, cm.N + g - W)
    return list(range(cm.N)) + list(range(lo, cm.N + g))


def random_windowed_circuit(rng):
    gates = []
    for g in range(24):
        refs = legal_refs(g)
        a = refs[int(rng.integers(len(refs)))]
        b = refs[int(rng.integers(len(refs)))]
        gates.append((int(rng.integers(4)), a, b))
    return gates


def slack_of(g, w):
    """Boundary slack of reference w at gate g; inputs get W."""
    if w < cm.N:
        return W
    age = (cm.N + g) - w          # 1 = most recent
    return W - age


def influences(gates, wires):
    base = wires[-1]
    infs = []
    for g in range(24):
        w2 = list(wires[:cm.N + g + 1])
        w2[cm.N + g] = ~wires[cm.N + g]
        for h in range(g + 1, 24):
            op, a, b = gates[h]
            w2.append(cm.gate_eval(op, w2[a], w2[b]))
        infs.append(float(np.count_nonzero(w2[-1] != base)) / cm.DOM)
    return infs


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main():
    rows = []
    fault_count = 0
    for seed in cm.MASTER_SEEDS:
        made = 0
        attempt = 0
        while made < OBJECTS_PER_SEED:
            attempt += 1
            rng = cm.rng_for(seed, 108, made, attempt)
            gates = random_windowed_circuit(rng)
            wires = cm.eval_wires(gates)
            f = wires[-1].copy()
            bal = float(f.mean())
            if not (BALANCE_BAND[0] <= bal <= BALANCE_BAND[1]):
                continue
            infs = influences(gates, wires)
            # full edit space incl. out-of-window rewires (faults)
            edits = []
            for gi, (op, a, b) in enumerate(gates):
                for no in range(4):
                    if no != op:
                        edits.append(("op", gi, no))
                for slot in (0, 1):
                    cur = (a, b)[slot]
                    for w in range(cm.N + gi):
                        if w != cur:
                            edits.append(("wire", gi, (slot, w)))
            rng_e = cm.rng_for(seed, 109, made)
            for k in range(K_EDITS):
                e = edits[int(rng_e.integers(len(edits)))]
                if e[0] == "wire":
                    w = e[2][1]
                    if w >= cm.N and (cm.N + e[1]) - w > W:
                        fault_count += 1     # FORCED: definitional
                        rows.append(dict(seed=seed, obj=made, kind="wire",
                                         cls="FAULT", slack=slack_of(
                                             e[1], w), inf=None))
                        continue
                f2 = cm.eval_wires(cm.apply_edit(gates, e))[-1]
                cls = cm.r_vec2(f, f2)
                sl = slack_of(e[1], e[2][1]) if e[0] == "wire" else None
                rows.append(dict(seed=seed, obj=made, kind=e[0],
                                 cls=cls, slack=sl, inf=infs[e[1]]))
            made += 1

    # class mix vs slack (valid rewires)
    valid_rw = [r for r in rows if r["kind"] == "wire"
                and r["cls"] != "FAULT"]
    nn = [r for r in valid_rw if r["cls"] != "NEUTRAL"]
    mix = {}
    for sl in range(W + 1):
        sub = [r for r in valid_rw if r["slack"] == sl]
        if sub:
            mix[sl] = {c: round(np.mean(
                [1 if r["cls"] == c else 0 for r in sub]), 3)
                for c in ("NEUTRAL", "SMALL", "LARGE", "DESTRUCTION")}

    folds_slack, folds_inf = {}, {}
    for hold in cm.MASTER_SEEDS:
        te = [r for r in nn if r["seed"] == hold]
        y = np.array([1 if r["cls"] == "SMALL" else 0 for r in te])
        s_sl = np.array([r["slack"] for r in te], float)
        s_in = np.array([r["inf"] for r in te], float)
        a1 = auc(s_sl, y)
        a2 = auc(s_in, y)
        folds_slack[hold] = round(max(a1, 1 - a1), 4)
        folds_inf[hold] = round(max(a2, 1 - a2), 4)

    hug = [1 if r["cls"] == "SMALL" else 0 for r in nn if r["slack"] == 0]
    far = [1 if r["cls"] == "SMALL" else 0 for r in nn if r["slack"] >= 4]
    rng = np.random.default_rng(STAT_SEED)
    diffs = []
    for _ in range(2000):
        h = rng.choice(hug, size=len(hug), replace=True).mean()
        fa = rng.choice(far, size=len(far), replace=True).mean()
        diffs.append(h - fa)
    ci = [round(float(np.percentile(diffs, q)), 4) for q in (2.5, 97.5)]

    support_ok = all(len([r for r in nn if r["seed"] == s]) >= 300
                     for s in cm.MASTER_SEEDS)
    if not support_ok:
        verdict = "INDETERMINATE"
    elif all(a >= 0.60 for a in folds_slack.values()):
        verdict = "BOUNDARY_ORGANIZATION"
    else:
        verdict = "NO_BOUNDARY_ORGANIZATION"

    report = dict(
        n_rows=len(rows), fault_rate=round(fault_count / len(rows), 4),
        fault_note="FORCED: definitional (out-of-window rewire)",
        class_mix_by_slack=mix,
        auc_slack_folds=folds_slack, auc_inf_folds=folds_inf,
        smallrate_hug_minus_far=dict(
            hug0=round(float(np.mean(hug)), 4), n_hug=len(hug),
            far4plus=round(float(np.mean(far)), 4), n_far=len(far),
            diff_ci95=ci),
        verdict=verdict)
    json.dump(report, open("results/analysis_3G.json", "w"), indent=1)
    print("fault_rate:", report["fault_rate"])
    print("AUC(slack):", folds_slack)
    print("AUC(inf)  :", folds_inf)
    print("SMALL rate hug0 vs far:", report["smallrate_hug_minus_far"])
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
