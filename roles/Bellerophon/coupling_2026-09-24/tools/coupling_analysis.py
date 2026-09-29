"""Preregistered analysis of the coupling campaign (COUPLING_CAMPAIGN_PREREG.md). Frozen with the preregistration,
before the first scientific run. Implements the primary tests P1-P6 (Holm), the secondary families, the replay check,
the AUTO verdict rule, origin/mechanism clustering and the frozen READINESS rule. Nothing here may change after launch.
    python coupling_analysis.py --workdir <dir> [--replay 0.03] [--workers 16]
Writes ../receipts/COUPLING_RESULTS.json, ../COUPLING_CAUSAL_LEDGER.jsonl, ../COUPLING_ORIGIN_LEDGER.jsonl."""
from __future__ import annotations

import argparse
import collections
import json
import math
import multiprocessing as mp
import os
import pathlib
import random
import statistics as st
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "receipts"
PINNED = None                                         # set from --code (the pinned code copy the campaign ran)


# ---- statistics ----------------------------------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def sign_test(a, b):
    n = a + b
    if n == 0:
        return 1.0
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[a] + 1e-15))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); m = len(ps); adj = [None] * m; run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i])); adj[i] = round(run, 8)
    return adj


def _rm(xs, nd):
    xs = list(xs)
    return round(st.mean(xs), nd) if xs else None


def boot_ci(xs, B=2000, seed=7):
    if not xs:
        return None
    rng = random.Random(seed); n = len(xs)
    ms = sorted(st.mean(rng.choice(xs) for _ in range(n)) for _ in range(B))
    return [round(ms[int(0.025 * B)], 4), round(ms[int(0.975 * B) - 1], 4)]


def paired(results_by_pair, arm_a, arm_b, f):
    """paired comparison of metric f (None = undefined) between two arms sharing a seed: sign test on the sign of
    f(a) - f(b) (ties dropped), mean difference with bootstrap CI over pairs."""
    d = []
    for arms in results_by_pair.values():
        if arm_a in arms and arm_b in arms:
            x, y = f(arms[arm_a]), f(arms[arm_b])
            if x is not None and y is not None:
                d.append(x - y)
    pos = sum(1 for v in d if v > 0); neg = sum(1 for v in d if v < 0)
    return {"pairs": len(d), "a_greater": pos, "b_greater": neg, "ties": len(d) - pos - neg, "p": sign_test(pos, neg),
            "mean_diff": _rm((d), 4) if d else None, "ci95": boot_ci(d)}


# ---- per-run metrics (frozen) ----------------------------------------------------------------------------------------
def comp_final(r):
    return None if r.get("void") else ((r.get("competence") or {}).get("final_competent") or 0) / 256.0


def comp_sr_alive(r):
    return None if r.get("void") else int(((r.get("competence") or {}).get("final_competent_sr") or 0) > 0)


def extinct(r):
    return None if r.get("void") else int(bool(r["extinct"]))


def persists(r):
    return None if r.get("void") else int(not r["extinct"])


def paid_births(r):
    return None if r.get("void") else (r.get("coupling") or {}).get("paid_births", r.get("endogenous_births"))


def r_cc(r, min_n=20):
    c = r.get("competence") or {}
    n = c.get("sr_births_comp_parent") or 0
    return (c["sr_comp_parent_comp_child"] / n) if n >= min_n else None


def r_nc(r, min_n=20):
    c = r.get("competence") or {}
    n = (c.get("sr_births") or 0) - (c.get("sr_births_comp_parent") or 0)
    return (c["sr_noncomp_parent_comp_child"] / n) if n >= min_n else None


def enrichment(r):
    """share of (sampled) births written by competent writers / time-mean competent share of the living"""
    c = r.get("competence") or {}
    if (c.get("births_all") or 0) < 10:
        return None
    fr = [s[2] / s[1] for s in (c.get("samples") or []) if s[1] > 0]
    m = st.mean(fr) if fr else 0
    if m <= 0:
        return None
    return (c["births_comp_writer"] / c["births_all"]) / m


