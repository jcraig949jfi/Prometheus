"""P-E01 [deformation B, T-X12]: TICK-CONTENT RESPONSE MAP.

Program-level ruler: SELF-DISPLACEMENT - a program's answer vector on episodes identical to the W0
base except for inserted material, against its answers on the base. Variants (ticks.w0_variants):
empty tick / 1-4 NOISE ticks / repeated last PUT / NOISE words inside the last PUT tick (no tick
boundary) / NOISE or empty tick BEFORE the first PUT / NOISE-then-empty vs empty-then-NOISE; and the
persist policy forced to 'none'. Lineages: viable parents of all strata, walker-16 descendants,
C4-08 selected tops. Per program a response class; per set the class shares (Wilson). Walker level:
w0_solver walkers 1-4 with a per-step self-displacement trace (onset step of tick sensitivity) and a
REVERT test where feasible. Cross observable (absorbed P-E07): tick sensitivity vs P-D01 damage loss
and state-use descriptors. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ticks as TK             # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID = "P-E01", "T-X12"
T = 0.05
VARS = ["empty1", "noise1", "noise2", "noise3", "noise4", "putrep", "noise_inline", "noise_pre", "empty_pre", "ne", "en"]


def classify(d):
    """Response class from the displacement curve (T = %.2f).""" % T
    if max(d[v] for v in VARS) < T:
        return "immune"
    if d["empty1"] >= T:
        return "boundary"          # any tick boundary moves it
    if d["noise1"] >= T:
        return "content"           # a NOISE tick moves it, an empty one does not
    if any(d["noise%d" % n] >= T for n in (2, 3, 4)):
        return "threshold"         # needs more than one tick
    return "other"


def job(j):
    p = j["program"]
    m = A.canonical(p["manifest"])
    base_eps = A.episodes("W0")
    V = TK.w0_variants(base_eps)
    a0 = A.C1.answers(m, V["base"])
    d = {v: A.C1.displacement(A.C1.answers(m, V[v]), a0) for v in VARS}
    ev0 = A.evaluate(m, V["base"], rng_seed=0, reward_mode="per_ask")
    rew = {v: A.evaluate(m, V[v], rng_seed=0, reward_mode="per_ask")["reward_per_ask"] for v in ("noise1", "empty1", "putrep")}
    mono = all(d["noise%d" % n] <= d["noise%d" % (n + 1)] + T for n in (1, 2, 3))
    mp = json.loads(json.dumps(m))
    mp["persist"] = "none"
    ap0 = A.C1.answers(mp, V["base"])
    dp = {"transform": A.C1.displacement(ap0, a0), "noise1": A.C1.displacement(A.C1.answers(mp, V["noise1"]), ap0), "empty1": A.C1.displacement(A.C1.answers(mp, V["empty1"]), ap0)}
    out = {"pid": p["organism_id"], "set": p["stratum"], "n_instr": CM.n_instr(m), "persist": m["persist"], "tick_budget": m["tick_budget"],
           "r0": ev0["reward_per_ask"], "answered": ev0["answered_share"], "tape_writes": ev0["tape_writes_per_episode"],
           "persistent_words": ev0["meter"].get("persistent_state_words"), "occupancy": ev0["tape_occupancy_max"],
           "disp": d, "reward": rew, "class": classify(d), "monotone": mono, "order_sensitive": abs(d["ne"] - d["en"]) >= T,
           "position_sensitive": abs(d["noise_pre"] - d["noise1"]) >= T, "persist_none": dp}
    if j.get("walkers"):
        out["walkers"] = walker_traces(p, m, V, a0)
    return out


def walker_traces(p, m, V, a0):
    env_eps = A.episodes(p["env"])
    res = []
    for w in range(1, 5):
        trace = {}

        def proposal(cur, rng):
            child, rec = A.GR.mutate(cur, rng, mate=None, name=None)
            if "noop" not in (rec.get("args") or {}):
                trace[A.digest(child)] = child
            return child, rec

        wk = A.C5.walk(m, p["organism_id"], w, env_eps, 16, 32, proposal=proposal)
        sens, mans = [], [m]
        for s in wk["steps"]:
            c = trace.get(s["digest"])
            mans.append(c)
            sens.append(A.C1.displacement(A.C1.answers(c, V["noise1"]), A.C1.answers(c, V["base"])) if c is not None else None)
        base_sens = A.C1.displacement(A.C1.answers(m, V["noise1"]), a0)
        onset, revert = None, None
        prev = base_sens
        for i, s in enumerate(sens):
            if s is not None and prev < 0.10 <= s:
                onset = {"depth": i + 1, "operator": wk["steps"][i]["operator"], "from": prev, "to": s}
                a, b = mans[i], mans[i + 1]
                final = wk["archived"].get(wk["depth"])
                if a is not None and len(a["genome"]) == len(b["genome"]) and final is not None and len(final["genome"]) == len(b["genome"]):
                    pos = [k for k in range(len(a["genome"])) if a["genome"][k] != b["genome"][k]]
                    f2 = json.loads(json.dumps(final))
                    for k in pos:
                        f2["genome"][k] = a["genome"][k]
                    sf = A.C1.displacement(A.C1.answers(final, V["noise1"]), A.C1.answers(final, V["base"]))
                    sr = A.C1.displacement(A.C1.answers(f2, V["noise1"]), A.C1.answers(f2, V["base"]))
                    revert = {"feasible": True, "n_words": len(pos), "final_sens": sf, "final_reverted_sens": sr, "necessary_at_end": sr < 0.10 <= sf}
                else:
                    revert = {"feasible": False, "why": "length changed at or after the onset step"}
                break
            if s is not None:
                prev = s
        res.append({"walker": w, "depth": wk["depth"], "base_sens": base_sens, "sens": sens, "onset": onset, "revert": revert,
                    "final_sens": sens[-1] if sens else base_sens})
    return res


def spearman_perm(x, y, n=2000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 8:
        return None

    def rk(v):
        return np.argsort(np.argsort(v)).astype(float)

    def rho(a, b):
        ra, rb = rk(a), rk(b)
        return float(np.corrcoef(ra, rb)[0, 1])
    obs = rho(x, y)
    rng = np.random.Generator(np.random.PCG64(seed))
    null = np.array([rho(x, rng.permutation(y)) for _ in range(n)])
    return {"rho": obs, "n": int(len(x)), "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)),
            "clears": bool(obs > np.percentile(null, 95) or obs < np.percentile(null, 5))}


def residual(v, X):
    v = np.asarray(v, float)
    beta = np.linalg.lstsq(X, v, rcond=None)[0]
    return v - X @ beta


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(c - h), float(c + h))


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "B", "scope": CM.SCOPE, "claim_type": "parameterized-response-map",
                         "ruler": "self-displacement: answers on a constructed variant vs answers on the base W0 episodes (same program)",
                         "variants": VARS + ["persist=none x {base, noise1, empty1}"], "threshold_T": T,
                         "classes": "immune (all < T) | boundary (empty tick >= T) | content (NOISE tick >= T, empty < T) | threshold (only >= 2 ticks) | other; plus order-sensitive (|ne-en| >= T), position-sensitive (|noise_pre - noise1| >= T), non-monotone",
                         "lineages": "viable parents (all strata), walker-16 (walker 1), C4-08 ordinary top-32 seed 1",
                         "walker_trace": "w0_solver walkers 1-4: self-displacement (noise1) of every accepted step; onset = first step crossing .10; REVERT = restore the onset step's words in the depth-16 final when every later step preserved length",
                         "cross_observable": "Spearman(tick sensitivity noise1, mean P-D01 delete loss per program) with a 2000-permutation null; partial on log length and set dummies; also vs tape writes, persistent words, tick budget",
                         "material_rule": "any of: paired sign-flip of (noise1 - empty1) outside its band; class 'not immune' share differs between two sets with non-overlapping Wilson 95% bands; the tick x damage Spearman clears its permutation band",
                         "continuation": ["tick budget as a dose", "state-word census at the onset step", "C5 representation B", "programs evolved under inserted ticks (P-E03 evolver)"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    w0_ids = {q["organism_id"] for q in parents if q["stratum"] == "w0_solver"}
    jobs = [{"program": p, "walkers": bool(p["stratum"] == "parent" and p["organism_id"] in w0_ids)} for p in programs]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    sets = sorted({r["set"] for r in rows})
    # class shares
    shares = {}
    for st in sets:
        rs = [r for r in rows if r["set"] == st]
        cnt = Counter(r["class"] for r in rs)
        k = sum(1 for r in rs if r["class"] != "immune")
        shares[st] = {"n": len(rs), "classes": dict(cnt), "not_immune": k / len(rs), "wilson": wilson(k, len(rs)),
                      "order_sensitive": sum(r["order_sensitive"] for r in rs) / len(rs), "position_sensitive": sum(r["position_sensitive"] for r in rs) / len(rs),
                      "non_monotone": sum(1 for r in rs if not r["monotone"]) / len(rs),
                      "mean_disp": {v: float(np.mean([r["disp"][v] for r in rs])) for v in VARS},
                      "persist_none_noise1": float(np.mean([r["persist_none"]["noise1"] for r in rs])), "persist_none_transform": float(np.mean([r["persist_none"]["transform"] for r in rs]))}
    sf_ne = CM.paired_signflip([r["disp"]["noise1"] - r["disp"]["empty1"] for r in rows])
    sf_inline = CM.paired_signflip([r["disp"]["noise1"] - r["disp"]["noise_inline"] for r in rows])
    sf_pre = CM.paired_signflip([r["disp"]["noise1"] - r["disp"]["noise_pre"] for r in rows])
    sf_persist = CM.paired_signflip([r["disp"]["noise1"] - r["persist_none"]["noise1"] for r in rows])
    by_persist = {}
    for r in rows:
        by_persist.setdefault(r["persist"], []).append(r["disp"]["noise1"])
    by_persist = {k: {"n": len(v), "mean_noise1": float(np.mean(v))} for k, v in by_persist.items()}
    # cross with P-D01 rows
    loss = {}
    pd = HERE.parent / "P-D01" / "rows.json"
    if pd.exists():
        for r in json.loads(pd.read_text(encoding="utf-8")):
            if r["kind"] == "delete" and r["decode"] == "modulo":
                loss.setdefault(r["pid"], []).append(r["loss"])
    loss = {k: float(np.mean(v)) for k, v in loss.items()}
    cross = {}
    paired = [r for r in rows if r["pid"] in loss]
    if len(paired) >= 8:
        x = [r["disp"]["noise1"] for r in paired]
        y = [loss[r["pid"]] for r in paired]
        cross["tick_vs_loss"] = spearman_perm(x, y)
        X = np.column_stack([np.ones(len(paired)), np.log([r["n_instr"] for r in paired])] + [[1.0 if r["set"] == st else 0.0 for r in paired] for st in sets[1:]])
        cross["tick_vs_loss_partial"] = spearman_perm(residual(x, X), residual(y, X))
        for key in ("tape_writes", "persistent_words", "tick_budget", "occupancy", "n_instr"):
            cross["tick_vs_" + key] = spearman_perm(x, [r[key] if r[key] is not None else np.nan for r in paired])
            cross["loss_vs_" + key] = spearman_perm(y, [r[key] if r[key] is not None else np.nan for r in paired])
        cross["n_paired"] = len(paired)
    # walker level
    wl = [w for r in rows if r.get("walkers") for w in r["walkers"]]
    onsets = [w["onset"] for w in wl if w["onset"]]
    reverts = [w["revert"] for w in wl if w["revert"]]
    walker_summary = {"n_walkers": len(wl), "n_onset": len(onsets), "onset_depth_hist": dict(Counter(o["depth"] for o in onsets)), "onset_ops": dict(Counter(o["operator"] for o in onsets)),
                      "revert_feasible": sum(1 for x in reverts if x.get("feasible")), "revert_necessary_at_end": sum(1 for x in reverts if x.get("necessary_at_end")),
                      "final_sens_mean": float(np.mean([w["final_sens"] for w in wl])) if wl else None, "base_sens_mean": float(np.mean([w["base_sens"] for w in wl])) if wl else None,
                      "lost_sensitivity": sum(1 for w in wl if w["base_sens"] >= 0.10 > w["final_sens"]), "gained_sensitivity": sum(1 for w in wl if w["base_sens"] < 0.10 <= w["final_sens"])}
    bands_disjoint = any(shares[a]["wilson"][1] < shares[b]["wilson"][0] or shares[b]["wilson"][1] < shares[a]["wilson"][0] for a in sets for b in sets if a < b)
    material = bool((sf_ne and (sf_ne["above_p95"] or sf_ne["below_p05"])) or bands_disjoint or (cross.get("tick_vs_loss") and cross["tick_vs_loss"]["clears"]))
    out = {"perturbation_id": PID, "parent": TID, "n_programs": len(rows), "shares_by_set": shares, "signflips": {"noise1_minus_empty1": sf_ne, "noise1_minus_inline": sf_inline, "noise1_minus_pre": sf_pre, "noise1_minus_persistnone": sf_persist},
           "by_persist_policy": by_persist, "cross": cross, "walkers": walker_summary, "wilson_bands_disjoint": bands_disjoint, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "tick-content response map: not-immune share by set %s; classes %s; noise1-empty1 %s; noise1-inline %s; pre-PUT %s; persist=none %s; tick x damage-loss rho %s; walkers onset %d/%d revert-necessary %d/%d"
                      % ({k: round(v["not_immune"], 3) for k, v in shares.items()}, {k: v["classes"] for k, v in shares.items()},
                         (round(sf_ne["mean_diff"], 3), sf_ne["above_p95"]) if sf_ne else None, (round(sf_inline["mean_diff"], 3), sf_inline["above_p95"]) if sf_inline else None,
                         (round(sf_pre["mean_diff"], 3), sf_pre["above_p95"] or sf_pre["below_p05"]) if sf_pre else None, (round(sf_persist["mean_diff"], 3), sf_persist["above_p95"] or sf_persist["below_p05"]) if sf_persist else None,
                         (round(cross["tick_vs_loss"]["rho"], 3), cross["tick_vs_loss"]["clears"]) if cross.get("tick_vs_loss") else None,
                         walker_summary["n_onset"], walker_summary["n_walkers"], walker_summary["revert_necessary_at_end"], walker_summary["revert_feasible"]),
                      material, detail={"shares": shares, "cross": cross, "walkers": walker_summary})
    print("DONE material=%s (%.0f s) %s | cross %s | walkers %s" % (material, time.time() - t0, {k: (round(v["not_immune"], 3), v["classes"]) for k, v in shares.items()},
                                                                      {k: (round(v["rho"], 3), v["clears"]) for k, v in cross.items() if isinstance(v, dict)}, walker_summary))


if __name__ == "__main__":
    main()
