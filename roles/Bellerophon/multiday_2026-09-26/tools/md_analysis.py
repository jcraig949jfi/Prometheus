"""Frozen analysis for the multi-day campaign (MULTIDAY_PREREG.md s7-s9). Run ONLY after the campaign stops.

    python md_analysis.py --workdir <wd> --code <pinned code> --inputs <pinned md_inputs.json> [--replay 0.03] [--workers N]

Writes receipts/MD_RESULTS.json and prints the dispositions. Unit = seed pair (lane, K, k); arms of a pair share a seed.
Exact two-sided sign tests on paired differences, ties dropped; Holm across the five primaries.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import multiprocessing as mp
import pathlib
import random
import statistics as st
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "receipts"
CONTROLS = ("OFF", "SHUFFLED", "YOKED")
MARGIN = 0.02                 # Q1 kill margin (percentage points of acquisition rate)
REPAIR_BASELINE = 4 / 60      # coupling campaign E2 K16 ON rate at 500 ticks


def sign_test(pos: int, neg: int) -> float:
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def boot_ci(xs, n=2000, seed=1):
    if not xs:
        return None
    rng = random.Random(seed); m = []
    for _ in range(n):
        s = [xs[rng.randrange(len(xs))] for _ in xs]; m.append(sum(s) / len(s))
    m.sort(); return [round(m[int(0.025 * n)], 4), round(m[int(0.975 * n) - 1], 4)]


def acquired(r) -> int:
    """a competent (configured task) self-replicator alive at the end; founders are verified NOT competent on it"""
    if r.get("void"):
        return 0
    return int(((r.get("competence") or {}).get("final_competent_sr") or 0) > 0)


def paired(pairs, a, b, f):
    pos = neg = ties = 0; d = []
    for arms in pairs.values():
        if a in arms and b in arms:
            x, y = f(arms[a]), f(arms[b])
            if x is None or y is None:
                continue
            d.append(x - y); pos += x > y; neg += x < y; ties += x == y
    return {"pairs": len(d), "a_greater": pos, "b_greater": neg, "ties": ties, "p": sign_test(pos, neg),
            "mean_diff": round(sum(d) / len(d), 4) if d else None, "ci95": boot_ci(d)}


def rate(pairs, arm, f):
    xs = [f(v[arm]) for v in pairs.values() if arm in v]
    return {"k": sum(xs), "n": len(xs), "rate": round(sum(xs) / len(xs), 4) if xs else None}


def robust_delta(r, key, field):
    """last-minus-first eligible checkpoint value of r['checkpoints'][*][key][field] (None if < 2 eligible)"""
    vals = [c[key][field] for c in (r.get("checkpoints") or []) if c.get(key) and c[key].get("eligible") and c[key].get(field) is not None]
    return round(vals[-1] - vals[0], 4) if len(vals) >= 2 else None


def holm(ps):
    order = sorted(ps, key=lambda k: ps[k]); m = len(ps); out = {}; run = 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (m - i) * ps[k])); out[k] = run
    return out


def _replay_one(args):
    code, p, stored = args
    sys.path.insert(0, code)
    from prometheus.z80atlas import multiday_campaign as MD
    q = dict(p)
    if stored.get("yoke_partner_void"):
        q["yoke"] = []
    out = MD._run(q)
    strip = lambda d: {k: v for k, v in d.items() if k not in ("wall_s", "yoke_partner_void")}
    return {"id": p["id"], "equal": json.dumps(strip(out), sort_keys=True, default=str) == json.dumps(strip(stored), sort_keys=True, default=str)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True); ap.add_argument("--code", required=True); ap.add_argument("--inputs", required=True)
    ap.add_argument("--replay", type=float, default=0.03); ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    sys.path.insert(0, a.code)
    from prometheus.z80atlas import multiday_campaign as MD
    inputs = json.loads(open(a.inputs, encoding="utf-8").read())
    P = MD.plan(inputs); plan_of = {p["id"]: p for p in P}
    wd = pathlib.Path(a.workdir)
    R = {}
    for line in open(wd / "results.jsonl", encoding="utf-8"):
        try:
            r = json.loads(line); R[r["id"]] = r
        except ValueError:
            pass
    status = json.loads(open(wd / "STATUS.json", encoding="utf-8").read())
    out = {"status": {k: status.get(k) for k in ("plan_sha256", "starts", "active_segments", "active_elapsed_s", "stopped_reason", "stopped_utc", "tail_repairs")},
           "planned": len(P), "completed": len(R), "voids": [i for i, r in R.items() if r.get("void")],
           "not_run": dict(collections.Counter(p["lane"] + "|" + p["K"] for p in P if p["id"] not in R)),
           "ledger_unbalanced": [i for i, r in R.items() if not r.get("void") and (r.get("coupling") or {}).get("balanced") is False],
           "yoke_partner_void": [i for i, r in R.items() if r.get("yoke_partner_void")]}
    by_lane = collections.defaultdict(lambda: collections.defaultdict(dict))
    for i, r in R.items():
        p = plan_of.get(i)
        if p is None:
            continue
        by_lane[p["lane"]][(p["K"], p["k"])][p["arm"]] = r
    primary = {}
    # ---- Q1: acquisition of the configured task (LADDER1, LADDER2, COPIER) --------------------------------------------
    for lane in ("LADDER1", "LADDER2", "COPIER"):
        t = by_lane[lane]
        vs = {c: paired(t, "ON", c, acquired) for c in CONTROLS}
        rates = {arm: rate(t, arm, acquired) for arm in ("ON",) + CONTROLS}
        best_ctrl = max((rates[c]["rate"] or 0) for c in CONTROLS)
        margin_ok = rates["ON"]["rate"] is not None and rates["ON"]["rate"] > best_ctrl + MARGIN
        by_k = {K: {arm: rate({kk: v for kk, v in t.items() if kk[0] == K}, arm, acquired) for arm in ("ON",) + CONTROLS} for K in ("K16", "K40")}
        primary["Q1_" + lane] = {"p": max(v["p"] for v in vs.values()), "vs": vs, "rates": rates, "by_K": by_k,
                                 "margin_ok": margin_ok, "direction_ok": all(v["a_greater"] > v["b_greater"] for v in vs.values())}
    # ---- Q2: protection of computation (task robustness rises within ON runs) -----------------------------------------
    on_d = [robust_delta(r, "robust_comp", "task") for L in by_lane.values() for arms in L.values() for arm, r in arms.items() if arm == "ON"]
    on_d = [x for x in on_d if x is not None]
    off_d = [robust_delta(r, "robust_sr_copy", "copy") for L in by_lane.values() for arms in L.values() for arm, r in arms.items() if arm == "OFF"]
    off_d = [x for x in off_d if x is not None]
    pos = sum(x > 0 for x in on_d); neg = sum(x < 0 for x in on_d)
    primary["Q2_protection"] = {"p": sign_test(pos, neg), "n": len(on_d), "pos": pos, "neg": neg,
                                "mean_delta_task_ON": round(st.mean(on_d), 4) if on_d else None, "ci95": boot_ci(on_d),
                                "direction_ok": pos > neg,
                                "control_OFF_delta_copy": {"n": len(off_d), "mean": round(st.mean(off_d), 4) if off_d else None, "ci95": boot_ci(off_d)}}
    # ---- Q3: repair becomes common (REPAIR lane) ----------------------------------------------------------------------
    t = by_lane["REPAIR"]
    vs = {c: paired(t, "ON", c, acquired) for c in ("OFF", "YOKED")}
    rr = {arm: rate(t, arm, acquired) for arm in ("ON", "OFF", "YOKED")}
    primary["Q3_repair"] = {"p": max(v["p"] for v in vs.values()), "vs": vs, "rates": rr,
                            "above_500tick_rate": (rr["ON"]["rate"] or 0) > REPAIR_BASELINE,
                            "direction_ok": all(v["a_greater"] > v["b_greater"] for v in vs.values())}
    ph = holm({k: v["p"] for k, v in primary.items()})
    for k, v in primary.items():
        v["p_holm"] = ph[k]
        extra = v.get("margin_ok", True) and v.get("above_500tick_rate", True)
        v["holds"] = v["p_holm"] < 0.05 and v["direction_ok"] and extra
    out["primary"] = primary
    # ---- descriptive (labelled; not tested) ----------------------------------------------------------------------------
    desc = {}
    for lane in ("LADDER1", "LADDER2"):
        t = by_lane[lane]
        desc[lane + "_prev_rung_retention_end"] = {arm: round(st.mean([(v[arm]["checkpoints"][-1].get("prev_rung_competent") or 0) / max(1, v[arm]["checkpoints"][-1]["alive"])
                                                                      for v in t.values() if arm in v and not v[arm].get("void") and v[arm].get("checkpoints")]) , 4)
                                                   if any(arm in v for v in t.values()) else None for arm in ("ON",) + CONTROLS}
    desc["acquisition_first_checkpoint"] = {lane: collections.Counter(
        next((c["tick"] for c in (arms["ON"].get("checkpoints") or []) if c.get("competent_sr")), None)
        for arms in by_lane[lane].values() if "ON" in arms) for lane in ("LADDER1", "LADDER2", "COPIER", "REPAIR")}
    desc["acquisition_first_checkpoint"] = {k: {str(kk): vv for kk, vv in v.items()} for k, v in desc["acquisition_first_checkpoint"].items()}
    desc["noncompetent_earner_share"] = {lane: (lambda cc, nc: round(nc / (cc + nc), 4) if cc + nc else None)(
        sum((r.get("competence") or {}).get("correct_by_competent", 0) for arms in L.values() for r in arms.values()),
        sum((r.get("competence") or {}).get("correct_by_noncompetent", 0) for arms in L.values() for r in arms.values())) for lane, L in by_lane.items()}
    desc["acquired_arch_ON"] = {lane: [arms["ON"].get("dominant_competent_arch") for arms in L.values() if "ON" in arms and acquired(arms["ON"])][:30]
                                for lane, L in by_lane.items()}
    out["descriptive"] = desc
    # ---- replay ------------------------------------------------------------------------------------------------------
    rng = random.Random(20260926)
    ids = sorted(i for i in R if not R[i].get("void"))
    sample = [i for i in ids if rng.random() < a.replay]
    jobs = []
    for i in sample:
        p = dict(plan_of[i])
        dep = p.get("depends")
        if p["arm"] == "YOKED":
            p["yoke"] = (R.get(dep) or {}).get("bonus_schedule") or []
        jobs.append((a.code, p, R[i]))
    with mp.Pool(a.workers, maxtasksperchild=2) as pool:
        rep = pool.map(_replay_one, jobs, chunksize=1)
    out["replay"] = {"n": len(rep), "equal": sum(x["equal"] for x in rep), "unequal": [x["id"] for x in rep if not x["equal"]]}
    out["instrument_ok"] = not out["voids"] and not out["ledger_unbalanced"] and not out["replay"]["unequal"]
    OUT.mkdir(exist_ok=True)
    (OUT / "MD_RESULTS.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"instrument_ok": out["instrument_ok"], "replay": out["replay"],
                      "primary": {k: {"p_holm": v["p_holm"], "holds": v["holds"]} for k, v in primary.items()}}, indent=1))


if __name__ == "__main__":
    mp.freeze_support()
    main()