def denovo_competent_sr(r):
    """a competent self-replicating tape dominant at the end that is not byte-identical to any fixture of the run"""
    c = r.get("competence") or {}
    t = c.get("dominant_competent_sr_tape")
    return None if r.get("void") else int(bool(t) and t not in (r.get("fixture_tapes") or []))


# ---- AUTO verdict rule (frozen) --------------------------------------------------------------------------------------
def auto_verdicts(auto):
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    cand = {}
    for r in auto:
        ci = int(r["pair"].split("|")[1])
        by[ci][r["arm"]].append(r); cand[ci] = r.get("candidate") or cand.get(ci)
    out = []
    for ci, arms in sorted(by.items()):
        succ = {a: sum(1 for r in rs if comp_sr_alive(r)) for a, rs in arms.items()}
        n = {a: len(rs) for a, rs in arms.items()}
        on = succ.get("ON", 0); ctrl = succ.get("OFF", 0) + succ.get("RANDOM_REWARD", 0); tab = succ.get("TASK_ABLATED_ON", 0)
        if n.get("ON", 0) < 3:
            v = "NOT_ADJUDICABLE"
        elif on >= 2 and ctrl <= 1 and tab <= 1:
            v = "CAUSAL_COUPLED"
        elif on >= 2:
            v = "SURVIVES_WITHOUT_COUPLING_OR_TASK"
        else:
            v = "NOT_REPRODUCED"
        out.append({"candidate": ci, "source_run": (cand.get(ci) or {}).get("source_run"), "tape": (cand.get(ci) or {}).get("tape"),
                    "successes": succ, "n": n, "verdict": v})
    return out


def mech_key(arch):
    if not arch:
        return None
    tp = arch.get("task_pcs") or []
    return (arch.get("copy_op"), arch.get("copy_pc"), arch.get("copy_len"), tuple(tp), bool(arch.get("copy_covers_task")))


