"""Diomedes cycle 005 Arm B — RUNNER: coordinate transport vs local relearning (Q2).

Executes the design frozen in CYCLE_005_PREREG_terminal.md S3 as applied by
AMENDMENT_2026-08-25b_armB_specification.md. The transport family T0-T5 is frozen and is
NOT altered here: no member is added, tuned, removed, or substituted.

Population: cycle 004's, via the identity-proved harvest cache (digest 1b4abb1a...).
Cells: (invariant_pair, relation), MIN_CELL=150, the 12 mixed pairs -> 24 cells.
Features: the frozen 18-feature family (no CARRY), identical to cycles 003-004.

DECISIVE COMPARISON is transport vs local relearning, not transport vs raw.

    recovery(T) = (transfer_T - transfer_T0) / (relearn_raw - transfer_T0)

Two runner-level specification decisions, recorded here BEFORE this script was executed
(this file is committed unrun; git ordering is the proof):

  D6 - The denominator is the RAW-CHART relearn, one value per target cell, held fixed
       across all transports. Only the numerator varies with T. Per-chart relearn is
       also reported, as a diagnostic only.
  D7 - Recovery is computed from AGGREGATE MEANS over ordered cell pairs, because a
       per-pair ratio has an unstable denominator whenever a target cell's relearn sits
       near its raw transfer. Per-target-cell recovery medians are reported as a
       robustness diagnostic and are declared non-decisive in advance.

  Also: under D4, `target` is ranked in the TESTED invariant's own distribution (it is a
  value of the tested invariant), while u and p are ranked in companion i's. "Its own
  invariant's distribution" is applied per value. This matters: the frozen feature
  absdiff_target_i compares a COMPANION value to a TESTED-invariant value, i.e. across
  two different scales, so quantile standardisation has real work to do there.

Non-LLM controls: no model in the loop. Two differential tests certify the two pieces of
new machinery against the frozen originals before either is used --
  (1) the augmented state builder must reproduce cycle 003's C2_states feature dicts
      bit-for-bit, per seed;
  (2) the batched AUC must reproduce cycle001_run.auc to 1e-12 on a sample.
Arm B remains rung 5 (fitted, sampled) as prereg S6 labels it; the assertions are rung 1.

    python roles/Diomedes/cycle005_armB_run.py
"""
import collections
import hashlib
import json
import math
import pathlib
import random

import numpy as np
from sklearn.linear_model import LogisticRegression

import cycle001_run as R
import cycle002_run as C2
import cycle003_run as C3
from harvest_cache import load_verified, digest as pop_digest

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "cycle005_armB_result.json"
ROWS_OUT = HERE / "cycle005_armB_handcheck_rows.json"

MIN_CELL = 150                       # frozen by cycle 004
SEEDS = C2.SEEDS
NC = C2.N_COMPANIONS                 # 3
CHARTS = ["T0", "T2", "T3", "T4", "T5"]          # T1 acts on the score, not the chart
POP_DIGEST = "1b4abb1a36a9cfb53d6a4bfb8c08a0623e28a88ba996556532d80e71d889af52"
HEADROOM_FLOOR = 0.05                # BOOTSTRAP S6 standing rule

FEATS = []
for _i in range(NC):
    FEATS += [f"delta_{_i}", f"absdelta_{_i}", f"parity_match_{_i}",
              f"absdiff_target_{_i}", f"absdiff_le3_{_i}", f"rank_delta_{_i}"]
IX = {n: k for k, n in enumerate(FEATS)}
# raw-unit ("difference-valued") columns, per D3
UNIT_COLS = [IX[f"{b}_{i}"] for i in range(NC) for b in ("delta", "absdelta", "absdiff_target")]


def rel_threshold(rel):
    """T2 divisor. Exactly one threshold exists in this population; equal_mod_2 has none."""
    return 3.0 if rel == "abs_diff_le_3" else 1.0


# --------------------------------------------------------------------------- AUC


