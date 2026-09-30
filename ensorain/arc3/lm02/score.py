"""LM02 assay scorer: the preregistered verdict rules (PREREG_LM02_ASSAY.md s5), applied to results/lm02_assay.json.
Written and committed BEFORE the evaluation run. Prints the tables and the verdicts; writes results/lm02_verdict.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from ensorain.arc3.lm02.assay import (REGIMES, WINDOWS, SUBSTRATES, CHEAP, ANOM_MARGIN, PRES_AC, PRES_TAU, PRES_CONTAM,
                                      P_MAX, kendall, ANOM_BAND)

HERE = os.path.dirname(__file__)
WNAMES = [f"WINDOW_{round(1 / f)}" for f in WINDOWS]
SAFE_CONTEXTS = ("STAT", "DIFFUSE", "LOCAL_BLOCK", "LOCAL_BOX", "MODE_SLAB")   # large unchanged populations exist


def pooled(acs):
    return {s: float(np.mean(list(v.values()))) for s, v in acs.items()}


def conclusions(acs):
    """best pooled AC; the pooled AC vector (ordering); the WORLD-LEVEL anomaly margin: best non-cheap minus best cheap.
    (Per-substrate flags were dropped on dev seeds 9_814_3xx: a single substrate's AC moves ~.2 between noise draws.)"""
    p = pooled(acs); cheap = max(p[c] for c in CHEAP)
    return max(p.values()), [p[s] for s in SUBSTRATES], max(p[s] for s in SUBSTRATES if s not in CHEAP) - cheap


def consensus(row):
    """Mean pooled AC per substrate over REF1-3 -> (best, vector, anomaly margin)."""
    P = [pooled(row["pol"][k]["AC"]) for k in ("REF1", "REF2", "REF3")]
    c = {s: float(np.mean([p[s] for p in P])) for s in SUBSTRATES}; cheap = max(c[x] for x in CHEAP)
    return max(c.values()), [c[s] for s in SUBSTRATES], max(c[s] for s in SUBSTRATES if s not in CHEAP) - cheap


def preserved(row, pol):
    """anom: the world-level flag (margin > ANOM_MARGIN) agrees with the consensus; a consensus margin within ANOM_BAND
    of the threshold is ambiguous and counts as agreement."""
    bR, vR, mR = consensus(row); r = row["pol"][pol]; b, v, m = conclusions(r["AC"])
    amb = abs(mR - ANOM_MARGIN) <= ANOM_BAND
    # competence vs the ATTAINABLE level from this history (max of FULL, ORACLE; REF_HOLD is scored vs REF consensus).
    # The gap attainable -> REF is data availability, reported separately, never charged to the memory policy.
    att = bR if pol.startswith("REF") else max(conclusions(row["pol"][q]["AC"])[0] for q in ("FULL", "ORACLE"))
    c = dict(comp=bool(b >= att - PRES_AC), ord=bool(kendall(v, vR) >= PRES_TAU),
             anom=bool(amb or ((m > ANOM_MARGIN) == (mR > ANOM_MARGIN))), contam=bool(r["contam"] <= PRES_CONTAM))
    c["all"] = all(c.values()); return c


def best_split(acs, split):
    return max(v.get(split, np.nan) for v in acs.values())


def main():
    rows = json.load(open(os.path.join(HERE, "results", "lm02_assay.json")))["rows"]
    by = {rg: [r for r in rows if r["regime"] == rg] for rg in REGIMES}
    pols = ["REF_HOLD", "FULL", "ORACLE"] + WNAMES + ["STRICT_det", "STRICT_orc", "HIER_det", "HIER_orc", "POPG_det", "HIER_det_p05", "HIER_det_p20"]
    V = {}
    # ---- preservation table
    rate = {p: {rg: sum(preserved(r, p)["all"] for r in by[rg]) for rg in REGIMES} for p in pols}
    print("preserved worlds of 8 (best >= attainable - %.2f; tau >= %.2f and world anomaly flag vs REF1-3 consensus; contam <= %.2f)" % (PRES_AC, PRES_TAU, PRES_CONTAM))
    print("%-14s" % "policy" + "".join("%-12s" % rg for rg in REGIMES))
    for p in pols:
        print("%-14s" % p + "".join("%-12d" % rate[p][rg] for rg in REGIMES))
    comp = {p: {k: sum(preserved(r, p)[k] for r in rows) for k in ("comp", "ord", "anom", "contam")} for p in pols}
    print("component passes over all %d worlds:" % len(rows), json.dumps(comp))
    # ---- instrument control
    ref2 = sum(rate["REF_HOLD"].values()) / len(rows); V["instrument_REF_HOLD_rate"] = ref2
    V["INSTRUMENT"] = "OK" if ref2 >= 0.90 else "INSTRUMENT_NOISY"
    # ---- window verdict
    ok = {p: all(rate[p][rg] >= 6 for rg in REGIMES) for p in WNAMES}
    adj = any(ok[WNAMES[i]] and ok[WNAMES[i + 1]] for i in range(len(WNAMES) - 1))
    reach = {rg: max(rate[p][rg] for p in WNAMES) >= 6 for rg in REGIMES}
    bestw = {rg: max(WNAMES, key=lambda p: (rate[p][rg], -WNAMES.index(p))) for rg in REGIMES}
    if adj:
        V["WINDOW"] = "WINDOW_SUFFICIENT"
    elif sum(reach.values()) >= 9 and len({bestw[rg] for rg in REGIMES if reach[rg]}) > 1:
        V["WINDOW"] = "WINDOW_REGIME_DEPENDENT"
    else:
        V["WINDOW"] = "WINDOW_NOT_SUPPORTED"
    V["window_reach"] = reach; V["best_window"] = bestw
    # ---- population evidence
    def recov(rg):
        xs = []
        for r in by[rg]:
            s_, h_ = (best_split(r["pol"][p]["AC"], "STALE") for p in ("STRICT_det", "HIER_det"))
            R_ = float(np.mean([best_split(r["pol"][k]["AC"], "STALE") for k in ("REF1", "REF2", "REF3")]))
            if np.isfinite(R_ - s_) and R_ - s_ > 0.05:
                xs.append((h_ - s_) / (R_ - s_))
        return (float(np.mean(xs)) if xs else None), len(xs)
    V["hier_recovery"] = {rg: recov(rg) for rg in REGIMES}
    ff = {}
    for rg in REGIMES:
        for p in ("HIER_det", "POPG_det", "HIER_det_p05", "HIER_det_p20", "HIER_orc"):
            n_ = sum(r["pol"][p]["labels"]["POPULATION_SUPPORTED"]["n"] for r in by[rg]); st = sum(r["pol"][p]["labels"]["POPULATION_SUPPORTED"]["stale"] for r in by[rg])
            ff.setdefault(p, {})[rg] = (st, n_, round(st / n_, 4) if n_ else None)
    V["pop_false_freshness"] = ff
    stat_rec = V["hier_recovery"]["STAT"][0]
    value = stat_rec is not None and stat_rec >= 0.5
    safe_all = all((x[2] is None or x[2] <= P_MAX) for x in ff["HIER_det"].values())
    safe_easy = all((ff["HIER_det"][rg][2] is None or ff["HIER_det"][rg][2] <= P_MAX) for rg in REGIMES if rg != "HIDDEN")
    if value and safe_all:
        V["POP"] = "POPULATION_EVIDENCE_ADDS_VALUE"
    elif value and safe_easy:
        V["POP"] = "POP_VALUE_REQUIRES_REPRESENTATIVENESS (falsified by HIDDEN)"
    elif value:
        V["POP"] = "POP_UNSAFE (stale-risk bound exceeded outside HIDDEN)"
    else:
        V["POP"] = "POP_NO_VALUE"
    # ---- gradual drift: detector placement vs window policy
    V["ramp_readings"] = {rg: {p: rate[p][rg] for p in ("STRICT_det", "STRICT_orc", "HIER_det", "HIER_orc") + tuple(WNAMES)} for rg in ("RAMP05", "RAMP20", "RAMP50")}
    # ---- descriptive per-regime means
    desc = {}
    for rg in REGIMES:
        desc[rg] = {p: dict(contam=round(np.mean([r["pol"][p]["contam"] for r in by[rg]]), 4),
                            retained=round(np.mean([r["pol"][p]["retained"] for r in by[rg]]), 4),
                            unnec_quar=round(np.mean([r["pol"][p]["unnec_quar"] for r in by[rg]]), 4),
                            best=round(np.mean([conclusions(r["pol"][p]["AC"])[0] for r in by[rg]]), 3),
                            stale_best=round(float(np.nanmean([best_split(r["pol"][p]["AC"], "STALE") for r in by[rg]])), 3))
                    for p in ["REF1"] + pols}
    V["describe"] = desc; V["rate"] = rate
    V["data_availability_loss"] = {rg: round(float(np.mean([consensus(r)[0] - max(conclusions(r["pol"][q]["AC"])[0] for q in ("FULL", "ORACLE")) for r in by[rg]])), 3) for rg in REGIMES}
    print(json.dumps({k: V[k] for k in ("INSTRUMENT", "instrument_REF_HOLD_rate", "WINDOW", "POP", "hier_recovery", "best_window", "window_reach")}, indent=1, default=str))
    print("POP false freshness (stale, n, frac) HIER_det:", json.dumps(ff["HIER_det"]))
    json.dump(V, open(os.path.join(HERE, "results", "lm02_verdict.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
