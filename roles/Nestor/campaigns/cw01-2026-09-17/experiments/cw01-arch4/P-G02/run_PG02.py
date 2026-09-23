"""P-G02 [T-ARCH4/M1, deformation A; requires P-G01]: RE-READ of the fixed-count damage claims with the
qualified scattered ruler. (a) P-D01: length effect, operand softness, set effect; (b) P-E05: depth 16 vs
64 under orig / no_growth (walks regenerated); (c) P-F06: select vs ancestors vs neutral drift at G60
(populations regenerated). Each claim returns SURVIVES_RULER_CHANGE / SHRINKS / REVERSES / DISAPPEARS /
UNRESOLVED with old and new numbers side by side. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import scatter as SC           # noqa: E402
import evolver as EV           # noqa: E402
import gate                    # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
sys.path.insert(0, str(HERE.parent / "P-E05"))
from run_PD01 import c408_tops   # noqa: E402
from run_PE05 import walk as walk64   # noqa: E402

PID, TID = "P-G02", "T-ARCH4/M1"
FS = (0.05, 0.10, 0.20)
OLD = {"pd01": {"log2_k": 0.145, "operand_vs_delete": (0.355, 0.717), "set_parent_vs_c408": 0.206, "set_walker_vs_c408": 0.194},
       "pe05": {"orig_64_minus_16": -0.099, "no_growth_64_minus_16": 0.099, "no_growth_minus_orig_at_64": 0.273},
       "pf06": {"select": 0.312, "ndrift": 0.621, "ancestor": 0.648, "select_coef_length_conditioned": -0.144, "seeds_holding": 6}}


def perm_slope(x, y, n=2000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    b = float(np.polyfit(x, y, 1)[0])
    rng = np.random.Generator(np.random.PCG64(seed))
    null = np.array([np.polyfit(rng.permutation(x), y, 1)[0] for _ in range(n)])
    return {"slope": b, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)), "n": int(ok.sum()), "outside": bool(b < np.percentile(null, 5) or b > np.percentile(null, 95))}


def disp(old, new_sig, new_val, same_sign):
    """SURVIVES: new significant, same sign, magnitude >= half the old; SHRINKS: significant same sign but smaller; REVERSES: significant opposite sign; DISAPPEARS: not significant."""
    if not new_sig:
        return "DISAPPEARS"
    if not same_sign:
        return "REVERSES"
    return "SURVIVES_RULER_CHANGE" if abs(new_val) >= 0.5 * abs(old) else "SHRINKS"


def a_job(j):
    p = j["program"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, {env: eps})
    out = {"pid": p["organism_id"], "set": p["stratum"], "n_instr": CM.n_instr(pm), "cells": {}}
    if pev[env]["answered_share"] == 0.0:
        out["degenerate"] = True
        return out
    out["degenerate"] = False
    for f in FS:
        for mode in ("delete", "operand"):
            r = SC.assay(pm, env, eps, f, 4, mode, p["organism_id"], pev=pev)
            out["cells"]["%s|%.2f" % (mode, f)] = {"loss": r["loss"], "disp": r["disp"], "dreward": r["dreward"], "fraction_hit": r["fraction_hit"]}
    return out


def b_job(j):
    p = j["parent"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    out = []
    for rule in ("orig", "no_growth"):
        for w in (1, 2):
            wk = walk64(pm, p["organism_id"], w, eps, rule, "frozen")
            for dd in (16, 64):
                m = wk["archived"].get(dd)
                if m is None:
                    continue
                r = SC.assay(m, env, eps, 0.10, 4, "delete", "%s|%s|%d|%d" % (p["organism_id"], rule, w, dd))
                if not r.get("degenerate"):
                    out.append({"pid": p["organism_id"], "rule": rule, "walker": w, "depth": dd, "loss": r["loss"], "dreward": r["dreward"], "n_instr": r["n_instr"]})
    return out


def c_evo(j):
    r = EV.run(j["arm"], j["seed"], j["init"], archive_gens=(59,), label="nestor.pf06")
    return {"arm": r["arm"], "seed": r["seed"], "pop": r["archive"][59]}


def c_assay(j):
    eps = A.episodes(EV.ENV)
    pm = A.canonical(j["m"])
    out = {k: v for k, v in j.items() if k != "m"}
    for f in (0.10, 0.20):
        r = SC.assay(pm, EV.ENV, eps, f, 4, "delete", j["tag"])
        out["loss_%.2f" % f] = None if r.get("degenerate") else r["loss"]
        out["dreward_%.2f" % f] = None if r.get("degenerate") else r["dreward"]
        out["n_instr"] = r.get("n_instr")
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "A", "requires": ["P-G01"], "scope": CM.SCOPE, "claim_type": "ruler-reread",
                         "ruler": SC.PROVENANCE, "fs": FS, "draws": 4, "old_numbers": OLD,
                         "claims": {"pd01_length": "loss falls with log length (old: fixed-k dose in units); new: slope of loss on log n at each f, permutation band",
                                    "pd01_operand": "operand hits softer than deletions (old .36 vs .72); new: paired sign-flip operand - delete at f .10",
                                    "pd01_set": "C4-08 tops ~.20 more robust than parents / walkers; new: relabel tops vs rest at f .10, and length-conditioned",
                                    "pe05_depth": "orig walks: loss falls 16 -> 64; no_growth: rises; new: paired 64 - 16 at f .10 per rule", "pe05_rule": "no_growth products lose more at 64; new: paired no_growth - orig at 64",
                                    "pf06_select": "select < ancestor and < ndrift at G60 (6/6 seeds); new: per-seed paired / relabel at f .10, length-conditioned coefficient"},
                         "disposition_rule": "SURVIVES if the new contrast clears its band with the old sign and magnitude >= half the old; SHRINKS if it clears but smaller; REVERSES if it clears with the opposite sign; DISAPPEARS if inside its band; UNRESOLVED if the reread could not be made",
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    gate.require_qualified(HERE, PID, TID, ph)
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    init, _ = EV.init_population()
    with A.pool(8) as ex:
        a_rows = [r for r in ex.map(a_job, [{"program": p} for p in programs]) if not r["degenerate"]]
        b_rows = [x for rs in ex.map(b_job, [{"parent": p} for p in parents]) for x in rs]
    with A.pool(6) as ex:
        pops = list(ex.map(c_evo, [{"arm": arm, "seed": s, "init": init} for arm in ("select", "ndrift") for s in range(1, 7)]))
    cj = []
    for r in pops:
        rng = A.SplitMix64(A.seed_from("nestor.pg02.sample", A.LOOP_SEED, r["arm"], r["seed"]))
        pop = r["pop"]
        chosen = sorted(pop, key=lambda x: -x["reward"])[:32] if r["arm"] == "select" else [pop[i] for i in sorted(set(int(rng.next_u32() % len(pop)) for _ in range(96)))[:32]]
        for i, x in enumerate(chosen):
            cj.append({"m": x["m"], "tag": "%s-%d-%d" % (r["arm"], r["seed"], i), "group": r["arm"], "seed": r["seed"], "anc": x["anc"]})
    for a in sorted({j["anc"] for j in cj}):
        cj.append({"m": init[a]["m"], "tag": "anc-%d" % a, "group": "ancestor", "seed": None, "anc": a})
    with A.pool(8) as ex:
        c_rows = list(ex.map(c_assay, cj))
    # ---- (a) P-D01
    res = {}
    lens = np.log([r["n_instr"] for r in a_rows])
    for f in FS:
        res["pd01_length|%.2f" % f] = perm_slope(lens, [r["cells"]["delete|%.2f" % f]["loss"] for r in a_rows])
    s10 = res["pd01_length|0.10"]
    res["pd01_length"] = disp(OLD["pd01"]["log2_k"], s10["outside"], -s10["slope"], s10["slope"] < 0)   # old: loss RISES with k at fixed n, i.e. falls with n at fixed k -> a negative slope on log n reproduces it
    sf_op = CM.paired_signflip([r["cells"]["operand|0.10"]["loss"] - r["cells"]["delete|0.10"]["loss"] for r in a_rows])
    res["pd01_operand_contrast"] = sf_op
    res["pd01_operand"] = disp(OLD["pd01"]["operand_vs_delete"][0] - OLD["pd01"]["operand_vs_delete"][1], bool(sf_op and (sf_op["below_p05"] or sf_op["above_p95"])), sf_op["mean_diff"] if sf_op else 0, bool(sf_op and sf_op["mean_diff"] < 0))
    tops = [r["cells"]["delete|0.10"]["loss"] for r in a_rows if r["set"] == "c408_ordinary"]
    rest = [r["cells"]["delete|0.10"]["loss"] for r in a_rows if r["set"] != "c408_ordinary"]
    rl = L.relabel_diff(rest, tops)
    X = np.column_stack([np.ones(len(a_rows)), lens, [1.0 if r["set"] == "c408_ordinary" else 0.0 for r in a_rows]])
    y = np.array([r["cells"]["delete|0.10"]["loss"] for r in a_rows])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    rng = np.random.Generator(np.random.PCG64(0))
    null = np.array([np.linalg.lstsq(X, rng.permutation(y), rcond=None)[0][2] for _ in range(2000)])
    res["pd01_set_contrast"] = {"relabel": rl, "length_conditioned_coef": float(beta[2]), "band": [float(np.percentile(null, 5)), float(np.percentile(null, 95))], "means": {"tops": float(np.mean(tops)), "rest": float(np.mean(rest))}}
    res["pd01_set"] = disp(-OLD["pd01"]["set_parent_vs_c408"], bool(rl["below_p05"] or rl["above_p95"]), rl["effect"], rl["effect"] < 0)
    res["pd01_by_set_f"] = {st: {"%.2f" % f: float(np.mean([r["cells"]["delete|%.2f" % f]["loss"] for r in a_rows if r["set"] == st])) for f in FS} for st in sorted({r["set"] for r in a_rows})}
    # ---- (b) P-E05
    byk = {}
    for r in b_rows:
        byk.setdefault((r["pid"], r["rule"], r["walker"]), {})[r["depth"]] = r
    for rule in ("orig", "no_growth"):
        pairs = [v[64]["loss"] - v[16]["loss"] for (pid, ru, w), v in byk.items() if ru == rule and 16 in v and 64 in v]
        sf = CM.paired_signflip(pairs)
        res["pe05_depth_%s_contrast" % rule] = sf
        old = OLD["pe05"]["%s_64_minus_16" % rule]
        res["pe05_depth_%s" % rule] = disp(old, bool(sf and (sf["below_p05"] or sf["above_p95"])), sf["mean_diff"] if sf else 0, bool(sf and np.sign(sf["mean_diff"]) == np.sign(old)))
    pairs = []
    for (pid, ru, w), v in byk.items():
        if ru == "orig" and 64 in v:
            o = byk.get((pid, "no_growth", w), {}).get(64)
            if o:
                pairs.append(o["loss"] - v[64]["loss"])
    sf = CM.paired_signflip(pairs)
    res["pe05_rule_contrast"] = sf
    res["pe05_rule"] = disp(OLD["pe05"]["no_growth_minus_orig_at_64"], bool(sf and (sf["below_p05"] or sf["above_p95"])), sf["mean_diff"] if sf else 0, bool(sf and sf["mean_diff"] > 0))
    res["pe05_means"] = {"%s|%d" % (ru, dd): float(np.mean([r["loss"] for r in b_rows if r["rule"] == ru and r["depth"] == dd])) for ru in ("orig", "no_growth") for dd in (16, 64)}
    # ---- (c) P-F06
    anc = {r["anc"]: r for r in c_rows if r["group"] == "ancestor"}
    M = EV.mean_or_none
    per_seed, holding = {}, []
    for s in range(1, 7):
        S_ = [r for r in c_rows if r["group"] == "select" and r["seed"] == s and r["loss_0.10"] is not None]
        D_ = [r for r in c_rows if r["group"] == "ndrift" and r["seed"] == s and r["loss_0.10"] is not None]
        sfa = CM.paired_signflip([r["loss_0.10"] - anc[r["anc"]]["loss_0.10"] for r in S_ if anc.get(r["anc"]) and anc[r["anc"]]["loss_0.10"] is not None])
        rl6 = L.relabel_diff([r["loss_0.10"] for r in D_], [r["loss_0.10"] for r in S_]) if S_ and D_ else None
        per_seed[s] = {"select": M([r["loss_0.10"] for r in S_]), "ndrift": M([r["loss_0.10"] for r in D_]), "select_minus_anc": sfa, "select_minus_ndrift": rl6}
        if sfa and sfa["below_p05"] and rl6 and rl6["below_p05"]:
            holding.append(s)
    g = [r for r in c_rows if r["group"] in ("select", "ndrift") and r["loss_0.10"] is not None]
    X = np.column_stack([np.ones(len(g)), np.log([r["n_instr"] for r in g]), [1.0 if r["group"] == "select" else 0.0 for r in g]])
    y = np.array([r["loss_0.10"] for r in g])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    null = np.array([np.linalg.lstsq(X, rng.permutation(y), rcond=None)[0] for _ in range(2000)])
    res["pf06_means"] = {"select": M([r["loss_0.10"] for r in g if r["group"] == "select"]), "ndrift": M([r["loss_0.10"] for r in g if r["group"] == "ndrift"]), "ancestor": M([v["loss_0.10"] for v in anc.values()]),
                         "select_0.20": M([r["loss_0.20"] for r in g if r["group"] == "select"]), "ndrift_0.20": M([r["loss_0.20"] for r in g if r["group"] == "ndrift"])}
    res["pf06_length_conditioned"] = {"log_len": float(b[1]), "log_len_band": [float(np.percentile(null[:, 1], 5)), float(np.percentile(null[:, 1], 95))], "select": float(b[2]), "select_band": [float(np.percentile(null[:, 2], 5)), float(np.percentile(null[:, 2], 95))]}
    res["pf06_seeds_holding"] = holding
    res["pf06_per_seed"] = {str(k): v for k, v in per_seed.items()}
    sel_sig = not (np.percentile(null[:, 2], 5) <= b[2] <= np.percentile(null[:, 2], 95))
    res["pf06_select"] = disp(OLD["pf06"]["select_coef_length_conditioned"], bool(len(holding) >= 4 or sel_sig), float(b[2]), b[2] < 0)
    audit = {k: res[k] for k in ("pd01_length", "pd01_operand", "pd01_set", "pe05_depth_orig", "pe05_depth_no_growth", "pe05_rule", "pf06_select")}
    material = True
    out = {"perturbation_id": PID, "parent": TID, "ruler_audit": audit, "details": res, "old": OLD, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps({"a": a_rows, "b": b_rows, "c": c_rows}, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "RULER REREAD (scattered f): %s | length slopes %s | operand-delete %s | tops vs rest %s (length-conditioned %+.3f band %s) | P-E05 means %s, depth contrasts orig %s no_growth %s, rule %s | P-F06 means %s, length-conditioned select %+.3f band %s, seeds holding %s"
                      % (audit, {k: (round(v["slope"], 3), v["outside"]) for k, v in res.items() if k.startswith("pd01_length|")}, (round(sf_op["mean_diff"], 3), sf_op["below_p05"]) if sf_op else None,
                         (round(rl["effect"], 3), rl["below_p05"]), beta[2], [round(x, 3) for x in res["pd01_set_contrast"]["band"]], {k: round(v, 3) for k, v in res["pe05_means"].items()},
                         (round(res["pe05_depth_orig_contrast"]["mean_diff"], 3), res["pe05_depth_orig_contrast"]["below_p05"]) if res["pe05_depth_orig_contrast"] else None,
                         (round(res["pe05_depth_no_growth_contrast"]["mean_diff"], 3), res["pe05_depth_no_growth_contrast"]["above_p95"]) if res["pe05_depth_no_growth_contrast"] else None,
                         (round(sf["mean_diff"], 3), sf["above_p95"]) if sf else None, {k: (round(v, 3) if v is not None else None) for k, v in res["pf06_means"].items()}, b[2], [round(x, 3) for x in res["pf06_length_conditioned"]["select_band"]], holding),
                      material, detail={"audit": audit, "details": {k: v for k, v in res.items() if not k.endswith("_contrast") and k not in ("pf06_per_seed",)}})
    for tid in ("T-X15", "T-R01"):
        L.append_evidence(tid, PID, "cross: ruler audit %s" % audit, material)
    print("DONE %s (%.0f s)" % (audit, time.time() - t0))


if __name__ == "__main__":
    main()
