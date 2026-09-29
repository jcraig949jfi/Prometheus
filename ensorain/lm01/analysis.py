"""WTP-LM01 VERDICT ANALYSIS v0.3.2 (PREREG s6), frozen with the prereg BEFORE any campaign row exists.

v0.3.2 repairs, each identified before any campaign result (review ensorain/arc3/reviews/LM01_ADVERSARIAL_REVIEW.md;
operator amendment 2026-09-28): the gates live HERE, not in a post-run addendum. The v0.3.1 file is preserved at
ensorain/lm01/archive_v031/analysis.py.

All comparisons use the paired per-world difference with a 90% t-interval over worlds:
  WIN(x > y)  <=> CI(x - y).lo > +DELTA ;  EQUIVALENT <=> -DELTA < CI.lo and CI.hi < +DELTA ;  else unresolved.
Gates, in order, per stratum (the dev TESTABLE frame comes from margins_reduced_v2.json and is unchanged):
  G1 HEADLINE-PAIR LEARNABILITY: CI.lo(L-R - N1) > DELTA on the campaign rows, else the headline reads
     UNTESTED_HEADLINE_NOT_LEARNABLE. Any equivalence reading also needs CI.lo(rung - N1) > 0.
  HPC HEADLINE POSITIVE CONTROL (dev fixture, per level): if the planted "retention must pay" world does not fire
     EXACT_RETENTION_PAYS at that level, a non-firing headline reads UNRESOLVED_INSTRUMENT_CANNOT_FIRE.
  E6 EVICTION POSITIVE CONTROL on the CAMPAIGN rows: CI.lo(oracle - random) > DELTA, else EVERY 6.3 label is
     UNRESOLVED_E6 (prose s7).
  G5 HEADROOM per eviction point B: CI.lo(random@full - random@B) > DELTA, else UNTESTED_NO_HEADROOM.
  G7 matched-HR2 readings whose interpolation clamps at the full store (majority of worlds) are UNMATCHED.
Readings never replace the per-stratum CURVES, which are always emitted (s6.8)."""
import json
import math
import os

import numpy as np

from .margins_reduce_v2 import ci, DELTA, SENS

HERE = os.path.dirname(__file__)
BOUNDED = ["c/8", "c/4", "c/2", "c", "2c"]
# v0.3.2 (diff #16): EXACT_RETENTION_PAYS is judged against the genuinely BOUNDED rungs, B <= c (at most one record per
# cell). 2c holds 37-73% of the history, and the headline positive control showed that including it makes the WIN rule
# unable to fire even where retention must pay (dev/fixtures_v032.json). 2c is still measured, reported, and used for
# B*/NULL.
WIN_RUNGS = ["c/8", "c/4", "c/2", "c"]
REP_CAP = 64
Z95, Z80, Z90 = 1.645, 0.842, 1.282


def _win(c, d):
    return c is not None and c["lo"] > d


def _eq(c, d):
    return c is not None and -d < c["lo"] and c["hi"] < d


def _paired(rows, fa, fb):
    v = []
    for r in rows:
        a, b = fa(r), fb(r)
        if a is not None and b is not None:
            v.append(a - b)
    return ci(v)


def _lad(r, key):
    x = r.get("ladder", {}).get(key)
    return None if x is None else x.get("AC")


def _n_rep(c, kind, d):
    """Replication block from THIS reading's own paired SD (review F9). win: one-sided 80% power at a true effect of
    2 x DELTA; equivalence: TOST with a true difference of 0 at 80% power."""
    if c is None or not c.get("sd"):
        return None
    z = (Z95 + Z80) if kind == "win" else (Z95 + Z90)
    return max(8, math.ceil((z * c["sd"] / d) ** 2))


def _rep_status(c, kind, d):
    n = _n_rep(c, kind, d)
    return dict(n_rep=n, status=("UNREPLICATED" if (n is None or n > REP_CAP) else f"PENDING_REPLICATION(n={n})"))


def curves(ok):
    """s6.8: the reservoir/capacity curves and per-arm resource loci, always emitted."""
    keys = sorted({k for r in ok for k in r.get("ladder", {})})
    out = {}
    for k in keys:
        v = [r["ladder"][k] for r in ok if k in r["ladder"]]
        c = ci([x["AC"] for x in v])
        med = lambda f: float(np.median([f(x) for x in v]))
        out[k] = dict(AC=c, B_frac=med(lambda x: x.get("B_frac", 1.0)),
                      HR2=(med(lambda x: x["HR2"]) if all("HR2" in x for x in v) else None),
                      stored_record_bytes=med(lambda x: x["loci"]["stored_record_bytes"]) if all("loci" in x for x in v) else None,
                      hypothesis_bytes=med(lambda x: x["loci"]["hypothesis_bytes"]) if all("loci" in x for x in v) else None,
                      transient_hypothesis_bytes=med(lambda x: x["loci"]["transient_hypothesis_bytes"]) if all("loci" in x for x in v) else None,
                      record_reads=med(lambda x: x["meter"]["record_reads"]),
                      query_ops=med(lambda x: x["meter"]["query_ops"]),
                      fit_ops=med(lambda x: x["meter"]["ops"] - x["meter"]["query_ops"]))
    return out


