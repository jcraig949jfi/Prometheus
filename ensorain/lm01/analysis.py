"""WTP-LM01 VERDICT ANALYSIS (PREREG s6), frozen with the prereg BEFORE any campaign row exists.

Input: campaign rows per stratum (campaign.job output) + PREREG_WTP_LM01_TABLES source (dev/margins_reduced_v2.json:
TESTABLE flag, E6 positive control, N_REP). Output: per-stratum labels at the GOVERNING DELTA = 0.30, plus the same
labels at 0.15 / 0.60 (DESCRIPTIVE ONLY), aggregation, and multiplicity counts.

All comparisons use the paired per-world difference with a 90% t-interval (margins_reduce_v2.ci):
  WIN(x > y)  <=> CI(x - y).lo > +DELTA ;  EQUIVALENT <=> -DELTA < CI.lo and CI.hi < +DELTA ;  else unresolved."""
import json
import os

import numpy as np

from .margins_reduce_v2 import ci, DELTA, SENS

HERE = os.path.dirname(__file__)
BOUNDED = ["c/8", "c/4", "c/2", "c", "2c"]


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


def headline(rows, d):
    out = {}
    lr = lambda r: _lad(r, "L-R|full")
    warm = lambda r: _lad(r, "random|full")
    rungs = [g for g in BOUNDED if any(f"random|{g}" in r.get("ladder", {}) for r in rows)]
    diffs = {g: _paired(rows, lr, lambda r, g=g: _lad(r, f"random|{g}")) for g in rungs}
    out["LR_minus_rung"] = diffs
    out["warm_minus_rung"] = {g: _paired(rows, warm, lambda r, g=g: _lad(r, f"random|{g}")) for g in rungs}
    out["endpoints_warm_minus_LR"] = _paired(rows, warm, lr)
    pays = bool(rungs) and all(_win(diffs[g], d) for g in rungs)
    lk_eq = _eq(_paired(rows, lambda r: r["arms"]["L-K"]["AC"], lr), d)
    out["B_star_LR"] = next((g for g in rungs if _eq(diffs[g], d)), None)
    out["B_star_warm"] = next((g for g in rungs if _eq(out["warm_minus_rung"][g], d)), None)
    if pays:
        out["label"] = "COUNTERMODEL_SIGNAL" if lk_eq else "LOSSLESS_TRANSIENT_CONTRACTION"
    else:
        out["label"] = "UNRESOLVED"
    out["reported"] = "BOUNDED_SUFFICES" if out["B_star_LR"] is not None else None
    out["all_rungs_equivalent_to_LR"] = bool(rungs) and all(_eq(diffs[g], d) for g in rungs)
    return out


def secondary(rows, d):
    ok = [r for r in rows if "SELECTIVE_LADDER" in r["arms"] and "LOSSLESS" in r["arms"]]
    if not ok:
        return dict(label="UNRESOLVED", reason="no ladder")
    caps = sorted({c for r in ok for c, v in r["arms"]["SELECTIVE_LADDER"]["ladder"].items() if "AC" in v}, key=int)
    L = lambda r: r["arms"]["LOSSLESS"]
    elig, res = [], {}
    for c in caps:
        rr = [r for r in ok if "AC" in r["arms"]["SELECTIVE_LADDER"]["ladder"].get(c, {})]
        if not rr:
            continue
        b = np.median([r["arms"]["SELECTIVE_LADDER"]["ladder"][c]["meter"]["peak_persistent"] <= L(r)["meter"]["peak_persistent"]
                       and r["arms"]["SELECTIVE_LADDER"]["ladder"][c]["meter"]["bytes_read"] <= L(r)["meter"]["bytes_read"] for r in rr])
        dd = _paired(rr, lambda r, c=c: r["arms"]["SELECTIVE_LADDER"]["ladder"][c]["AC"], lambda r: L(r)["AC"])
        res[c] = dict(S_minus_L=dd, within_budget=bool(b >= 0.5))
        if b >= 0.5:
            elig.append(c)
    lab = "UNRESOLVED"
    if any(_win(res[c]["S_minus_L"], d) for c in elig):
        lab = "SELECTIVE_ADVANTAGE"
    elif elig and all(res[c]["S_minus_L"] is not None and res[c]["S_minus_L"]["hi"] < -d for c in elig):
        lab = "LOSSLESS_TRANSIENT_CONTRACTION" if ok[0]["arms"]["LOSSLESS"]["label"].startswith("L-R") else "COUNTERMODEL_SIGNAL"
    return dict(label=lab, caps=res, note="optimizer confounded (SGD vs ALS); never gates a falsifier")


def eviction(rows, d, posctl_pass):
    ev = sorted({k.split("|")[0] for r in rows for k in r.get("ladder", {}) if not k.startswith(("random|", "L-R|"))})
    if not ev:
        return dict(label="UNRESOLVED", reason="no eviction candidate")
    e = ev[0]
    out = dict(candidate=e, at={})
    labs = []
    for g in ("c/4", "c"):
        i = _paired(rows, lambda r: _lad(r, f"{e}|{g}"), lambda r: _lad(r, f"random|{g}"))
        ii = _paired(rows, lambda r: _lad(r, f"{e}|{g}"),
                     lambda r: (float(np.mean([x["AC"] for x in r["dual"][g]["runs"]])) if g in r.get("dual", {}) else None))
        if _win(i, d) and _win(ii, d):
            lab = "RESERVOIR_SELECTIVE_ADVANTAGE"
        elif _win(i, d):
            lab = "SELECTIVE_BUYS_BYTES"
        elif i is not None and i["hi"] < -d:
            lab = "RANDOM_BEATS_SELECTIVE"
        elif _eq(i, d) and _eq(ii, d) and posctl_pass:
            lab = "INDISCRIMINATE_EQUIVALENT"
        else:
            lab = "UNRESOLVED"
        out["at"][g] = dict(matched_B=i, matched_HR2=ii, label=lab)
        labs.append(lab)
    out["label"] = labs[0] if len(set(labs)) == 1 else "MIXED:" + "/".join(labs)
    return out