def batched_auc(labels, scores, seg_lens):
    """Tie-averaged rank AUC per segment, vectorised. Same formula as cycle001_run.auc.

    Returns nan for segments with an absent class (R.auc returns None there).
    """
    n = int(seg_lens.sum())
    nseg = len(seg_lens)
    seg = np.repeat(np.arange(nseg), seg_lens)
    order = np.lexsort((scores, seg))                 # by segment, then score ascending
    s, g, lab = scores[order], seg[order], labels[order]
    starts = np.concatenate(([0], np.cumsum(seg_lens)[:-1]))
    rank = (np.arange(n) - np.repeat(starts, seg_lens)) + 1.0
    newgrp = np.ones(n, dtype=bool)
    if n > 1:
        newgrp[1:] = (s[1:] != s[:-1]) | (g[1:] != g[:-1])
    gid = np.cumsum(newgrp) - 1
    gsum = np.bincount(gid, weights=rank)
    gcnt = np.bincount(gid).astype(float)
    rank = (gsum / gcnt)[gid]                          # average rank within ties
    npos = np.bincount(g, weights=lab, minlength=nseg)
    prs = np.bincount(g, weights=rank * lab, minlength=nseg)
    nneg = seg_lens.astype(float) - npos
    out = np.full(nseg, np.nan)
    ok = (npos > 0) & (nneg > 0)
    out[ok] = (prs[ok] - npos[ok] * (npos[ok] + 1) / 2.0) / (npos[ok] * nneg[ok])
    return out


# ------------------------------------------------------------- augmented builder


def states_aug(values, parents, osee, obrk, ocel, orel, inv_cat, by_cat, sortedvals, rng):
    """Frozen cycle-002/003 state builder, PLUS the raw quantile components T4 needs.

    The feature expressions are copied verbatim from cycle003_run.C2_states. Identity with
    that function is not asserted by inspection but by differential test in main().
    """
    out = []
    for st in parents:
        tested = st["inv_a"] if st["side"] == "a" else st["inv_b"]
        cat = inv_cat.get(tested)
        if cat is None:
            continue
        pool = values.get((cat, tested), {})
        if len(pool) < 10:
            continue
        comp = [inv for _, inv in by_cat[cat] if inv != tested][:NC]
        pobj = st["obj_a"] if st["side"] == "a" else st["obj_b"]
        target = st["val_b"] if st["side"] == "a" else st["val_a"]
        names = sorted(pool)
        cands = names if len(names) <= R.K else rng.sample(names, R.K)
        # target is a value of the TESTED invariant -> ranked in the tested invariant's own list
        qt = C2.qrank(sortedvals[(cat, tested)], target)
        labels, oracle, rows, qrows = [], [], [], []
        for c in cands:
            v = pool[c]
            va, vb = (v, st["val_b"]) if st["side"] == "a" else (st["val_a"], v)
            broke = not R.relation_holds(st["rel"], va, vb)
            labels.append(1 if broke else 0)
            oracle.append(1.0 if broke else 0.0)
            f, q = {}, {}
            for i in range(NC):
                u = p = None
                if i < len(comp):
                    tbl = values[(cat, comp[i])]
                    u, p = tbl.get(c), tbl.get(pobj)
                if u is None:
                    for nm in (f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}",
                               f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"):
                        f[nm] = 0.0
                    q[f"has_{i}"] = 0.0
                    q[f"qu_{i}"] = q[f"qp_{i}"] = 0.0
                    continue
                p = u if p is None else p
                f[f"delta_{i}"] = float(u - p)
                f[f"absdelta_{i}"] = float(abs(u - p))
                f[f"parity_match_{i}"] = float(int(u - target) % 2 == 0)
                f[f"absdiff_target_{i}"] = float(abs(u - target))
                f[f"absdiff_le3_{i}"] = float(abs(u - target) <= 3)
                sv = sortedvals[(cat, comp[i])]
                qu, qp = C2.qrank(sv, u), C2.qrank(sv, p)
                f[f"rank_delta_{i}"] = qu - qp
                q[f"has_{i}"] = 1.0
                q[f"qu_{i}"], q[f"qp_{i}"] = qu, qp
            q["qt"] = qt
            rows.append(f)
            qrows.append(q)
        if 0 < sum(labels) < len(labels):
            out.append({"labels": labels, "oracle": oracle, "F": rows, "Q": qrows,
                        "key": (st["inv_a"], st["inv_b"]), "rel": st["rel"],
                        "tested": tested, "cat": cat, "comp": comp,
                        "target": target, "cands": cands, "pobj": pobj})
    return out