def headline(ok, d, hpc_pass):
    lr = lambda r: _lad(r, "L-R|full")
    warm = lambda r: _lad(r, "random|full")
    out = dict(G1_LR_minus_N1=_paired(ok, lr, lambda r: r.get("N1")))
    if not _win(out["G1_LR_minus_N1"], d):
        out["label"] = "UNTESTED_HEADLINE_NOT_LEARNABLE"
        return out
    rungs = [g for g in BOUNDED if sum(f"random|{g}" in r.get("ladder", {}) for r in ok) >= 3]
    diffs = {g: _paired(ok, lr, lambda r, g=g: _lad(r, f"random|{g}")) for g in rungs}
    wdiffs = {g: _paired(ok, warm, lambda r, g=g: _lad(r, f"random|{g}")) for g in rungs}
    above_floor = {g: (c := _paired(ok, lambda r, g=g: _lad(r, f"random|{g}"), lambda r: r.get("N1"))) is not None
                   and c["lo"] > 0 for g in rungs}
    out.update(LR_minus_rung=diffs, warm_minus_rung=wdiffs, endpoints_warm_minus_LR=_paired(ok, warm, lr),
               suffstat_minus_LR=_paired(ok, lambda r: _lad(r, "SUFFSTAT|table"), lr))   # R2: reported only

    def bstar(dd):                       # monotone: the smallest rung from which ALL larger rungs are EQUIVALENT
        for i, g in enumerate(rungs):
            if all(_eq(dd[h], d) and above_floor[h] for h in rungs[i:]):
                return g
        return None
    out["B_star_LR"], out["B_star_warm"] = bstar(diffs), bstar(wdiffs)
    win_rungs = [g for g in rungs if g in WIN_RUNGS]
    # pre-freeze review R1: every bounded rung in the WIN rule must itself be above the N1 floor (the same condition
    # as the sufficiency readings), so "retention pays" cannot be read against broken bounded arms
    pays = bool(win_rungs) and all(_win(diffs[g], d) and above_floor[g] for g in win_rungs)
    # pre-freeze review R3: the v0.3.1 comparison set (every rung incl. 2c, no floor), a DESCRIPTIVE column only
    out["v031_set_label"] = ("EXACT_RETENTION_PAYS" if rungs and all(_win(diffs[g], d) for g in rungs)
                             else "not_firing")
    lk_eq = _eq(_paired(ok, lambda r: r["arms"]["L-K"]["AC"], lr), d)
    if pays:
        out["label"] = "COUNTERMODEL_SIGNAL" if lk_eq else "LOSSLESS_TRANSIENT_CONTRACTION"
        out["replication"] = _rep_status(min((diffs[g] for g in win_rungs), key=lambda c: c["lo"]), "win", d)
    elif not hpc_pass:
        out["label"] = "UNRESOLVED_INSTRUMENT_CANNOT_FIRE"
    else:
        out["label"] = "UNRESOLVED"
    out["reported"] = "BOUNDED_SUFFICES" if out["B_star_LR"] is not None else None
    out["all_rungs_equivalent_to_LR"] = bool(rungs) and all(_eq(diffs[g], d) and above_floor[g] for g in rungs)
    return out


