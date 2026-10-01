"""Shadow decision layer for the alien-lawful assay: an independent,
exact-arithmetic re-implementation of every PREREG s6/s7 decision rule.

    python -m hecate.alien.shadow_decisions --model claude [--json]

Why: roles/Hecate/harvest_w2/AUDIT_A_alien_semantics.md found that the frozen
analysis (analyze.py) compares thresholds on float means (F01: H3,
0.2 - 0.1 = 0.0999... < 0.10) and applies some rules that differ from the
PREREG text (F02 H4 rule, F03 detector alien sets, F04 degenerate bootstrap
CIs). The frozen code and RESULTS.json are NOT modified; this module only
reads them and reports, per hypothesis:

    recorded decision (RESULTS.json)  |  shadow decision (PREREG text)  |  DIVERGES

Sources (all read-only):
  - answer key, groups, subsets: hecate/alien/data/answer_key.json via
    runner.load / runner.subsets / score.grp (frozen).
  - per-item T1/T2 recomputed here from runs/<model>/*.jsonl with the frozen
    parser (score._states, score.structure_score), in Fractions.
  - sandbox-dependent per-item scores (T5 code eval, analogy-code eval) are
    taken from the frozen per-system scores in RESULTS.json "rows" (running
    the sandbox again takes minutes; AUDIT_A s0 showed RESULTS reproduces
    byte-for-byte). Bars from data/BASELINES.json.
  Floats from frozen code are mapped back to the rational they represent
  (q(): Fraction.limit_denominator(10**6); every such quantity is a mean of
  <= 200 values with denominators <= 12, so recovery is exact; q() asserts
  the float round-trips).

The snapshot is the set of rows RESULTS.json scored: blind rows written to
runs/ after RESULTS.json (free-tier trickle) are counted, not used, so the
comparison is like-for-like.

Every threshold/decision is decided on Fractions or integer counts. The
bootstrap (2000, seed 20260930, systems resampled within group, percentile
index rule of score.boot_diff) is replayed with the same random stream, so
any divergence is the decision layer, not resampling noise. Where the
PREREG is ambiguous every consistent reading is emitted, labelled; the
`primary` reading uses the frozen code's choice of sets/predicates so that a
primary DIVERGES isolates arithmetic / rule-form differences.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from bisect import bisect_left, bisect_right
from fractions import Fraction
from functools import lru_cache

from hecate.alien import score as S
from hecate.alien.dataset import OUT
from hecate.alien.runner import RUNS, load, subsets

F = Fraction
BOOT, BOOT_SEED = S.BOOT, S.BOOT_SEED
LEARN_MARGIN, LEARN_EXACT, CODE_LEARN_EXACT = F(3, 20), F(1, 4), F(1, 2)      # PREREG s4
THR = {"H1": F(1, 10), "H2": F(3, 20), "H3": F(1, 10), "H4": F(1, 10), "H5": F(3, 20)}
DET_AUC, DET_CI_LO, DET_PAIR = F(4, 5), F(13, 20), F(4, 5)                     # PREREG s7
FAMS = ("tab", "graph", "rewrite", "vm", "map")


# ---- exact helpers ----------------------------------------------------------------

def q(x, maxden=10 ** 6):
    """Float from frozen code -> the small-denominator rational it encodes."""
    if x is None:
        return None
    if isinstance(x, (Fraction, int)):
        return F(x)
    r = F(x).limit_denominator(maxden)
    assert abs(float(r) - float(x)) < 1e-9, (x, r)
    return r


def fmt(x):
    if x is None:
        return "None"
    if isinstance(x, Fraction):
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    if isinstance(x, float):
        return repr(x)
    return str(x)


def decide(est, ci, thr):
    """PREREG s6 general rule, exact. ci = (lo, hi)."""
    if est is None or ci is None or ci[0] is None:
        return "NOT_ELIGIBLE"
    if est >= thr and ci[0] > 0:
        return "SUPPORTED"
    if est <= 0 and ci[1] < thr / 2:
        return "NOT_SUPPORTED"
    return "INDETERMINATE"


def auc_exact(pos, neg):
    """Mann-Whitney AUC, ties 0.5, as a Fraction. pos/neg: comparable exact values."""
    if not pos or not neg:
        return None
    ns = sorted(neg)
    twice = 0
    for a in pos:
        lo, hi = bisect_left(ns, a), bisect_right(ns, a)
        twice += 2 * lo + (hi - lo)
    return F(twice, 2 * len(pos) * len(neg))


def rate(vals):
    vals = [v for v in vals if v is not None]
    return (F(sum(vals), len(vals)), len(vals)) if vals else (None, 0)


def boot(groups, stat, seed=BOOT_SEED, n=BOOT):
    """Within-group resampling; draw order = order of `groups` (matches
    analyze.diff_auc [K, A, N] and score.boot_diff [a, b]). Same percentile
    index rule as the frozen code. Returns (lo, hi, n_distinct)."""
    if any(not g for g in groups):
        return None, None, 0
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        smp = [[rng.choice(g) for _ in g] for g in groups]
        v = stat(*smp)
        if v is not None:
            vals.append(v)
    if not vals:
        return None, None, 0
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1], len(set(vals))


def clopper_pearson(x, n, alpha=0.05):
    """Exact two-sided (1-alpha) binomial interval, as exact Fractions of the
    float quantiles (the bound itself is a float computation)."""
    from scipy.stats import beta
    if n == 0:
        return None, None
    lo = 0.0 if x == 0 else float(beta.ppf(alpha / 2, x, n - x + 1))
    hi = 1.0 if x == n else float(beta.ppf(1 - alpha / 2, x + 1, n - x))
    return F(lo), F(hi)


def cp_rate_diff(xs_plus, xs_minus):
    """Conservative interval for sum(p_plus) - sum(p_minus) by interval
    arithmetic over per-group 95% Clopper-Pearson intervals. xs_*: list of
    (count, n)."""
    lo = hi = F(0)
    for x, n in xs_plus:
        a, b = clopper_pearson(x, n)
        lo, hi = lo + a, hi + b
    for x, n in xs_minus:
        a, b = clopper_pearson(x, n)
        lo, hi = lo - b, hi - a
    return lo, hi


# ---- per-item layer (frozen scorers, exact values) ---------------------------------

def _t2_exact(p, obj, truth_states):
    """score.score_t2 in Fractions, using the frozen parser score._states."""
    preds = S._states(p, ((obj or {}).get("t2") or {}).get("predictions"))
    truth = [tuple(s) for s in truth_states]
    ex = comp = F(0)
    for i, t in enumerate(truth):
        pr = preds[i] if i < len(preds) else None
        if pr is None:
            continue
        ex += int(tuple(pr) == t)
        comp += F(sum(a == b for a, b in zip(pr, t)), len(t))
    n = len(truth)
    return ex / n, comp / n


def _t1_exact(obj):
    sc, v = S.structure_score(obj)
    return q(sc), v


def _conf(o):
    try:
        return q(float(o.get("confidence") or 0))
    except (TypeError, ValueError):
        return F(0)


def _analogy_class(o, asc, bar):
    """score.analogy_class decision layer in Fractions (PREREG s4 T6)."""
    o = o or {}
    name, conf = o.get("analogy"), _conf(o)
    if not name or str(name).lower() in ("null", "none") or conf < F(3, 10):
        return "NO_ANALOGY"
    ex = q(asc.get("eval_exact")) if asc else None
    comp = q(asc.get("eval_comp")) if asc else None
    if ex is not None and ex >= F(9, 10):
        return "CORRECT_ANALOGY"
    if comp is not None and comp >= bar + F(1, 5):
        return "USEFUL_PARTIAL_ANALOGY"
    if conf >= F(3, 5) and str(o.get("claimed_equivalence", "")).upper() in ("EXACT", "PARTIAL"):
        return "FALSE_COLLAPSE_TO_FAMILIAR"
    return "SUPERFICIAL_ANALOGY"


def _learned(t2, t5):
    ex, comp, bar = t2
    return bool((comp >= bar + LEARN_MARGIN and ex >= LEARN_EXACT) or
                (q((t5 or {}).get("eval_exact")) or 0) >= CODE_LEARN_EXACT)


def _ok(row):
    return bool(row and row.get("ok") and isinstance(row.get("parsed"), dict))


def _results(model):
    path = os.path.join(RUNS, model, "RESULTS.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def per_item(model):
    _, key = load()
    with open(os.path.join(OUT, "BASELINES.json"), encoding="utf-8") as fh:
        base = {r["id"]: r for r in json.load(fh)["rows"]}
    res = _results(model)
    rec_rows = res["rows"]
    blind, fam = S.read(model, "blind"), S.read(model, "fam")
    reveal, active = S.read(model, "reveal"), S.read(model, "active")
    rows, checks = {}, {"t2_mismatch": [], "t1_mismatch": [], "learned_flips": [],
                        "analogy_class_flips": [], "active_learned_flips": [],
                        "unscored_new_blind_rows": [], "unscored_new_fam_rows": []}
    for sid, e in sorted(key.items()):
        p, ans, b = e["params"], e["answers"], base[sid]
        rr = rec_rows.get(sid, {})
        r = {"id": sid, "group": S.grp(e), "family": e["family"],
             "bar_t2": max(q(b["identity_t2_comp"]), q(b["nn_t2_comp"])),
             "bar_eval": max(q(b["identity_eval_comp"]), q(b["nn_eval_comp"]))}
        br = blind.get(sid)
        if _ok(br) and "t1_score" not in rr:
            checks["unscored_new_blind_rows"].append(sid)
        if _ok(br) and "t1_score" in rr:
            o = br["parsed"]
            r["t1_score"], r["t1_verdict"] = _t1_exact(o)
            r["t2_exact"], r["t2_comp"] = _t2_exact(p, o, ans["t2"])
            t5 = rr.get("t5") or {}
            r["t5_eval_exact"], r["t5_eval_comp"] = q(t5.get("eval_exact")), q(t5.get("eval_comp"))
            r["learned"] = _learned((r["t2_exact"], r["t2_comp"], r["bar_t2"]), t5)
            r["behav_score"] = max(r["t2_comp"] - r["bar_t2"], (r["t5_eval_comp"] or 0) - r["bar_eval"])
            if (abs(float(r["t2_comp"]) - rr["t2_comp"]) > 1e-12 or
                    abs(float(r["t2_exact"]) - rr["t2_exact"]) > 1e-12):
                checks["t2_mismatch"].append(sid)
            if r["t1_verdict"] != rr["t1_verdict"] or abs(float(r["t1_score"]) - rr["t1_score"]) > 1e-12:
                checks["t1_mismatch"].append(sid)
            if r["learned"] != rr["learned"]:
                checks["learned_flips"].append(sid)
        fr = fam.get(sid)
        if _ok(fr) and "coherence" not in rr:
            checks["unscored_new_fam_rows"].append(sid)
        if _ok(fr) and "coherence" in rr:
            o = fr["parsed"]
            r["coherence"] = str(o.get("coherence", "")).upper()
            asc = rr.get("analogy_score")
            asc = asc if asc and asc.get("status") == "OK" else None
            r["analogy_class"] = _analogy_class(o, asc, r["bar_eval"])
            if r["analogy_class"] != rr.get("analogy_class"):
                checks["analogy_class_flips"].append(sid)
        rv = reveal.get(sid)
        if _ok(rv) and "reveal" in rr:
            r["reveal_coherence"] = str(rv["parsed"].get("coherence", "")).upper()
        ac = active.get(sid)
        if _ok(ac) and "active" in rr:
            ex, comp = _t2_exact(p, ac["parsed"], ans["t2"])
            r["active_learned"] = _learned((ex, comp, r["bar_t2"]), rr["active"].get("t5"))
            if r["active_learned"] != rr["active"]["learned"]:
                checks["active_learned_flips"].append(sid)
        rows[sid] = r
    return rows, key, res["summary"], checks


# ---- decision layer ----------------------------------------------------------------

def _int_keys(rows, fields):
    """AUC depends only on order: add exact integer images k = x * lcm(dens)
    (order-preserving, tie-preserving) so the 2000-replicate bootstrap compares ints."""
    from math import lcm
    for fld in fields:
        vals = [r[fld] for r in rows.values() if r.get(fld) is not None]
        d = lcm(*[v.denominator for v in vals]) if vals else 1
        for r in rows.values():
            if r.get(fld) is not None:
                r["_k_" + fld] = r[fld].numerator * (d // r[fld].denominator)


def _reading(label, decision, recorded, inputs, note=""):
    return {"label": label, "decision": decision, "recorded": recorded,
            "diverges": decision != recorded, "inputs": inputs, "note": note}


def _degenerate(ci):
    return ci[0] is not None and ci[0] == ci[1]


def _rate_hyp(name, fn, A_sets, K, thr, recorded):
    """H2 / H5: rate_A - rate_K >= thr, s6 rule; one reading per alien set,
    plus a Clopper-Pearson reading wherever the bootstrap CI is degenerate."""
    out = []
    for label, A in A_sets:
        av = [fn(r) for r in A if fn(r) is not None]
        kv = [fn(r) for r in K if fn(r) is not None]
        if not av or not kv:
            out.append(_reading(label, "NOT_ELIGIBLE", recorded, {"n_A": len(av), "n_K": len(kv)}))
            continue
        est = F(sum(av), len(av)) - F(sum(kv), len(kv))
        lo, hi, nd = boot([av, kv], lambda a, b: F(sum(a), len(a)) - F(sum(b), len(b)))
        inp = {"A": f"{sum(av)}/{len(av)}", "K": f"{sum(kv)}/{len(kv)}", "estimate": est,
               "ci95_boot": (lo, hi), "threshold": thr}
        out.append(_reading(label, decide(est, (lo, hi), thr), recorded, inp))
        if _degenerate((lo, hi)):
            cp = cp_rate_diff([(sum(av), len(av))], [(sum(kv), len(kv))])
            inp2 = dict(inp, ci95_boot_DEGENERATE=True, ci95_clopper_pearson=cp,
                        cp_A=clopper_pearson(sum(av), len(av)), cp_K=clopper_pearson(sum(kv), len(kv)))
            out.append(_reading(label + "+CP_fallback", decide(est, cp, thr), recorded, inp2,
                                "bootstrap CI has zero width; per-group 95% Clopper-Pearson, interval arithmetic"))
    return out


def shadow(model):
    rows, key, summ, checks = per_item(model)
    _int_keys(rows, ("t1_score", "behav_score"))
    sub = subsets(key)
    G = {}
    for r in rows.values():                                   # sorted sid order, as analyze
        G.setdefault(r["group"], []).append(r)
    g = lambda k: G.get(k, [])
    incomp = [r for k in S.INCOMP for r in g(k)]
    A, AADV, K = g("A"), g("AADV"), g("K")
    Aall = A + AADV
    A_sets = [("A=standard(32)", A), ("A=all aliens(40)", Aall)]
    Hrec = summ.get("hypotheses", {})
    rec = lambda h: (Hrec.get(h) or {}).get("decision")
    H = {}

    # H1 -------------------------------------------------------------------------
    for hname, fld in (("H1_t1", "t1_score"), ("H1_behav", "behav_score")):
        f = lambda r, fld=fld: r.get("_k_" + fld)
        out = []
        for label, AA in A_sets:
            kk = [r for r in K if f(r) is not None]
            aa = [r for r in AA if f(r) is not None]
            nn = [r for r in incomp if f(r) is not None]
            if not (kk and aa and nn):
                out.append(_reading(label, "NOT_ELIGIBLE", rec(hname), {"n_K": len(kk), "n_A": len(aa), "n_N": len(nn)}))
                continue
            def stat(k_, a_, n_):
                nv = [f(r) for r in n_]
                return auc_exact([f(r) for r in k_], nv) - auc_exact([f(r) for r in a_], nv)
            est = stat(kk, aa, nn)
            lo, hi, nd = boot([kk, aa, nn], stat)
            inp = {"AUC_K": auc_exact([f(r) for r in kk], [f(r) for r in nn]),
                   "AUC_A": auc_exact([f(r) for r in aa], [f(r) for r in nn]),
                   "estimate": est, "ci95_boot": (lo, hi), "threshold": THR["H1"]}
            if _degenerate((lo, hi)):
                inp["ci95_boot_DEGENERATE"] = True
            out.append(_reading(label, decide(est, (lo, hi), THR["H1"]), rec(hname), inp))
        H[hname] = out

    # H2 / H5 ----------------------------------------------------------------------
    false_neg = lambda r: (int(r.get("t1_verdict") == "RANDOM" or r.get("coherence") == "INCOHERENT")
                           if "t1_verdict" in r or "coherence" in r else None)
    collapse = lambda r: int(r["analogy_class"] == "FALSE_COLLAPSE_TO_FAMILIAR") if "analogy_class" in r else None
    H["H2"] = _rate_hyp("H2", false_neg, A_sets, K, THR["H2"], rec("H2"))
    H["H5"] = _rate_hyp("H5", collapse, A_sets, K, THR["H5"], rec("H5"))

    # H3 -------------------------------------------------------------------------
    act = [rows[s] for s in sub["active"] if "active_learned" in rows[s]]
    aa = [r for r in act if r["group"] == "A"]
    kk = [r for r in act if r["group"] == "K"]
    if aa and kk:
        pl = lambda rs: F(sum(int(r.get("learned", False)) for r in rs), len(rs))
        al = lambda rs: F(sum(int(r["active_learned"]) for r in rs), len(rs))
        gp, ga = pl(kk) - pl(aa), al(kk) - al(aa)
        d = gp - ga
        H["H3"] = [_reading("prereg_s6_H3 (exact)", "SUPPORTED" if d >= THR["H3"] else "INDETERMINATE", rec("H3"),
                            {"K_passive": pl(kk), "A_passive": pl(aa), "K_active": al(kk), "A_active": al(aa),
                             "gap_passive": gp, "gap_active": ga, "diff": d, "threshold": THR["H3"],
                             "float_diff_as_frozen": (float(pl(kk)) - float(pl(aa))) - (float(al(kk)) - float(al(aa)))})]
    else:
        H["H3"] = [_reading("prereg_s6_H3 (exact)", "NOT_ELIGIBLE", rec("H3"), {"n_A": len(aa), "n_K": len(kk)})]

    # H4: s6 general rule (bootstrap), predicate readings, CP fallback ----------------
    rv = [rows[s] for s in sub["reveal"] if "reveal_coherence" in rows[s]]
    ra = [r for r in rv if r["group"] == "A"]
    rk = [r for r in rv if r["group"] == "K"]
    preds = [
        ("code_predicates (blind RANDOM|INCOHERENT; reveal INCOHERENT|UNCLEAR)",
         false_neg, lambda r: int(r["reveal_coherence"] in ("INCOHERENT", "UNCLEAR"))),
        ("unified_strict (both: RANDOM|INCOHERENT / INCOHERENT)",
         false_neg, lambda r: int(r["reveal_coherence"] == "INCOHERENT")),
        ("unified_incl_unclear (both include UNCLEAR)",
         lambda r: (int(r.get("t1_verdict") == "RANDOM" or r.get("coherence") in ("INCOHERENT", "UNCLEAR"))
                    if "t1_verdict" in r or "coherence" in r else None),
         lambda r: int(r["reveal_coherence"] in ("INCOHERENT", "UNCLEAR"))),
    ]
    out = []
    for label, bfn, rfn in preds:
        a_ = [r for r in ra if bfn(r) is not None]
        k_ = [r for r in rk if bfn(r) is not None]
        if not a_ or not k_:
            out.append(_reading(label, "NOT_ELIGIBLE", rec("H4"), {"n_A": len(a_), "n_K": len(k_)}))
            continue
        mean = lambda rs, fn: F(sum(fn(r) for r in rs), len(rs))
        stat = lambda A_, K_: (mean(A_, bfn) - mean(K_, bfn)) - (mean(A_, rfn) - mean(K_, rfn))
        est = stat(a_, k_)
        lo, hi, nd = boot([a_, k_], stat)
        cnt = lambda rs, fn: (sum(fn(r) for r in rs), len(rs))
        inp = {"A_blind": "%d/%d" % cnt(a_, bfn), "K_blind": "%d/%d" % cnt(k_, bfn),
               "A_reveal": "%d/%d" % cnt(a_, rfn), "K_reveal": "%d/%d" % cnt(k_, rfn),
               "estimate": est, "ci95_boot": (lo, hi), "threshold": THR["H4"]}
        out.append(_reading("s6_rule/" + label, decide(est, (lo, hi), THR["H4"]), rec("H4"), inp))
        # the frozen code's own rule form, exact (est >= thr else INDETERMINATE)
        out.append(_reading("code_rule_form_exact/" + label,
                            "SUPPORTED" if est >= THR["H4"] else "INDETERMINATE", rec("H4"), {"estimate": est},
                            "not the PREREG s6 rule (AUDIT_A F02); shown for reference"))
        if _degenerate((lo, hi)):
            cp = cp_rate_diff([cnt(a_, bfn), cnt(k_, rfn)], [cnt(k_, bfn), cnt(a_, rfn)])
            out.append(_reading("s6_rule+CP_fallback/" + label, decide(est, cp, THR["H4"]), rec("H4"),
                                dict(inp, ci95_boot_DEGENERATE=True, ci95_clopper_pearson=cp),
                                "four per-group 95% CP intervals, interval arithmetic (conservative)"))
    H["H4"] = out

    # H6 -------------------------------------------------------------------------
    out = []
    for label, AA in (("A=all aliens(40)", Aall), ("A=standard(32)", A)):
        strict = [r["id"] for r in AA if r.get("learned") and
                  (r.get("t1_verdict") == "RANDOM" or r.get("coherence") == "INCOHERENT")]
        soft = [r["id"] for r in AA if r.get("learned") and
                (r.get("t1_verdict") in ("RANDOM", "UNCERTAIN") or r.get("coherence") in ("INCOHERENT", "UNCLEAR"))]
        n_eval = sum(1 for r in AA if "learned" in r)
        inp = {"strict_ids": strict, "soft_ids": soft, "n_aliens_scored": n_eval}
        out.append(_reading(label, "SUPPORTED" if len(strict) >= 2 else "NOT_SUPPORTED", rec("H6"), inp))
        if n_eval == 0:
            out.append(_reading(label + "+s6_eligibility", "NOT_ELIGIBLE", rec("H6"), inp,
                                "s6 'NOT_ELIGIBLE if a group is empty' applied to H6"))
    H["H6"] = out

    # Detector validation (s7) ------------------------------------------------------
    pr = S.read(model, "pair")
    pairs = []
    for a_id, n_id in sub["pairs"]:
        row = pr.get(a_id)
        if row and row.get("ok") and key[n_id]["null_type"] != "DESTROY":
            ch = str(row["parsed"].get("choice", "")).upper()
            pairs.append({"alien": a_id, "adv": bool(key[a_id].get("adversarial")), "correct": int(ch == row["lawful"])})
    drec = (summ.get("detector_validation") or {}).get("verdict")
    out = []
    t1 = lambda r: r.get("_k_t1_score")
    for label, AA, pset in (("literal_code (AUC standard A; all 30 incomp pairs)", A, pairs),
                            ("consistent_standard (standard A; 22 standard pairs)", A, [x for x in pairs if not x["adv"]]),
                            ("consistent_all (all 40 A; all 30 pairs)", Aall, pairs)):
        aa = [t1(r) for r in AA if t1(r) is not None]
        nn = [t1(r) for r in incomp if t1(r) is not None]
        auc = auc_exact(aa, nn)
        # resampling unit as frozen: rows (unfiltered), A then incomp
        lo, hi, nd = boot([AA, incomp], lambda a, b: auc_exact([t1(r) for r in a if t1(r) is not None],
                                                                  [t1(r) for r in b if t1(r) is not None])) \
            if AA and incomp else (None, None, 0)
        pacc = F(sum(x["correct"] for x in pset), len(pset)) if pset else None
        inp = {"auc": auc, "ci95_boot": (lo, hi), "pairs": f"{sum(x['correct'] for x in pset)}/{len(pset)}",
               "pair_acc": pacc, "pair_acc_cp95": clopper_pearson(sum(x["correct"] for x in pset), len(pset))}
        if _degenerate((lo, hi)):
            inp["ci95_boot_DEGENERATE"] = True
        missing = auc is None or lo is None or pacc is None
        ok = (not missing) and auc >= DET_AUC and lo >= DET_CI_LO and pacc >= DET_PAIR
        verdict = "NOVELTY_DETECTOR_VALIDATED" if ok else "NOVELTY_DETECTOR_NOT_VALIDATED"
        out.append(_reading(label, verdict, drec, inp, "s7 literal: missing leg -> NOT_VALIDATED" if missing else ""))
        if missing:
            out.append(_reading(label + "+s6_eligibility", "NOT_ELIGIBLE", drec, inp,
                                "s6 'NOT_ELIGIBLE if a group is empty' (current analyze.py behaviour)"))
    H["DETECTOR"] = out

    summary = {}
    for h, rs in H.items():
        prim = rs[0]
        summary[h] = {"recorded": prim["recorded"], "shadow_primary": prim["decision"],
                      "primary_reading": prim["label"], "DIVERGES": prim["diverges"],
                      "any_reading_diverges": any(x["diverges"] for x in rs),
                      "degenerate_ci": any(x["inputs"].get("ci95_boot_DEGENERATE") for x in rs)}
    # H4's primary is the s6-rule reading with the code's predicates (index 0)
    return {"model": model, "summary": summary, "readings": H, "per_item_checks": checks}


@lru_cache(maxsize=None)
def shadow_cached(model):
    return shadow(model)


def diverging(model):
    return sorted(h for h, s in shadow_cached(model)["summary"].items() if s["DIVERGES"])


# ---- CLI ------------------------------------------------------------------------

def _jsonable(o):
    if isinstance(o, Fraction):
        return {"exact": fmt(o), "float": float(o)}
    if isinstance(o, tuple):
        return [_jsonable(x) for x in o]
    if isinstance(o, list):
        return [_jsonable(x) for x in o]
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    return o


def _short(inp):
    parts = []
    for k, v in inp.items():
        if k in ("soft_ids",):
            continue
        if isinstance(v, tuple):
            v = "[" + ", ".join(fmt(x) if not isinstance(x, Fraction) else f"{float(x):.4f}" for x in v) + "]"
        elif isinstance(v, Fraction):
            v = f"{fmt(v)}({float(v):.4f})"
        parts.append(f"{k}={v}")
    return "; ".join(parts)


def table(res):
    lines = [f"model={res['model']}",
             f"{'HYP':9} {'RECORDED':31} {'SHADOW':31} DIV  reading / inputs"]
    for h, rs in res["readings"].items():
        for i, x in enumerate(rs):
            tag = "YES" if x["diverges"] else "no"
            lines.append(f"{h if i == 0 else '':9} {str(x['recorded']):31} {x['decision']:31} {tag:4} "
                         f"{'*' if i == 0 else ' '}{x['label']}")
            lines.append(f"{'':9} {'':31} {'':31} {'':4}   {_short(x['inputs'])}")
            if x["note"]:
                lines.append(f"{'':9} {'':31} {'':31} {'':4}   note: {x['note']}")
    lines.append("(* = primary reading: the frozen code's sets/predicates; DIVERGES in summary refers to it)")
    lines.append("per-item checks: " + json.dumps({k: (len(v), v[:5]) for k, v in res["per_item_checks"].items()}))
    lines.append("PRIMARY DIVERGES: " + (", ".join(h for h, s in res["summary"].items() if s["DIVERGES"]) or "none"))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = shadow_cached(a.model)
    print(json.dumps(_jsonable(res), indent=1) if a.json else table(res))


if __name__ == "__main__":
    main(sys.argv[1:])