def pack(cell_states):
    """Flatten a cell into arrays: raw features, quantile components, labels, segments."""
    X = np.array([[f[n] for n in FEATS] for s in cell_states for f in s["F"]], dtype=float)
    qu = np.array([[q[f"qu_{i}"] for i in range(NC)] for s in cell_states for q in s["Q"]])
    qp = np.array([[q[f"qp_{i}"] for i in range(NC)] for s in cell_states for q in s["Q"]])
    hs = np.array([[q[f"has_{i}"] for i in range(NC)] for s in cell_states for q in s["Q"]])
    qt = np.array([q["qt"] for s in cell_states for q in s["Q"]])
    y = np.array([l for s in cell_states for l in s["labels"]], dtype=float)
    seg = np.array([len(s["labels"]) for s in cell_states], dtype=np.int64)
    return {"X": X, "qu": qu, "qp": qp, "has": hs, "qt": qt, "y": y, "seg": seg}


# ------------------------------------------------------------------- transports


def chart(P, T, rel):
    """Apply chart T to a packed cell, using THAT cell's own relation (two-sided, D2)."""
    X = P["X"].copy()
    if T in ("T4", "T5"):                       # quantile standardisation (D4)
        qu, qp, qt, hs = P["qu"], P["qp"], P["qt"], P["has"]
        for i in range(NC):
            m = hs[:, i] > 0
            d = np.where(m, qu[:, i] - qp[:, i], 0.0)
            X[:, IX[f"delta_{i}"]] = d
            X[:, IX[f"absdelta_{i}"]] = np.abs(d)
            X[:, IX[f"absdiff_target_{i}"]] = np.where(m, np.abs(qu[:, i] - qt), 0.0)
            X[:, IX[f"rank_delta_{i}"]] = d
            # parity_match_i and absdiff_le3_i deliberately untouched (D4)
    if T in ("T2", "T5"):                       # threshold normalisation (D3)
        X[:, UNIT_COLS] /= rel_threshold(rel)
    # T3 (modulus alignment) is identically the identity on this population: the only
    # modulus is 2, which is already the parity feature's modulus, and abs_diff_le_3 has
    # none. Asserted equal to T0 in main(), not assumed.
    return X


# ------------------------------------------------------------------------ model


def fit(X, y):
    """Return the effective weight vector v with score = Xeval @ v (monotone-equal to
    predict_proba), plus the standardiser, so evaluation is one matmul."""
    if len(set(y.tolist())) < 2 or len(X) < 50:
        return None
    mu, sd = X.mean(0), X.std(0) + 1e-9
    clf = LogisticRegression(max_iter=3000).fit((X - mu) / sd, y)
    w = clf.coef_[0]
    return {"v": w / sd, "mu": mu, "sd": sd, "w": w, "b": float(clf.intercept_[0]), "clf": clf}


def cellname(c):
    return f"{c[0][0]}|{c[0][1]}|{c[1]}"


def split_idx(seed, c, n):
    """Deterministic 60/40 split keyed by (seed, cell) — independent of iteration order."""
    h = hashlib.sha256(f"{seed}|{cellname(c)}".encode()).hexdigest()
    r = random.Random(int(h[:16], 16))
    idx = list(range(n))
    r.shuffle(idx)
    k = max(1, int(0.6 * n))
    return idx[:k], (idx[k:] or idx[:k])


# ------------------------------------------------------------------------- main