def secondary(ok, d):
    """6.2 (optimizer confounded). ELIGIBILITY (v0.3.2, review F6): a SELECTIVE ladder point is eligible iff, in the
    majority of worlds, its persistent bytes <= the frozen LOSSLESS arm's AND its record_reads (the common convention)
    <= the LOSSLESS arm's. The same eligibility is used for SELECTIVE_ADVANTAGE and for the secondary COUNTERMODEL."""
    rows = [r for r in ok if "SELECTIVE_LADDER" in r["arms"] and "LOSSLESS" in r["arms"]]
    if not rows:
        return dict(label="UNRESOLVED", reason="no ladder")
    L = lambda r: r["arms"]["LOSSLESS"]
    caps = sorted({c for r in rows for c, v in r["arms"]["SELECTIVE_LADDER"]["ladder"].items() if "AC" in v}, key=int)
    res, elig = {}, []
    for c in caps:
        rr = [r for r in rows if "AC" in r["arms"]["SELECTIVE_LADDER"]["ladder"].get(c, {})]
        if len(rr) < 3:
            continue
        pt = lambda r: r["arms"]["SELECTIVE_LADDER"]["ladder"][c]
        within = np.mean([pt(r)["meter"]["peak_persistent"] <= L(r)["meter"]["peak_persistent"]
                          and pt(r)["meter"]["record_reads"] <= L(r)["meter"]["record_reads"] for r in rr]) >= 0.5
        dd = _paired(rr, lambda r: pt(r)["AC"], lambda r: L(r)["AC"])
        res[c] = dict(S_minus_L=dd, eligible=bool(within))
        if within:
            elig.append(c)
    lab, rep = "UNRESOLVED", None
    wins = [c for c in elig if _win(res[c]["S_minus_L"], d)]
    if wins:
        lab = "SELECTIVE_ADVANTAGE"
        rep = _rep_status(max((res[c]["S_minus_L"] for c in wins), key=lambda c: c["lo"]), "win", d)
    elif elig and all(res[c]["S_minus_L"] is not None and res[c]["S_minus_L"]["hi"] < -d for c in elig):
        lab = "LOSSLESS_TRANSIENT_CONTRACTION" if rows[0]["arms"]["LOSSLESS"]["label"].startswith("L-R") else "COUNTERMODEL_SIGNAL"
    return dict(label=lab, caps=res, replication=rep, note="confounded: optimizer (SGD vs ALS), model class, regularization, tuning point; never gates a falsifier")


def e6_campaign(ok, d):
    c = _paired([r for r in ok if r.get("posctl")], lambda r: r["posctl"].get("oracle"), lambda r: r["posctl"].get("random"))
    return dict(ci=c, pass_=_win(c, d))


def eviction(ok, d, e6_pass):
    """6.3 v0.3.2 (review F7): the two declared candidates are SURPRISE-DRIVEN heuristics (keep_worst,
    residual_reservoir), read against random AND the FIFO recency reference."""
    ev = sorted({k.split("|")[0] for r in ok for k in r.get("ladder", {})} - {"random", "L-R", "fifo", "SUFFSTAT"})
    if not ev:
        return dict(label="UNRESOLVED", reason="no eviction candidate", at={})
    e = ev[0]
    out = dict(candidate=e, at={})
    for g in ("c/4", "c"):
        if not any(f"{e}|{g}" in r.get("ladder", {}) for r in ok):
            continue
        room = _paired(ok, lambda r: _lad(r, "random|full"), lambda r, g=g: _lad(r, f"random|{g}"))
        i = _paired(ok, lambda r: _lad(r, f"{e}|{g}"), lambda r: _lad(r, f"random|{g}"))
        f = _paired(ok, lambda r: _lad(r, f"{e}|{g}"), lambda r: _lad(r, f"fifo|{g}"))
        clamp = [r["dual"][g].get("clamped", False) for r in ok if g in r.get("dual", {})]
        unmatched = bool(clamp) and np.mean(clamp) > 0.5
        ii = None if unmatched else _paired(ok, lambda r: _lad(r, f"{e}|{g}"),
                                           lambda r: (float(np.mean([x["AC"] for x in r["dual"][g]["runs"]]))
                                                      if g in r.get("dual", {}) else None))
        if not e6_pass:
            lab = "UNRESOLVED_E6"
        elif not _win(room, d):
            lab = "UNTESTED_NO_HEADROOM"
        elif _win(i, d) and not _win(f, d):
            lab = "RECENCY"                                   # beats random but not the recency reference
        elif _win(i, d) and _win(ii, d):
            lab = "HEURISTIC_ADVANTAGE"
        elif _win(i, d):
            lab = "HEURISTIC_BUYS_BYTES" if ii is not None else "UNRESOLVED_UNMATCHED"
        elif i is not None and i["hi"] < -d:
            # pre-freeze review (recommended): symmetric recency attribution. If the heuristic loses to random but is
            # EQUIVALENT to the FIFO recency reference, and random also beats FIFO, the loss is attributed to recency
            fr = _paired(ok, lambda r: _lad(r, f"fifo|{g}"), lambda r: _lad(r, f"random|{g}"))
            lab = "RECENCY_LOSES" if (_eq(f, d) and fr is not None and fr["hi"] < -d) else "RANDOM_BEATS_HEURISTIC"
        elif _eq(i, d) and _eq(ii, d):
            lab = "HEURISTIC_EQUIVALENT_TO_RANDOM"
        else:
            lab = "UNRESOLVED"
        rep = None
        if lab in ("HEURISTIC_ADVANTAGE", "RANDOM_BEATS_HEURISTIC"):
            rep = _rep_status(i, "win", d)
        elif lab == "HEURISTIC_EQUIVALENT_TO_RANDOM":
            rep = _rep_status(i, "tost", d)
        out["at"][g] = dict(headroom=room, matched_B=i, matched_HR2=ii, vs_fifo=f, unmatched=unmatched, label=lab,
                            replication=rep)
    labs = [a["label"] for a in out["at"].values()]
    out["label"] = labs[0] if len(set(labs)) == 1 else "MIXED:" + "/".join(labs)
    return out