def hybrid(rows, d):
    g = ci([r["arms"]["HYBRID"]["ablation"]["gap"] for r in rows if "HYBRID" in r["arms"]])
    return dict(gap=g, label="HYBRID_REQUIRED" if _win(g, d) else "UNRESOLVED")


def stratum(rows, dev, d, key_family=None):
    ok = [r for r in rows if r.get("status") == "OK"]
    if dev.get("frame") != "TESTABLE":
        return dict(label="UNTESTED", reason="dev gate (TABLES)")
    h, s, e, y = headline(ok, d), secondary(ok, d), eviction(ok, d, dev.get("posctl_pass")), hybrid(ok, d)
    if key_family == "F1_episodic":                  # PREREG s2/s3: branch trigger on exact-hit cells; never headline
        return dict(n=len(ok), role="F1_BRANCH_TRIGGER (exact-hit; never headline, never a firing or support)",
                    headline=h, secondary=s, eviction=e, hybrid=y, firings=[], supports_pending_replication=[],
                    lossless_must_win=_win(_paired(ok, lambda r: r["arms"]["L-K"]["AC"],
                                                   lambda r: max(v["AC"] for v in r["arms"]["SELECTIVE_LADDER"]["ladder"].values()
                                                                 if "AC" in v)), d))
    null = h["all_rungs_equivalent_to_LR"] and bool(dev.get("posctl_pass"))
    firings = []
    if h["label"] == "COUNTERMODEL_SIGNAL":
        firings.append("F-B")
    # each eviction B point (c/4, c) is its own reading (PREREG 6.3/6.7): fires / supports are named with the point
    for g, a in e.get("at", {}).items():
        if a["label"] in ("INDISCRIMINATE_EQUIVALENT", "RANDOM_BEATS_SELECTIVE"):
            firings.append(f"F-C@{g}:{a['label']}")
    supports = [s["label"]] if s["label"] == "SELECTIVE_ADVANTAGE" else []
    supports += [f"RESERVOIR_SELECTIVE_ADVANTAGE@{g}" for g, a in e.get("at", {}).items()
                 if a["label"] == "RESERVOIR_SELECTIVE_ADVANTAGE"]
    return dict(n=len(ok), headline=h, secondary=s, eviction=e, hybrid=y, NULL=null, firings=firings,
                supports_pending_replication=supports, n_rep=dev.get("n_rep"), replicable=dev.get("replicable"),
                visits_per_cell=dev.get("visits_per_cell"))


def analyse(campaign_dir, dev_path=os.path.join(HERE, "dev", "margins_reduced_v2.json")):
    dev = json.load(open(dev_path))
    res = {}
    for key, dv in dev.items():
        fn = os.path.join(campaign_dir, key.replace("|", "__") + ".jsonl")
        rows = [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []
        res[key] = {str(d): stratum(rows, dv, d, key.split('|')[0]) for d in (DELTA,) + SENS}
    gov = {k: v[str(DELTA)] for k, v in res.items()}
    tested = [k for k, v in gov.items() if v.get("label") != "UNTESTED" and not k.startswith("F1_episodic")]
    mult = {}
    for lab, getter in (("COUNTERMODEL_SIGNAL", lambda v: v["headline"]["label"]),
                        ("LOSSLESS_TRANSIENT_CONTRACTION", lambda v: v["headline"]["label"]),
                        ("SELECTIVE_ADVANTAGE", lambda v: v["secondary"]["label"]),
                        ("HYBRID_REQUIRED", lambda v: v["hybrid"]["label"])):
        fired = [k for k in tested if getter(gov[k]) == lab]
        mult[lab] = dict(readings=len(tested), fired=len(fired), expected_by_chance=round(0.05 * len(tested), 2), strata=fired)
    for lab in ("INDISCRIMINATE_EQUIVALENT", "RANDOM_BEATS_SELECTIVE", "RESERVOIR_SELECTIVE_ADVANTAGE", "SELECTIVE_BUYS_BYTES"):
        pts = [(k, g) for k in tested for g, a in gov[k]["eviction"].get("at", {}).items() if a["label"] == lab]
        n_pts = sum(len(gov[k]["eviction"].get("at", {})) for k in tested)
        mult[lab] = dict(readings=n_pts, fired=len(pts), expected_by_chance=round(0.05 * n_pts, 2), points=pts)
    agg = {}
    for k in tested:
        f, l, g = k.split("|")
        agg.setdefault(f"{f}|{l}", {})[g] = gov[k]["headline"]["label"]
    gen_dep = {fl: ("GENERATOR_DEPENDENT" if len(set(v.values())) > 1 else list(v.values())[0]) for fl, v in agg.items()}
    return dict(per_stratum=res, multiplicity=mult, family_level=gen_dep, delta=DELTA, sensitivity=list(SENS))