def main():
    bundle = load_verified()
    assert pop_digest(bundle) == POP_DIGEST, "population digest mismatch — refusing to run"
    values, parents, osee, obrk, ocel, orel = bundle
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    CARRY = ["B1_break_rate", "B2_freq", "n_cells", "n_rels"]

    checks = {"population_digest": POP_DIGEST, "digest_ok": True}
    per_seed, handrows = [], None

    for seed in SEEDS:
        # ---- differential test 1: augmented builder == frozen builder, bit for bit ----
        st_aug = states_aug(values, parents, osee, obrk, ocel, orel,
                            inv_cat, by_cat, sortedvals, random.Random(seed))
        st_ref = C3.C2_states(values, parents, osee, obrk, ocel, orel,
                              inv_cat, by_cat, sortedvals, random.Random(seed), FEATS, CARRY)
        assert len(st_aug) == len(st_ref), f"builder length mismatch {len(st_aug)}!={len(st_ref)}"
        nfeat = 0
        for a, b in zip(st_aug, st_ref):
            assert a["labels"] == b["labels"] and a["key"] == b["key"] and a["rel"] == b["rel"]
            for fa, fb in zip(a["F"], b["F"]):
                for n in FEATS:
                    assert fa[n] == fb[n], f"feature {n} diverged"
                    nfeat += 1
        checks[f"builder_differential_seed_{seed}"] = {
            "n_states": len(st_aug), "n_feature_values_compared": nfeat, "identical": True}

        states = st_aug
        cell = collections.defaultdict(list)
        for s in states:
            cell[(s["key"], s["rel"])].append(s)
        pairs = collections.defaultdict(set)
        for (k, rel), ss in cell.items():
            if len(ss) >= MIN_CELL:
                pairs[k].add(rel)
        mixed = sorted([k for k, rs in pairs.items() if len(rs) >= 2])
        rels = sorted(R.RELATIONS)
        cells = [(k, r) for k in mixed for r in rels if len(cell.get((k, r), [])) >= MIN_CELL]

        # ---- pack, split ----
        PK, TR, EV = {}, {}, {}
        for c in cells:
            ss = cell[c]
            tri, evi = split_idx(seed, c, len(ss))
            TR[c] = pack([ss[i] for i in tri])
            EV[c] = pack([ss[i] for i in evi])
            PK[c] = pack(ss)                       # full cell, for the reproduction check

        # ---- differential test 2: batched AUC == cycle001_run.auc ----
        if seed == SEEDS[0]:
            c0 = cells[0]
            ss = cell[c0][:60]
            rng0 = random.Random(1234)
            sc = np.array([rng0.random() for s in ss for _ in s["labels"]])
            lb = np.array([l for s in ss for l in s["labels"]], dtype=float)
            sg = np.array([len(s["labels"]) for s in ss], dtype=np.int64)
            got = batched_auc(lb, sc, sg)
            ref, o = [], 0
            for s in ss:
                n = len(s["labels"])
                ref.append(R.auc(s["labels"], sc[o:o + n].tolist()))
                o += n
            worst = max(abs(g - r) for g, r in zip(got, ref) if r is not None)
            assert worst < 1e-12, f"batched AUC diverged from cycle001_run.auc by {worst}"
            checks["auc_differential"] = {"n_segments": len(ss), "max_abs_diff": float(worst),
                                          "tolerance": 1e-12, "pass": True}

            # ---- charter S20.3 mandatory harness assertions ----
            lab = np.array([l for s in ss for l in s["labels"]], dtype=float)
            orc = np.array([o_ for s in ss for o_ in s["oracle"]])
            a_perf = np.nanmean(batched_auc(lab, orc, sg))
            a_const = np.nanmean(batched_auc(lab, np.zeros_like(orc), sg))
            a_mono = np.nanmean(batched_auc(lab, np.exp(3 * sc + 7), sg))
            a_plain = np.nanmean(batched_auc(lab, sc, sg))
            permrng = np.random.default_rng(7)
            permlab = lab.copy()
            o = 0
            for n in sg:                            # permute WITHIN each state
                permlab[o:o + n] = permrng.permutation(permlab[o:o + n])
                o += n
            a_perm = np.nanmean(batched_auc(permlab, orc, sg))
            assert abs(a_perf - 1.0) < 1e-12, f"perfect predictor scored {a_perf}"
            assert abs(a_const - 0.5) < 1e-12, f"constant predictor scored {a_const}"
            assert abs(a_mono - a_plain) < 1e-12, "metric not monotone-invariant"
            checks["harness"] = {"perfect_predictor": round(float(a_perf), 12),
                                 "constant_predictor": round(float(a_const), 12),
                                 "monotone_invariance_absdiff": float(abs(a_mono - a_plain)),
                                 "permuted_labels_vs_oracle": round(float(a_perm), 4)}

        # ---- fit every cell in every chart, then evaluate every ordered pair ----
        # transfer[T][(i,j)] , relearn_raw[j] , relearn[T][j]
        transfer = {T: {} for T in CHARTS}
        relearn = {T: {} for T in CHARTS}
        raw_full = {}
        models = {}
        for T in CHARTS:
            for c in cells:
                m = fit(chart(TR[c], T, c[1]), TR[c]["y"])
                if m:
                    models[(T, c)] = m
            for j in cells:
                Xe = chart(EV[j], T, j[1])
                ye, sg = EV[j]["y"], EV[j]["seg"]
                for i in cells:
                    m = models.get((T, i))
                    if m is None:
                        continue
                    a = np.nanmean(batched_auc(ye, Xe @ m["v"], sg))
                    if i == j:
                        relearn[T][j] = float(a)
                    else:
                        transfer[T][(i, j)] = float(a)
                if T == "T0":                      # reproduction check vs cycle 004
                    Xf = chart(PK[j], "T0", j[1])
                    for i in cells:
                        m = models.get(("T0", i))
                        if m is None or i == j:
                            continue
                        raw_full[(i, j)] = float(np.nanmean(
                            batched_auc(PK[j]["y"], Xf @ m["v"], PK[j]["seg"])))

        # ---- assertion: T3 is the identity map, so it must equal T0 exactly ----
        d3 = max(abs(transfer["T3"][k] - transfer["T0"][k]) for k in transfer["T0"])
        assert d3 < 1e-12, f"T3 differs from T0 by {d3}; T3 was proved to be the identity"

        # ---- T1 acts on the score: AUC -> 1-AUC exactly ----
        transfer["T1"] = {k: 1.0 - v for k, v in transfer["T0"].items()}
        relearn["T1"] = {k: 1.0 - v for k, v in relearn["T0"].items()}
        if seed == SEEDS[0]:
            j0 = cells[0]
            i0 = next(i for i in cells if i != j0)
            m = models[("T0", i0)]
            Xe = chart(EV[j0], "T0", j0[1])
            a_pos = float(np.nanmean(batched_auc(EV[j0]["y"], Xe @ m["v"], EV[j0]["seg"])))
            a_neg = float(np.nanmean(batched_auc(EV[j0]["y"], -(Xe @ m["v"]), EV[j0]["seg"])))
            assert abs((a_pos + a_neg) - 1.0) < 1e-12, "sign flip is not AUC -> 1-AUC"
            # and the effective-weight shortcut must rank identically to predict_proba
            Z = (Xe - m["mu"]) / m["sd"]
            a_pp = float(np.nanmean(batched_auc(EV[j0]["y"],
                                                m["clf"].predict_proba(Z)[:, 1], EV[j0]["seg"])))
            assert abs(a_pp - a_pos) < 1e-12, "effective-weight score does not match predict_proba"
            checks["score_identities"] = {"sign_flip_sums_to_one": abs((a_pos + a_neg) - 1.0),
                                          "effective_weight_vs_predict_proba": abs(a_pp - a_pos)}

        # ---- pair typing ----
        def ptype(i, j):
            same_pair, same_rel = i[0] == j[0], i[1] == j[1]
            if same_pair and not same_rel:
                return "B_same_pair_diff_rel"
            if not same_pair and same_rel:
                return "C_diff_pair_same_rel"
            if not same_pair and not same_rel:
                return "D_diff_pair_diff_rel"
            return "same_cell"

        keys = sorted(transfer["T0"])
        types = {k: ptype(*k) for k in keys}
        mean_relearn = float(np.mean([relearn["T0"][j] for j in cells if j in relearn["T0"]]))
        mean_raw = float(np.mean([transfer["T0"][k] for k in keys]))
        headroom = mean_relearn - mean_raw
        assert headroom >= HEADROOM_FLOOR, (
            f"conditional headroom {headroom:.4f} < {HEADROOM_FLOOR}; population disqualified "
            "by the BOOTSTRAP S6 standing rule")

        def agg(T, sel=None):
            ks = [k for k in keys if sel is None or types[k] == sel]
            return float(np.mean([transfer[T][k] for k in ks])) if ks else None

        rec, rec_by_type, rec_median = {}, {}, {}
        for T in ["T0", "T1", "T2", "T3", "T4", "T5"]:
            a = agg(T)
            rec[T] = (a - mean_raw) / headroom
            rec_by_type[T] = {}
            for tp in ("B_same_pair_diff_rel", "C_diff_pair_same_rel", "D_diff_pair_diff_rel"):
                at, a0 = agg(T, tp), agg("T0", tp)
                ks = [k for k in keys if types[k] == tp]
                rl = float(np.mean([relearn["T0"][j] for (_, j) in set((i, j) for i, j in ks)]))
                rec_by_type[T][tp] = {"auc": at, "raw": a0,
                                      "recovery": (at - a0) / (rl - a0) if rl - a0 > 1e-9 else None}
            # D7 diagnostic: per-target-cell recovery, median over target cells
            pc = []
            for j in cells:
                ks = [k for k in keys if k[1] == j]
                if not ks or j not in relearn["T0"]:
                    continue
                a0 = float(np.mean([transfer["T0"][k] for k in ks]))
                aT = float(np.mean([transfer[T][k] for k in ks]))
                den = relearn["T0"][j] - a0
                if den > 1e-9:
                    pc.append((aT - a0) / den)
            rec_median[T] = float(np.median(pc)) if pc else None

        rawfull_by_type = {}
        for tp in ("B_same_pair_diff_rel", "C_diff_pair_same_rel", "D_diff_pair_diff_rel"):
            ks = [k for k in raw_full if types.get(k) == tp]
            rawfull_by_type[tp] = round(float(np.mean([raw_full[k] for k in ks])), 4) if ks else None

        per_seed.append({
            "seed": seed, "n_cells": len(cells), "n_ordered_pairs": len(keys),
            "mean_relearn_raw_chart": round(mean_relearn, 4),
            "mean_raw_transfer": round(mean_raw, 4),
            "headroom_relearn_minus_raw": round(headroom, 4),
            "headroom_floor": HEADROOM_FLOOR,
            "transfer_auc": {T: round(agg(T), 4) for T in ["T0", "T1", "T2", "T3", "T4", "T5"]},
            "relearn_auc_per_chart": {T: round(float(np.mean(list(relearn[T].values()))), 4)
                                      for T in ["T0", "T1", "T2", "T3", "T4", "T5"]},
            "recovery": {T: round(rec[T], 4) for T in rec},
            "recovery_median_over_target_cells_DIAGNOSTIC": {
                T: (round(v, 4) if v is not None else None) for T, v in rec_median.items()},
            "by_pair_type": {T: {tp: {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                                      for kk, vv in d.items()}
                                 for tp, d in rec_by_type[T].items()}
                             for T in rec_by_type},
            "cycle004_reproduction_check_raw_on_full_cell": rawfull_by_type,
        })

        # ---- hand-checkable rows, from the first seed ----
        if handrows is None:
            j0 = cells[0]
            i0 = next(i for i in cells if i[0] != j0[0] and i[1] == j0[1])
            m0, m4 = models[("T0", i0)], models[("T4", i0)]
            ss = cell[j0]
            _, evi = split_idx(seed, j0, len(ss))
            s = ss[evi[0]]
            X0 = chart(pack([s]), "T0", j0[1])
            X4 = chart(pack([s]), "T4", j0[1])
            sc0, sc4 = X0 @ m0["v"], X4 @ m4["v"]
            r0 = np.argsort(np.argsort(-sc0)) + 1
            r4 = np.argsort(np.argsort(-sc4)) + 1
            rows = []
            for t in range(min(20, len(s["labels"]))):
                rows.append({
                    "candidate": s["cands"][t], "label_broke": s["labels"][t],
                    "raw_features": {n: round(float(X0[t, IX[n]]), 6) for n in FEATS},
                    "T4_features": {n: round(float(X4[t, IX[n]]), 6) for n in FEATS},
                    "score_T0": round(float(sc0[t]), 6), "rank_T0_desc": int(r0[t]),
                    "score_T4": round(float(sc4[t]), 6), "rank_T4_desc": int(r4[t]),
                })
            handrows = {
                "note": "score = sum_n feature[n] * effective_weight[n]; rank 1 = highest score. "
                        "AUC ranks by score within this one state; label_broke=1 is the positive "
                        "class. Multiply and check without running the code.",
                "source_cell_i": cellname(i0), "target_cell_j": cellname(j0),
                "state_tested_invariant": s["tested"], "state_target_value": s["target"],
                "state_parent_object": s["pobj"], "state_relation": s["rel"],
                "n_candidates_in_state": len(s["labels"]),
                "effective_weights_T0": {n: round(float(m0["v"][IX[n]]), 6) for n in FEATS},
                "effective_weights_T4": {n: round(float(m4["v"][IX[n]]), 6) for n in FEATS},
                "auc_this_state_T0": float(batched_auc(
                    np.array(s["labels"], float), sc0, np.array([len(s["labels"])]))[0]),
                "auc_this_state_T4": float(batched_auc(
                    np.array(s["labels"], float), sc4, np.array([len(s["labels"])]))[0]),
                "rows": rows}
        print(f"seed {seed}: cells={len(cells)} pairs={len(keys)} "
              f"relearn={mean_relearn:.4f} raw={mean_raw:.4f} headroom={headroom:.4f}")
        print("   transfer:", {T: round(agg(T), 4) for T in ["T0", "T1", "T2", "T3", "T4", "T5"]})
        print("   recovery:", {T: round(rec[T], 4) for T in rec})

    # ------------------------------------------------------------------ aggregate
    def A(path):
        v = [r for r in (p for p in per_seed)]
        return v

    trans = {T: round(float(np.mean([p["transfer_auc"][T] for p in per_seed])), 4)
             for T in ["T0", "T1", "T2", "T3", "T4", "T5"]}
    recov = {T: round(float(np.mean([p["recovery"][T] for p in per_seed])), 4)
             for T in ["T0", "T1", "T2", "T3", "T4", "T5"]}
    se = {T: round(float(np.std([p["recovery"][T] for p in per_seed], ddof=1)
                         / math.sqrt(len(per_seed))), 4)
          for T in recov} if len(per_seed) > 1 else {}
    best_T = max(recov, key=lambda t: recov[t])
    best = recov[best_T]

    if best >= 0.50:
        band, disposition = "Q2_FAILS_CHART_MISMATCH", "REDESIGN"
    elif best >= 0.25:
        band, disposition = "MIXED_AMBIGUOUS", "PARK"
    else:
        band, disposition = "Q2_SURVIVES_FOR_LIVE_TRANSPORTS", "PARK"

    rep = {
        "prereg": "CYCLE_005_PREREG_terminal.md S3",
        "amendment": "AMENDMENT_2026-08-25b_armB_specification.md",
        "arm": "B", "question": "Q2 — does anti-transfer survive mathematically natural transport?",
        "evidence_rung": "5 (fitted, sampled) for the AUCs; 1 for the assertions in `checks`",
        "decisive_comparison": "transport vs local relearning",
        "band": band, "disposition": disposition,
        "best_transport": best_T, "best_recovery": best,
        "gate_Q2_fails_at": 0.50, "gate_mixed_at": 0.25,
        "mean_transfer_auc": trans, "mean_recovery": recov, "recovery_se_over_seeds": se,
        "mean_relearn_raw_chart": round(float(np.mean([p["mean_relearn_raw_chart"]
                                                       for p in per_seed])), 4),
        "mean_raw_transfer": round(float(np.mean([p["mean_raw_transfer"] for p in per_seed])), 4),
        "mean_headroom": round(float(np.mean([p["headroom_relearn_minus_raw"]
                                              for p in per_seed])), 4),
        "degenerate_transports_declared_before_measurement": {
            "T0": "identity (definitional)",
            "T3": "identity map on this population; asserted equal to T0 to 1e-12",
            "T2": "identity within-relation; acts only across relations (one threshold exists)",
            "T1": "closed form AUC -> 1-AUC; asserted",
        },
        "checks": checks, "per_seed": per_seed,
    }
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    ROWS_OUT.write_text(json.dumps(handrows, indent=1), encoding="utf-8")
    print("\nBAND:", band, "| DISPOSITION:", disposition)
    print("transfer AUC:", json.dumps(trans))
    print("recovery    :", json.dumps(recov))
    print("recovery SE :", json.dumps(se))
    print(f"best transport {best_T} at recovery {best:.4f} "
          f"(relearn {rep['mean_relearn_raw_chart']}, raw {rep['mean_raw_transfer']})")
    print("->", OUT)
    print("->", ROWS_OUT)


if __name__ == "__main__":
    main()