def hybrid(ok, d, abl_pc_pass):
    g = ci([r["arms"]["HYBRID"]["ablation"]["gap"] for r in ok if "HYBRID" in r["arms"]])
    if _win(g, d):
        lab = "HYBRID_REQUIRED"
    elif _eq(g, d) and abl_pc_pass:
        lab = "INDEX_NOT_REQUIRED"
    else:
        lab = "UNRESOLVED"
    return dict(gap=g, label=lab)


def f1_trigger(ok, d):
    """Branch trigger (F1): L-K vs the SELECTIVE ladder point nearest cap = cells/4 (review F12: fixed cap, not a
    per-world max)."""
    def s_ac(r):
        lad = r["arms"].get("SELECTIVE_LADDER", {}).get("ladder", {})
        caps = [int(c) for c, v in lad.items() if "AC" in v]
        if not caps:
            return None
        target = int(r.get("cells", 0)) // 4
        c = min(caps, key=lambda x: abs(x - target)) if target else sorted(caps)[len(caps) // 2]
        return lad[str(c)]["AC"]
    return _win(_paired(ok, lambda r: r["arms"]["L-K"]["AC"], s_ac), d)


def stratum(rows, dev, d, key_family=None, fixtures=None):
    fixtures = fixtures or {}
    ok = [r for r in rows if r.get("status") == "OK"]
    level = ok[0]["level"] if ok else None
    cur = curves(ok) if ok else {}
    if dev.get("frame") != "TESTABLE":
        return dict(label="UNTESTED", reason="dev gate (TABLES)", curves=cur)
    if key_family == "F1_episodic":
        must = f1_trigger(ok, d)
        return dict(n=len(ok), role="F1_BRANCH_TRIGGER (exact-hit; never headline, never a firing or support)",
                    lossless_must_win=must, instrument=("OK" if must else "INSTRUMENT_FAILURE"), firings=[],
                    supports_pending_replication=[], curves=cur)
    hpc = fixtures.get("headline_pc", {}).get(level, False)
    e6 = e6_campaign(ok, d)
    h = headline(ok, d, hpc)
    s = secondary(ok, d)
    e = eviction(ok, d, e6["pass_"])
    y = hybrid(ok, d, fixtures.get("ablation_pc", False))
    null = (h.get("label") in ("UNRESOLVED", "UNRESOLVED_INSTRUMENT_CANNOT_FIRE") and h.get("all_rungs_equivalent_to_LR")
            and hpc)
    firings = []
    if h.get("label") == "COUNTERMODEL_SIGNAL":
        firings.append(dict(falsifier="F-B", replication=h.get("replication")))
    for g, a in e.get("at", {}).items():
        if a["label"] in ("HEURISTIC_EQUIVALENT_TO_RANDOM", "RANDOM_BEATS_HEURISTIC"):
            firings.append(dict(falsifier=f"F-C@{g}:{a['label']} (scope: surprise-driven retention)",
                                replication=a["replication"]))
    supports = []
    if s["label"] == "SELECTIVE_ADVANTAGE":
        supports.append(dict(label="SELECTIVE_ADVANTAGE", replication=s["replication"]))
    for g, a in e.get("at", {}).items():
        if a["label"] == "HEURISTIC_ADVANTAGE":
            supports.append(dict(label=f"HEURISTIC_ADVANTAGE@{g}", replication=a["replication"]))
    return dict(n=len(ok), headline=h, secondary=s, eviction=e, e6_campaign=e6, e6_dev=dev.get("posctl_pass"),
                e6_disagreement=bool(e6["pass_"]) != bool(dev.get("posctl_pass")), hybrid=y, NULL=bool(null),
                firings=firings, supports_pending_replication=supports, visits_per_cell=dev.get("visits_per_cell"),
                curves=cur)


def analyse(campaign_dir, dev_path=os.path.join(HERE, "dev", "margins_reduced_v2.json"),
            fixtures_path=os.path.join(HERE, "dev", "fixtures_v032.json")):
    dev = json.load(open(dev_path))
    if not os.path.exists(fixtures_path):                  # pre-freeze review R4: fail loudly, never silently
        raise FileNotFoundError(f"LM01: frozen fixtures file missing: {fixtures_path}")
    fixtures = json.load(open(fixtures_path))
    res = {}
    for key, dv in dev.items():
        fn = os.path.join(campaign_dir, key.replace("|", "__") + ".jsonl")
        rows = [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []
        res[key] = {str(DELTA): stratum(rows, dv, DELTA, key.split("|")[0], fixtures)}
        for sd in SENS:                                    # descriptive only; each delta's own dev frame (review F15f)
            dvs = dict(dv, frame=dv.get("sensitivity", {}).get(str(sd), {}).get("frame", dv.get("frame")))
            res[key][str(sd)] = stratum(rows, dvs, sd, key.split("|")[0], fixtures)
    gov = {k: v[str(DELTA)] for k, v in res.items()}
    GATE = ("UNTESTED", "UNRESOLVED_E6", "UNTESTED_NO_HEADROOM", "UNRESOLVED_INSTRUMENT_CANNOT_FIRE",
            "UNTESTED_HEADLINE_NOT_LEARNABLE", "UNRESOLVED_UNMATCHED")
    live = lambda lab: lab is not None and not str(lab).startswith(GATE)     # review: aggregate live readings only
    tested = [k for k, v in gov.items() if v.get("label") != "UNTESTED" and not k.startswith("F1_episodic")]
    mult = {}
    for lab, get in (("COUNTERMODEL_SIGNAL", lambda v: v["headline"].get("label")),
                     ("LOSSLESS_TRANSIENT_CONTRACTION", lambda v: v["headline"].get("label")),
                     ("SELECTIVE_ADVANTAGE", lambda v: v["secondary"]["label"]),
                     ("HYBRID_REQUIRED", lambda v: v["hybrid"]["label"])):
        lv = [k for k in tested if live(get(gov[k]))]
        fired = [k for k in lv if get(gov[k]) == lab]
        mult[lab] = dict(readings=len(lv), fired=len(fired), expected_by_chance=round(0.05 * len(lv), 2), strata=fired)
    for lab in ("HEURISTIC_EQUIVALENT_TO_RANDOM", "RANDOM_BEATS_HEURISTIC", "HEURISTIC_ADVANTAGE", "RECENCY",
                "HEURISTIC_BUYS_BYTES"):
        pts = [(k, g) for k in tested for g, a in gov[k]["eviction"].get("at", {}).items() if a["label"] == lab]
        n_pts = sum(1 for k in tested for a in gov[k]["eviction"].get("at", {}).values() if live(a["label"]))
        mult[lab] = dict(readings=n_pts, fired=len(pts), expected_by_chance=round(0.05 * n_pts, 2), points=pts)
    agg = {"headline": {}, "eviction@c/4": {}, "eviction@c": {}, "secondary": {}, "hybrid": {}}
    for k in tested:
        f, l, g = k.split("|")
        v = gov[k]
        agg["headline"].setdefault(f"{f}|{l}", {})[g] = v["headline"].get("label")
        agg["secondary"].setdefault(f"{f}|{l}", {})[g] = v["secondary"]["label"]
        agg["hybrid"].setdefault(f"{f}|{l}", {})[g] = v["hybrid"]["label"]
        for pt in ("c/4", "c"):
            a = v["eviction"].get("at", {}).get(pt)
            if a:
                agg[f"eviction@{pt}"].setdefault(f"{f}|{l}", {})[g] = a["label"]
    gen_dep = {}
    for r, m in agg.items():
        gen_dep[r] = {}
        for fl, x in m.items():
            lv = {g: lab for g, lab in x.items() if live(lab)}
            gen_dep[r][fl] = ("NO_LIVE_READING" if not lv else
                              ("GENERATOR_DEPENDENT" if len(set(lv.values())) > 1 else list(lv.values())[0]))
    cross = {}
    for k in tested:
        f, l, g = k.split("|")
        cross.setdefault(f"{f}|{g}", {})[l] = gov[k]["headline"].get("label")
    crossover = {k: v for k, v in cross.items() if len({x for x in v.values() if live(x)}) > 1}
    instr = [k for k, v in gov.items() if v.get("instrument") == "INSTRUMENT_FAILURE"]
    return dict(per_stratum=res, multiplicity=mult, aggregation=gen_dep, CROSSOVER=crossover,
                INSTRUMENT_FAILURE=instr, delta=DELTA, sensitivity=list(SENS), fixtures=fixtures)
