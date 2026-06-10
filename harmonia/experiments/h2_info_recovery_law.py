"""h2 information-recovery LAW harness (§3.3 of Proposal E, generalized).

Pre-registration: D:\\Prometheus\\harmonia\\experiments\\h2_info_recovery_prereg.md
(read decision rules there BEFORE this output).

Measures, for the h2 kill-label scheme and redesign candidates:

  Q2  I(pair; Y_fresh), I(tag; Y_fresh), I(tag; Y_fresh | pair) — analytic
      (from per-(pair,method) verdict distributions estimated at R draws via
      the PRODUCTION evaluator) and empirical (production .next() kills paired
      with fresh production evaluations; permutation nulls).
  Q3  per-pair tag entropy + test-retest match probability (echo vs noise).
  D   redesign candidates S1..S5 under the iterate-or-kill loop, each scored
      by I(label; Y) and I(label; Y | pair) + held-out predictive lift (L2).
  C   a4-INCONCLUSIVE-weighted pair mix (the production-realistic prior).
  BUG production method-skip mislabeling rate per pair (index-shift defect,
      h2_triangulation_protocol.py REJECTED branch).

Y_fresh := verdict triple of a fresh (M1, M2, M3) production evaluation of the
same (ki, ei) pair, independent seeds (27-valued).

Run:  python harmonia/experiments/h2_info_recovery_law.py
Output: harmonia/experiments/_h2_info_recovery_law_results.json (flushed per
phase; no shell redirection).
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from itertools import product as iproduct
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(Path(__file__).parent))

from theseus.emit.record_schema import Verdict  # noqa: E402
from theseus.generators.h2_triangulation_protocol import (  # noqa: E402
    H2TriangulationProtocolGenerator,
    METHOD_VARIANTS,
)
from theseus.generators.a4_symbolic_regression import (  # noqa: E402
    A4SymbolicRegressionGenerator,
)
from theseus.generators.a1_catalog_cross_product import (  # noqa: E402
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
)
from h2_backfill_and_validate import (  # noqa: E402
    make_parent, split_label, shannon_entropy,
)

SEED = 20260610  # pre-registered master seed
R_GROUND_TRUTH = 2000          # draws per (pair, method)
N_EMPIRICAL_KILLS = 3000       # production kills paired with fresh Y
N_PERMS = 200                  # permutation-null shuffles
A4_INC_TARGET = 2000           # a4@15 INCONCLUSIVE parents for the mix
A4_ATTEMPT_CAP = 150_000

PAIRS = [(ki, ei) for ki in KNOT_INTEGER_INVARIANTS for ei in EC_INTEGER_INVARIANTS]
V3 = (Verdict.SHADOW_CATALOG.value, Verdict.INCONCLUSIVE.value, Verdict.REJECTED.value)
RESULTS_PATH = Path(__file__).parent / "_h2_info_recovery_law_results.json"


# ---------------------------------------------------------------------------
# Information-theory helpers (plug-in, bits)
# ---------------------------------------------------------------------------
def mi_from_joint(joint: dict) -> float:
    """joint: {(x, y): count} -> plug-in mutual information in bits."""
    tot = sum(joint.values())
    if tot == 0:
        return 0.0
    px, py = Counter(), Counter()
    for (x, y), c in joint.items():
        px[x] += c
        py[y] += c
    mi = 0.0
    for (x, y), c in joint.items():
        if c == 0:
            continue
        p = c / tot
        mi += p * math.log2(p * tot * tot / (px[x] * py[y]))
    return mi


def cond_mi(triples) -> float:
    """triples: iterable of (x, y, z) -> I(X; Y | Z) in bits (plug-in)."""
    by_z = defaultdict(Counter)
    for x, y, z in triples:
        by_z[z][(x, y)] += 1
    tot = sum(sum(c.values()) for c in by_z.values())
    out = 0.0
    for z, joint in by_z.items():
        nz = sum(joint.values())
        out += (nz / tot) * mi_from_joint(dict(joint))
    return out


def perm_null_mi(xs, ys, n_perms, rng, conditional_zs=None):
    """95th percentile of MI (or CMI) under label shuffling."""
    vals = []
    ys = list(ys)
    for _ in range(n_perms):
        rng.shuffle(ys)
        if conditional_zs is None:
            joint = Counter(zip(xs, ys))
            vals.append(mi_from_joint(dict(joint)))
        else:
            vals.append(cond_mi(zip(xs, ys, conditional_zs)))
    vals.sort()
    return vals[int(0.95 * len(vals))] if vals else 0.0


# ---------------------------------------------------------------------------
# Phase B — ground truth P(verdict | pair, method) via PRODUCTION evaluator
# ---------------------------------------------------------------------------
def ground_truth_pools(gen, rng):
    """R_GROUND_TRUTH draws per (pair, method) -> verdict counts + skip rate."""
    pools = {}   # (pair, m_idx) -> Counter(verdict); 'SKIP' for r2 None
    for (ki, ei) in PAIRS:
        for m_idx, (mname, n_target, degree) in enumerate(METHOD_VARIANTS):
            c = Counter()
            for _ in range(R_GROUND_TRUTH):
                r2, _n = gen._polyfit_at_method(
                    ki, ei, n_target, degree, rng.randint(0, 2**31))
                if r2 is None:
                    c["SKIP"] += 1
                else:
                    c[gen._r2_to_verdict(r2)] += 1
            pools[(ki, ei, m_idx)] = c
    return pools


def analytic_quantities(pools, pair_prior):
    """Exact-in-model quantities from per-cell verdict probabilities.
    Skips are folded out (conditional on all three methods evaluating), with
    the skip rate reported separately — the bug analysis owns that branch."""
    per_pair = {}
    for (ki, ei) in PAIRS:
        pv = []
        for m_idx in range(3):
            c = pools[(ki, ei, m_idx)]
            tot = sum(v for k, v in c.items() if k != "SKIP")
            pv.append({v: c.get(v, 0) / tot if tot else 0.0 for v in V3})
        # joint over 27 verdict triples (independence by construction)
        joint = {}
        for trip in iproduct(V3, repeat=3):
            joint[trip] = pv[0][trip[0]] * pv[1][trip[1]] * pv[2][trip[2]]
        # kill = >= 2 of 3 REJECTED (2/3 majority toward REJECTED)
        kill_p = sum(p for t, p in joint.items()
                     if sum(1 for v in t if v == Verdict.REJECTED.value) >= 2)
        # tag distribution given kill
        tag_p = Counter()
        for t, p in joint.items():
            n_rej = sum(1 for v in t if v == Verdict.REJECTED.value)
            if n_rej < 2:
                continue
            rej = sorted(METHOD_VARIANTS[i][0]
                         for i, v in enumerate(t) if v == Verdict.REJECTED.value)
            tag_p["_".join(m[0] for m in rej)] += p
        tag_p = {k: v / kill_p for k, v in tag_p.items()} if kill_p > 0 else {}
        per_pair[(ki, ei)] = {
            "p_verdict": pv, "joint27": joint, "kill_p": kill_p, "tag_p": tag_p,
            "skip_rate": [
                pools[(ki, ei, m)]["SKIP"] / sum(pools[(ki, ei, m)].values())
                for m in range(3)],
        }

    # I(pair; Y) under prior, Y = fresh verdict triple
    joint_pair_y = {}
    for (ki, ei), d in per_pair.items():
        w = pair_prior.get((ki, ei), 0.0)
        for t, p in d["joint27"].items():
            joint_pair_y[((ki, ei), t)] = w * p
    scale = 1_000_000  # counts proxy for the plug-in helper
    i_pair_y = mi_from_joint({k: v * scale for k, v in joint_pair_y.items()})

    # I(tag; Y) and I(tag; Y | pair): tag from one kill emission, Y fresh —
    # independent given pair, so joint(tag, Y | pair) = tag_p x joint27.
    # Pair prior restricted to kills: w_kill(pair) ∝ prior * kill_p.
    wk = {pr: pair_prior.get(pr, 0.0) * per_pair[pr]["kill_p"] for pr in per_pair}
    z = sum(wk.values()) or 1.0
    wk = {pr: v / z for pr, v in wk.items()}
    joint_tag_y, trips = {}, []
    for pr, d in per_pair.items():
        for tag, tp in d["tag_p"].items():
            for t, p in d["joint27"].items():
                key = (tag, t)
                joint_tag_y[key] = joint_tag_y.get(key, 0.0) + wk[pr] * tp * p
    i_tag_y = mi_from_joint({k: v * scale for k, v in joint_tag_y.items()})
    # conditional: sum_pair w * I(tag; Y | pair) = 0 exactly by product form —
    # computed anyway as a self-check of the pipeline arithmetic.
    i_tag_y_given_pair = 0.0
    for pr, d in per_pair.items():
        j = {(tag, t): tp * p
             for tag, tp in d["tag_p"].items()
             for t, p in d["joint27"].items()}
        i_tag_y_given_pair += wk[pr] * mi_from_joint(
            {k: v * scale for k, v in j.items()})

    return per_pair, {
        "I_pair_Y_bits": i_pair_y,
        "I_tag_Y_bits": i_tag_y,
        "I_tag_Y_given_pair_bits": i_tag_y_given_pair,
        "dpi_ok": i_tag_y <= i_pair_y + 1e-9,
    }


# ---------------------------------------------------------------------------
# Phase A-empirical — production kills paired with fresh production Y
# ---------------------------------------------------------------------------
def empirical_run(rng):
    gen = H2TriangulationProtocolGenerator(
        batch_id="harmonia-E-law-empirical", seed=SEED + 7)
    gen._loaded = True
    gen._inconclusive_parents = [
        make_parent(ki, ei, 0) for (ki, ei) in PAIRS]
    rows = []
    while len(rows) < N_EMPIRICAL_KILLS:
        r = gen.next()
        if r is None or r.verdict != Verdict.REJECTED.value or not r.kill_pattern:
            continue
        agr, pair, tag = split_label(r.kill_pattern)
        ki = r.claim_payload["knot_invariant"]
        ei = r.claim_payload["ec_invariant"]
        y = []
        for (mname, n_target, degree) in METHOD_VARIANTS:
            r2, _ = gen._polyfit_at_method(
                ki, ei, n_target, degree, rng.randint(0, 2**31))
            y.append("SKIP" if r2 is None else gen._r2_to_verdict(r2))
        rows.append({
            "pair": pair, "tag": tag, "agr": agr, "y": tuple(y),
            "mean_r2": r.claim_payload["mean_r2"],
            "max_r2": max(r.claim_payload["method_r2s"]),
            "n_methods": r.claim_payload["n_methods_evaluated"],
        })
    return rows


def empirical_mi(rows, rng):
    pairs = [r["pair"] for r in rows]
    tags = [r["tag"] for r in rows]
    ys = [r["y"] for r in rows]
    i_pair_y = mi_from_joint(dict(Counter(zip(pairs, ys))))
    i_tag_y = mi_from_joint(dict(Counter(zip(tags, ys))))
    i_tag_y_g_pair = cond_mi(zip(tags, ys, pairs))
    return {
        "n": len(rows),
        "I_pair_Y_bits": i_pair_y,
        "I_pair_Y_null95": perm_null_mi(pairs, list(ys), N_PERMS, rng),
        "I_tag_Y_bits": i_tag_y,
        "I_tag_Y_null95": perm_null_mi(tags, list(ys), N_PERMS, rng),
        "I_tag_Y_given_pair_bits": i_tag_y_g_pair,
        "I_tag_Y_given_pair_null95": perm_null_mi(
            tags, list(ys), N_PERMS, rng, conditional_zs=pairs),
    }


# ---------------------------------------------------------------------------
# Phase D — redesign candidates (iterate-or-kill rounds 2..3)
# ---------------------------------------------------------------------------
def r2_band(x):
    if x < 0.0:
        return "neg"
    if x < 0.1:
        return "lo"
    if x < 0.3:
        return "mid"
    return "hi"


def redesign_scoring(rows, rng):
    """Score label-scheme candidates on the SAME empirical rows."""
    schemes = {
        "S1_current(agr,pair,tag)": lambda r: (r["agr"], r["pair"], r["tag"]),
        "S2_pair_only": lambda r: r["pair"],
        "S3_pair+meanR2band": lambda r: (r["pair"], r2_band(r["mean_r2"])),
        "S4_pair+maxR2band": lambda r: (r["pair"], r2_band(r["max_r2"])),
        "S5_tag_only(d3_style)": lambda r: r["tag"],
    }
    pairs = [r["pair"] for r in rows]
    ys = [r["y"] for r in rows]
    out = {}
    half = len(rows) // 2
    for name, fn in schemes.items():
        labels = [fn(r) for r in rows]
        i_l_y = mi_from_joint(dict(Counter(zip(labels, ys))))
        i_l_y_g_pair = cond_mi(zip(labels, ys, pairs))
        null95 = perm_null_mi(labels, list(ys), N_PERMS, rng,
                              conditional_zs=pairs)
        # L2 lens: held-out predictive accuracy of fresh-Y "n_rejected" from
        # the label (majority class per label on train half).
        tgt = [sum(1 for v in r["y"] if v == Verdict.REJECTED.value) for r in rows]
        train_maj = defaultdict(Counter)
        for lbl, t in zip(labels[:half], tgt[:half]):
            train_maj[lbl][t] += 1
        global_maj = Counter(tgt[:half]).most_common(1)[0][0]
        pred = [train_maj[lbl].most_common(1)[0][0] if lbl in train_maj
                else global_maj for lbl in labels[half:]]
        acc = sum(1 for p, t in zip(pred, tgt[half:]) if p == t) / max(1, len(pred))
        base_acc = sum(1 for t in tgt[half:] if t == global_maj) / max(1, len(tgt[half:]))
        out[name] = {
            "I_label_Y_bits": i_l_y,
            "I_label_Y_given_pair_bits": i_l_y_g_pair,
            "I_label_Y_given_pair_null95": null95,
            "beyond_coordinate_signal": i_l_y_g_pair > null95,
            "L2_heldout_acc": acc, "L2_flat_baseline_acc": base_acc,
            "L2_lift": acc - base_acc,
        }
    return out


# ---------------------------------------------------------------------------
# Phase C — a4-INCONCLUSIVE pair mix (production-realistic prior)
# ---------------------------------------------------------------------------
def a4_inconclusive_mix():
    gen = A4SymbolicRegressionGenerator(
        batch_id="harmonia-E-a4mix", seed=SEED + 99, sample_size=15)
    c, attempts = Counter(), 0
    while sum(c.values()) < A4_INC_TARGET and attempts < A4_ATTEMPT_CAP:
        attempts += 1
        r = gen.next()
        if r is None:
            break
        if r.verdict == Verdict.INCONCLUSIVE.value:
            p = r.claim_payload
            if "knot_invariant" in p and "ec_invariant" in p:
                c[(p["knot_invariant"], p["ec_invariant"])] += 1
    tot = sum(c.values())
    return ({pr: c.get(pr, 0) / tot for pr in PAIRS} if tot else {}), attempts, tot


# ---------------------------------------------------------------------------
def main():
    rng = random.Random(SEED)
    out = {"prereg": "h2_info_recovery_prereg.md", "seed": SEED,
           "R_ground_truth": R_GROUND_TRUTH}

    print("[B] ground-truth pools (24 pairs x 3 methods x "
          f"{R_GROUND_TRUTH})...", flush=True)
    gen = H2TriangulationProtocolGenerator(batch_id="harmonia-E-law-gt", seed=SEED)
    pools = ground_truth_pools(gen, rng)

    print("[C] a4@15 INCONCLUSIVE pair mix...", flush=True)
    a4_prior, a4_attempts, a4_n = a4_inconclusive_mix()
    out["a4_mix"] = {
        "attempts": a4_attempts, "n_inconclusive": a4_n,
        "inconclusive_rate": a4_n / a4_attempts if a4_attempts else 0.0,
        "prior_nonzero_pairs": sum(1 for v in (a4_prior or {}).values() if v > 0),
        "prior": {f"{k[0]}|{k[1]}": v for k, v in (a4_prior or {}).items()},
    }

    uniform_prior = {pr: 1 / len(PAIRS) for pr in PAIRS}
    print("[B2] analytic quantities (uniform + a4 priors)...", flush=True)
    per_pair, analytic_u = analytic_quantities(pools, uniform_prior)
    out["analytic_uniform_prior"] = analytic_u
    if a4_n:
        _, analytic_a4 = analytic_quantities(pools, a4_prior)
        out["analytic_a4_prior"] = analytic_a4

    # Q3 — tag echo-vs-noise per pair (kills only, analytic)
    q3 = {}
    for pr, d in per_pair.items():
        tp = d["tag_p"]
        match_p = sum(p * p for p in tp.values())  # P(tag1 == tag2 | pair)
        q3[f"{pr[0]}|{pr[1]}"] = {
            "kill_p": d["kill_p"],
            "H_tag_given_pair_bits": -sum(
                p * math.log2(p) for p in tp.values() if p > 0),
            "P_tag_match": match_p,
            "tag_dist": {k: round(v, 4) for k, v in
                         sorted(tp.items(), key=lambda kv: -kv[1])},
            "skip_rate_per_method": [round(s, 4) for s in d["skip_rate"]],
        }
    out["q3_per_pair"] = q3
    kill_ps = [d["kill_p"] for d in per_pair.values()]
    out["kill_p_range"] = [min(kill_ps), max(kill_ps)]
    RESULTS_PATH.write_text(json.dumps(out, indent=2, default=str),
                            encoding="utf-8")

    print("[A] empirical production kills + fresh Y "
          f"(n={N_EMPIRICAL_KILLS})...", flush=True)
    rows = empirical_run(rng)
    out["empirical_mi"] = empirical_mi(rows, rng)
    print("[D] redesign candidate scoring...", flush=True)
    out["redesign"] = redesign_scoring(rows, rng)

    # BUG quantification — production skip-driven mislabeling
    n_skip_kills = sum(1 for r in rows if r["n_methods"] < 3)
    out["production_bug"] = {
        "kills_with_skipped_method": n_skip_kills,
        "fraction": n_skip_kills / len(rows),
        "note": "all such kills carry a misattributed method_tag "
                 "(index-shift defect, REJECTED branch)",
    }

    RESULTS_PATH.write_text(json.dumps(out, indent=2, default=str),
                            encoding="utf-8")
    print("\n=== analytic (uniform prior) ===", flush=True)
    print(json.dumps(out["analytic_uniform_prior"], indent=2), flush=True)
    if "analytic_a4_prior" in out:
        print("=== analytic (a4 prior) ===", flush=True)
        print(json.dumps(out["analytic_a4_prior"], indent=2), flush=True)
    print("=== empirical MI ===", flush=True)
    print(json.dumps(out["empirical_mi"], indent=2), flush=True)
    print("=== redesign ===", flush=True)
    print(json.dumps(out["redesign"], indent=2), flush=True)
    print("=== production bug ===", flush=True)
    print(json.dumps(out["production_bug"], indent=2), flush=True)
    print(f"\nresults -> {RESULTS_PATH}", flush=True)


if __name__ == "__main__":
    main()