# ---- replay ----------------------------------------------------------------------------------------------------------
def _replay(item):
    import tempfile, shutil
    p, stored, code = item
    if code not in sys.path:
        sys.path.insert(0, code)
    from prometheus.z80atlas import coupling_campaign as CC
    td = tempfile.mkdtemp()
    try:
        q = dict(p, workdir=td, drop_rundir=True)
        if stored.get("_yoke") is not None:
            q["yoke"] = stored["_yoke"]
        out = CC._run(q)
        strip = lambda d: {k: v for k, v in d.items() if k not in ("wall_s", "_yoke")}
        return {"id": p["id"], "equal": json.dumps(strip(out), sort_keys=True, default=str) == json.dumps(strip(stored), sort_keys=True, default=str)}
    finally:
        shutil.rmtree(td, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True); ap.add_argument("--code", required=True)
    ap.add_argument("--inputs", required=True); ap.add_argument("--replay", type=float, default=0.03); ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, a.code)
    from prometheus.z80atlas import coupling_campaign as CC
    inputs = json.loads(open(a.inputs, encoding="utf-8").read())
    P1 = CC.plan(inputs)
    if a.smoke:
        keep = set(p["pair"] for p in P1[:: max(1, len(P1) // a.smoke)])
        P1 = [dict(p, seed=p["seed"] - 3_500_000_000_000) for p in P1 if p["pair"] in keep]
    plan_of = {p["id"]: p for p in P1}
    wd = pathlib.Path(a.workdir)
    R = {}
    for line in open(wd / "results.jsonl", encoding="utf-8"):
        try:
            r = json.loads(line); R[r["id"]] = r
        except ValueError:
            pass
    status = json.loads(open(wd / "STATUS.json", encoding="utf-8").read())
    P2 = json.loads(open(wd / "PHASE2_PLAN.json", encoding="utf-8").read()) if (wd / "PHASE2_PLAN.json").exists() else []
    PE = json.loads(open(wd / "EXT_PLAN.json", encoding="utf-8").read()) if (wd / "EXT_PLAN.json").exists() else []
    for p in P2 + PE:
        plan_of[p["id"]] = p
    out = {"status": status, "phase1_planned": len(P1), "phase2_planned": len(P2), "ext_planned": len(PE),
           "completed": len(R), "voids": [r["id"] for r in R.values() if r.get("void")],
           "not_run": collections.Counter(plan_of[i]["lane"] for i in plan_of if i not in R),
           "ledger_unbalanced": [r["id"] for r in R.values() if not r.get("void") and r.get("coupling") and r["coupling"].get("balanced") is False]}
    # pair tables (extension seeds pool with their lane's cell)
    def pairs(lane, block=None, K=None, cellpref=None):
        t = collections.defaultdict(dict)
        for r in R.values():
            p = plan_of.get(r["id"])
            if p is None:
                continue
            L = p.get("ext_of", p["lane"]) if p["lane"] == "EXT" else p["lane"]
            if L != lane or (K and p["K"] != K) or (block is not None and p["block"] != block) or (cellpref and not p["cell"].startswith(cellpref)):
                continue
            t[(p["block"], p["k"], p.get("ext_of"))][p["arm"]] = r
        return t

    # ---- P1: Lane A, correct computation -> reproductive output --------------------------------------------------
    A = {}
    for K in ("K16", "K40"):
        tA = collections.defaultdict(dict)
        for r in R.values():
            p = plan_of[r["id"]]
            if p["lane"] == "A" and p["K"] == K:
                tA[p["k"]][p["arm"]] = r
        A[K] = {x: paired(tA, "A1_hyb_ON", x, paid_births) for x in ("A2_hyb_OFF", "A3_nocomp_ON", "A4_nocopy_ON", "A5_hyb_SHUFFLED", "A6_randout_ON", "A7_rep_ON")}
        A[K]["persist"] = {arm: {"k": sum(persists(v[arm]) or 0 for v in tA.values() if arm in v), "n": sum(1 for v in tA.values() if arm in v)}
                           for arm in sorted({a for v in tA.values() for a in v})}
        A[K]["bonus_earned_mean"] = {arm: _rm(((v[arm].get("coupling") or {}).get("earned_bonus", 0) for v in tA.values() if arm in v and not v[arm].get("void")), 1)
                                     for arm in sorted({a for v in tA.values() for a in v})}
    out["laneA"] = A
    # ---- Lane C (P2, P3, P4, P5) ---------------------------------------------------------------------------------------
    C = {}
    for K in ("K16", "K40"):
        t = pairs("C", K=K)
        C[K] = {"comp_final": {x: paired(t, "ON", x, comp_final) for x in ("YOKED", "OFF", "RANDOM_REWARD", "DELAYED", "IRRELEVANT")},
                "extinct": {x: paired(t, x, "ON", extinct) for x in ("YOKED", "OFF", "RANDOM_REWARD", "DELAYED", "IRRELEVANT")},
                "retention_r_cc": {x: paired(t, "ON", x, r_cc) for x in ("YOKED", "RANDOM_REWARD", "IRRELEVANT")},
                "enrichment": {arm: (lambda xs: {"n": len(xs), "median": st.median(xs) if xs else None, "ci95_mean": boot_ci(xs)})(
                    [e for e in (enrichment(v[arm]) for v in t.values() if arm in v) if e is not None]) for arm in ("ON", "YOKED", "OFF", "RANDOM_REWARD", "DELAYED", "IRRELEVANT")},
                "heritability_gap_ON": (lambda hs: {"n": len(hs), "pos": sum(h > 0 for h in hs), "neg": sum(h < 0 for h in hs),
                                                    "p": sign_test(sum(h > 0 for h in hs), sum(h < 0 for h in hs)), "mean": _rm((hs), 4) if hs else None,
                                                    "ci95": boot_ci(hs)})(
                    [r_cc(v["ON"]) - r_nc(v["ON"]) for v in t.values() if "ON" in v and r_cc(v["ON"]) is not None and r_nc(v["ON"]) is not None]),
                "irrelevant_emitters_final_mean": {arm: _rm((((v[arm].get("competence") or {}).get("final_irrelevant_emitters") or 0) for v in t.values() if arm in v), 2)
                                                   for arm in ("ON", "IRRELEVANT", "YOKED")},
                "comp_final_mean": {arm: _rm((comp_final(v[arm]) or 0 for v in t.values() if arm in v), 4) for arm in ("ON", "YOKED", "OFF", "RANDOM_REWARD", "DELAYED", "IRRELEVANT")},
                "persist": {arm: {"k": sum(persists(v[arm]) or 0 for v in t.values() if arm in v), "n": sum(1 for v in t.values() if arm in v)}
                            for arm in ("ON", "YOKED", "OFF", "RANDOM_REWARD", "DELAYED", "IRRELEVANT")}}
    out["laneC"] = C
    # ---- Lane E2 (P6) ------------------------------------------------------------------------------------------------
    E2 = {}
    for K in ("K16", "K40"):
        t = pairs("E2", K=K)
        E2[K] = {"repair_emerged": {x: paired(t, "ON", x, comp_sr_alive) for x in ("OFF", "YOKED")},
                 "rate": {arm: {"k": sum(comp_sr_alive(v[arm]) or 0 for v in t.values() if arm in v), "n": sum(1 for v in t.values() if arm in v)} for arm in ("ON", "OFF", "YOKED")},
                 "repaired_arch": [v["ON"].get("dominant_competent_arch") for v in t.values() if "ON" in v and comp_sr_alive(v["ON"])][:40]}
    out["laneE2"] = E2
    # ---- primary family + Holm ---------------------------------------------------------------------------------------
    prim = {"P1_A1_vs_A3_paid_births_K16": A["K16"]["A3_nocomp_ON"], "P2_C_ON_vs_YOKED_comp_final_K16": C["K16"]["comp_final"]["YOKED"],
            "P3_C_ON_heritability_gap_K16": C["K16"]["heritability_gap_ON"], "P4_C_YOKED_vs_ON_extinction_K16": C["K16"]["extinct"]["YOKED"],
            "P5_C_ON_vs_YOKED_retention_K16": C["K16"]["retention_r_cc"]["YOKED"], "P6_E2_ON_vs_OFF_repair_K16": E2["K16"]["repair_emerged"]["OFF"]}
    dir_ok = {"P1_A1_vs_A3_paid_births_K16": lambda d: d["a_greater"] > d["b_greater"], "P2_C_ON_vs_YOKED_comp_final_K16": lambda d: d["a_greater"] > d["b_greater"],
              "P3_C_ON_heritability_gap_K16": lambda d: d["pos"] > d["neg"], "P4_C_YOKED_vs_ON_extinction_K16": lambda d: d["a_greater"] > d["b_greater"],
              "P5_C_ON_vs_YOKED_retention_K16": lambda d: d["a_greater"] > d["b_greater"], "P6_E2_ON_vs_OFF_repair_K16": lambda d: d["a_greater"] > d["b_greater"]}
    names = list(prim); adj = holm([prim[n]["p"] for n in names])
    out["primary"] = {n: dict(prim[n], p_holm=adj[i], direction_as_predicted=dir_ok[n](prim[n]), holds=adj[i] < 0.05 and dir_ok[n](prim[n]))
                      for i, n in enumerate(names)}
    # ---- Lane F / G generality ---------------------------------------------------------------------------------------
    F = {}
    for task in ("CONST", "ECHO", "INC", "COND_ONE", "SUM2", "COND_MULTI"):
        t = pairs("F", cellpref="F_%s_" % task)
        F[task] = {"ON_vs_YOKED": paired(t, "ON", "YOKED", comp_final), "ON_vs_OFF": paired(t, "ON", "OFF", comp_final),
                   "retention_ON_vs_YOKED": paired(t, "ON", "YOKED", r_cc),
                   "comp_final_mean": {arm: _rm((comp_final(v[arm]) or 0 for v in t.values() if arm in v), 4) for arm in ("ON", "OFF", "YOKED")},
                   "dominant_arch_ON": [v["ON"].get("dominant_competent_arch") for v in t.values() if "ON" in v][:5]}
    out["laneF"] = F
    out["laneF_replicating_tasks"] = [k for k, v in F.items() if v["ON_vs_YOKED"]["p"] < 0.05 and v["ON_vs_YOKED"]["a_greater"] > v["ON_vs_YOKED"]["b_greater"]]
    # OFF worlds must not depend on task identity (G1T check under v3): identical OFF trajectories across tasks at equal seeds are NOT
    # expected here (fixtures differ by task), so reported: OFF comp means only.
    G = {}
    for r in R.values():
        p = plan_of[r["id"]]
    for name in ("copy_cost2", "ldir_cost4", "undefined_halt", "mut_low", "mut_vlow", "VM_COPY", "BYTECODE32", "CONSTRUCTIVE"):
        t = pairs("G", cellpref="G_%s_" % name)
        G[name] = {"ON_vs_OFF": paired(t, "ON", "OFF", comp_final), "persist": {arm: {"k": sum(persists(v[arm]) or 0 for v in t.values() if arm in v),
                                                                                      "n": sum(1 for v in t.values() if arm in v)} for arm in ("ON", "OFF")}}
    out["laneG"] = G
    out["laneG_replicating"] = [k for k, v in G.items() if v["ON_vs_OFF"]["p"] < 0.05 and v["ON_vs_OFF"]["a_greater"] > v["ON_vs_OFF"]["b_greater"]]
    # ---- Lane B (fresh evolution) ------------------------------------------------------------------------------------
    B = {}
    for lane in ("B-rand", "B-cop"):
        cells = sorted({plan_of[i]["block"] for i in plan_of if plan_of[i]["lane"] == lane})
        for bl in cells:
            t = pairs(lane, block=bl)
            ex = next(iter(t.values())).get("ON") if t else None
            label = "%s|%s" % (lane, plan_of[ex["id"]]["cell"].rsplit("_", 1)[0] if ex else bl)
            B[label] = {"denovo_competent_sr": {arm: {"k": sum(denovo_competent_sr(v[arm]) or 0 for v in t.values() if arm in v), "n": sum(1 for v in t.values() if arm in v)}
                                                for arm in ("ON", "OFF", "SHUFFLED", "YOKED")},
                        "ON_vs_YOKED": paired(t, "ON", "YOKED", denovo_competent_sr), "ON_vs_OFF": paired(t, "ON", "OFF", denovo_competent_sr),
                        "ON_vs_SHUFFLED": paired(t, "ON", "SHUFFLED", denovo_competent_sr),
                        "comp_final_ON_vs_YOKED": paired(t, "ON", "YOKED", comp_final),
                        "spontaneous_SR": {arm: {"k": sum(1 for v in t.values() if arm in v and (v[arm].get("first_self_replication") or {}).get("tick") is not None
                                                          and not (v[arm]["first_self_replication"] or {}).get("seeded")), "n": sum(1 for v in t.values() if arm in v)}
                                           for arm in ("ON", "OFF", "SHUFFLED", "YOKED")},
                        "persist": {arm: {"k": sum(persists(v[arm]) or 0 for v in t.values() if arm in v), "n": sum(1 for v in t.values() if arm in v)} for arm in ("ON", "OFF", "SHUFFLED", "YOKED")}}
    out["laneB"] = B
    # ---- Lane I (exploits): designed probes + the automated probe in every run ---------------------------------------
    I = {}
    for r in R.values():
        p = plan_of[r["id"]]
        if p["lane"] == "I" and not r.get("void"):
            d = I.setdefault(p["cell"], {"n": 0, "persist": 0, "earned_bonus": [], "correct_by_noncompetent": 0, "correct_by_competent": 0})
            d["n"] += 1; d["persist"] += persists(r); d["earned_bonus"].append((r.get("coupling") or {}).get("earned_bonus", 0))
            c = r.get("competence") or {}; d["correct_by_noncompetent"] += c.get("correct_by_noncompetent", 0); d["correct_by_competent"] += c.get("correct_by_competent", 0)
    for d in I.values():
        d["earned_bonus_mean"] = _rm((d.pop("earned_bonus")), 1)
    auto_probe = collections.defaultdict(lambda: [0, 0, 0])
    earners = []
    for r in R.values():
        if r.get("void"):
            continue
        p = plan_of[r["id"]]; c = r.get("competence") or {}
        if p["config_overrides"].get("coupling") in ("ON",):
            a_ = auto_probe[p["lane"]]; a_[0] += c.get("correct_by_noncompetent", 0); a_[1] += c.get("correct_by_competent", 0); a_[2] += 1
            for tape, info in (c.get("noncompetent_earners") or {}).items():
                if len(earners) < 400:
                    earners.append({"run": r["id"], "lane": p["lane"], "tape": tape, "tick": info.get("tick"), "partner_present": info.get("partner_present")})
    out["laneI"] = {"designed_probes": I, "auto_probe_ON_by_lane": {k: {"correct_by_noncompetent": v[0], "correct_by_competent": v[1], "runs": v[2],
                                                                       "noncompetent_share": round(v[0] / max(1, v[0] + v[1]), 4)} for k, v in auto_probe.items()},
                    "noncompetent_earner_specimens": len(earners)}
    # ---- Lane J -----------------------------------------------------------------------------------------------------
    J = collections.defaultdict(lambda: collections.defaultdict(lambda: {"n": 0, "persist": 0, "comp_sr_alive": 0, "fixture_share": []}))
    for r in R.values():
        p = plan_of[r["id"]]
        if p["lane"] == "J" and not r.get("void"):
            kind = p["cell"][2:].rsplit("_", 1)[0]
            d = J[kind][p["arm"]]; d["n"] += 1; d["persist"] += persists(r); d["comp_sr_alive"] += comp_sr_alive(r)
            d["fixture_share"].append((r.get("competence") or {}).get("fixture_lineage_share") or 0)
    out["laneJ"] = {k: {arm: dict(v, fixture_share=_rm((v["fixture_share"]), 3) if v["fixture_share"] else None) for arm, v in arms.items()} for k, arms in J.items()}
    # ---- AUTO causal follow-ups -----------------------------------------------------------------------------------
    auto = [r for r in R.values() if plan_of.get(r["id"], {}).get("lane") == "AUTO"]
    for r in auto:
        r["candidate"] = plan_of[r["id"]].get("candidate")
    av = auto_verdicts(auto)
    out["AUTO"] = {"candidates": len(av), "verdicts": collections.Counter(v["verdict"] for v in av)}
    # ---- Lane H origins: every de novo competent-SR run is one origin; cluster by mechanism --------------------------
    origins = []; variants = collections.Counter()
    for r in R.values():
        p = plan_of.get(r["id"])
        # independent ORIGINS only where no competent fixture was seeded (B-rand, B-cop; E2's seed is not competent).
        # In C/F/G a competent SR tape differing from the seeded hybrid is a DESCENDANT variant: counted separately.
        if p is None or r.get("void"):
            continue
        if p["lane"] in ("C", "F", "G") and denovo_competent_sr(r):
            variants[p["lane"] + "|" + p["arm"]] += 1
            continue
        if p["lane"] not in ("B-rand", "B-cop", "E2"):
            continue
        if denovo_competent_sr(r):
            a_ = r.get("dominant_competent_arch")
            origins.append({"run": r["id"], "lane": p["lane"], "cell": p["cell"], "arm": p["arm"], "K": p["K"], "tape": r["competence"]["dominant_competent_sr_tape"],
                            "mech_key": [str(x) for x in (mech_key(a_) or [])], "arch": a_})
    keys = collections.Counter(tuple(o["mech_key"]) for o in origins)
    auto_by_src = {v["source_run"]: v["verdict"] for v in av}
    for o in origins:
        o["auto_verdict"] = auto_by_src.get(o["run"])
    out["laneH"] = {"fixture_descendant_variant_runs_C_F_G": dict(variants), "denovo_runs": len(origins), "by_lane_arm": collections.Counter("%s|%s" % (o["lane"], o["arm"]) for o in origins),
                    "distinct_mechanisms": len(keys), "distinct_tapes": len({o["tape"] for o in origins}),
                    "causal_coupled_candidates": sum(1 for v in av if v["verdict"] == "CAUSAL_COUPLED"),
                    "causal_coupled_distinct_mechanisms": len({tuple(o["mech_key"]) for o in origins if o["auto_verdict"] == "CAUSAL_COUPLED"})}
    # ---- replay sample ------------------------------------------------------------------------------------------------
    ids = sorted(i for i, r in R.items() if not r.get("void") and plan_of[i]["lane"] != "AUTO")
    samp = random.Random(2026092499).sample(ids, max(1, int(round(a.replay * len(ids))))) if a.replay > 0 else []
    items = []
    for i in samp:
        p = plan_of[i]; st_r = dict(R[i])
        if p.get("depends"):
            st_r["_yoke"] = R[p["depends"]].get("bonus_schedule") or []
        items.append((p, st_r, a.code))
    if items:
        with mp.Pool(a.workers) as pool:
            rep = pool.map(_replay, items, chunksize=1)
        out["replay"] = {"n": len(rep), "equal": sum(x["equal"] for x in rep), "unequal": [x["id"] for x in rep if not x["equal"]][:20]}
    # ---- READINESS (frozen rule) ------------------------------------------------------------------------------------
    pr = out["primary"]
    a8 = A["K16"]["persist"].get("A8_rep_v2", {"k": 0, "n": 1})
    instrument_ok = (not out["voids"]) and (not out["ledger_unbalanced"]) and (out.get("replay", {}).get("equal") == out.get("replay", {}).get("n")) \
        and a8["k"] >= 0.9 * a8["n"]
    core = pr["P1_A1_vs_A3_paid_births_K16"]["holds"] and pr["P2_C_ON_vs_YOKED_comp_final_K16"]["holds"] and pr["P3_C_ON_heritability_gap_K16"]["holds"]
    novelty = pr["P6_E2_ON_vs_OFF_repair_K16"]["holds"] or (out["laneH"]["causal_coupled_candidates"] >= 3 and out["laneH"]["causal_coupled_distinct_mechanisms"] >= 2)
    general = len(out["laneF_replicating_tasks"]) >= 3 and len(out["laneG_replicating"]) >= 4
    if not instrument_ok:
        cls = "INSTRUMENT_REPAIR_REQUIRED"
    elif core and novelty and general:
        cls = "READY_FOR_MULTIDAY"
    elif core:
        cls = "READY_WITH_RESTRICTED_SCOPE"
    else:
        cls = "REPHYSICS_REQUIRED"
    out["readiness"] = {"classification": cls, "instrument_ok": instrument_ok, "core_P1_P2_P3": core, "novelty": novelty, "generality": general,
                        "a8_positive_control": a8}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "COUPLING_RESULTS.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    with open(HERE.parent / "COUPLING_CAUSAL_LEDGER.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for n, d in out["primary"].items():
            fh.write(json.dumps({"kind": "primary_test", "id": n, **d}, sort_keys=True, default=str) + "\n")
        for v in av:
            fh.write(json.dumps({"kind": "auto_candidate", **v}, sort_keys=True, default=str) + "\n")
        for task, d in F.items():
            fh.write(json.dumps({"kind": "laneF_task", "task": task, "ON_vs_YOKED": d["ON_vs_YOKED"], "ON_vs_OFF": d["ON_vs_OFF"]}, sort_keys=True, default=str) + "\n")
        for name, d in G.items():
            fh.write(json.dumps({"kind": "laneG_perturbation", "name": name, **d}, sort_keys=True, default=str) + "\n")
        for e in earners:
            fh.write(json.dumps({"kind": "exploit_candidate_noncompetent_earner", **e}, sort_keys=True) + "\n")
    with open(HERE.parent / "COUPLING_ORIGIN_LEDGER.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for o in origins:
            fh.write(json.dumps(o, sort_keys=True, default=str) + "\n")
    print(json.dumps({"readiness": out["readiness"], "primary": {n: (d["p_holm"], d["holds"]) for n, d in out["primary"].items()},
                      "completed": out["completed"], "voids": len(out["voids"]), "replay": out.get("replay")}, indent=1, default=str))


if __name__ == "__main__":
    main()
