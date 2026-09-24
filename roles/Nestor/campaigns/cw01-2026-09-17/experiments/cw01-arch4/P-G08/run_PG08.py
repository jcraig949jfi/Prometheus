"""P-G08 [T-R01, anti-gravity; requires P-G01]: DOES THE SCATTERED RULER HAVE ITS OWN GEOMETRY? Five rulers
at f .10 on the same programs: (i) scattered Bernoulli delete; (ii) exact-count scattered delete; (iii)
contiguous window of round(f n); (iv) scattered delete restricted to REACHED instructions; (v) scattered
DISABLE (opcode := NOP). For each: the log-length slope of loss, the set effect (tops vs rest), and the
mean loss. Computational scope: integer programs on a bounded VM.
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
import gate                    # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops, damage, windows, reduced_class   # noqa: E402

PID, TID, F, DRAWS = "P-G08", "T-R01", 0.10, 4
RULERS = ("bernoulli", "exact_count", "contiguous", "reached_only", "disable")


def child_for(pm, ruler, key, n, reach):
    rng = A.SplitMix64(A.seed_from("nestor.pg08", A.LOOP_SEED, *key))
    if ruler == "bernoulli":
        return SC.apply(pm, SC.mask(n, F, key), "delete", key)
    if ruler == "disable":
        return SC.apply(pm, SC.mask(n, F, key), "nop", key)
    k = max(1, int(round(F * n)))
    if ruler == "exact_count":
        idx = set()
        while len(idx) < k:
            idx.add(int(rng.next_u32() % n))
        return SC.apply(pm, [i in idx for i in range(n)], "delete", key)
    if ruler == "contiguous":
        return damage(pm, "delete", windows(n, k, 1, "even", rng), rng, "modulo")
    if ruler == "reached_only":
        el = [i for i in range(n) if reach[i]]
        if not el:
            return None
        msk = [False] * n
        r2 = A.SplitMix64(A.seed_from("nestor.pg08.reached", A.LOOP_SEED, *key))
        for i in el:
            msk[i] = r2.unit() < F
        return SC.apply(pm, msk, "delete", key)
    raise ValueError(ruler)


def job(j):
    p = j["program"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    n = CM.n_instr(pm)
    pev = A.eval_all(pm, {env: eps})
    if pev[env]["answered_share"] == 0.0 or n < 4:
        return {"pid": p["organism_id"], "skipped": True}
    reach = SC.reach_map(pm, eps)
    out = {"pid": p["organism_id"], "set": p["stratum"], "n_instr": n, "reached_share": float(np.mean(reach)), "loss": {}, "dreward": {}, "skipped": False}
    for ruler in RULERS:
        ls, drs = [], []
        for d in range(1, DRAWS + 1):
            c = child_for(pm, ruler, (p["organism_id"], ruler, d), n, reach)
            if c is None:
                continue
            cev = A.eval_all(c, {env: eps})
            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
            ls.append(int(reduced_class(cev, pev, disp, env) in ("D2", "D3")))
            drs.append(cev[env]["reward_per_ask"] - pev[env]["reward_per_ask"])
        out["loss"][ruler] = float(np.mean(ls)) if ls else None
        out["dreward"][ruler] = float(np.mean(drs)) if drs else None
    return out


def perm_slope(x, y, n=2000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    b = float(np.polyfit(x, y, 1)[0])
    rng = np.random.Generator(np.random.PCG64(seed))
    null = np.array([np.polyfit(rng.permutation(x), y, 1)[0] for _ in range(n)])
    return {"slope": b, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)), "outside": bool(b < np.percentile(null, 5) or b > np.percentile(null, 95))}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-G01"], "scope": CM.SCOPE, "claim_type": "ruler-deformation", "f": F, "draws": DRAWS, "rulers": RULERS,
                         "readouts": "per ruler: mean loss, log-length slope (permutation band), set effect tops vs rest (relabel), for loss and for absolute reward change",
                         "reading": "RULER_DEPENDENT if the length slope or the set effect differs in significance or sign between (i) and any of (ii), (iv), (v); (iii) is the known-dilution reference",
                         "material_rule": "RULER_DEPENDENT, or (iii) differs from (i) as D084 predicts (a positive control on the ruler defect)", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    gate.require_qualified(HERE, PID, TID, ph)
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = [r for r in ex.map(job, [{"program": p} for p in programs]) if not r.get("skipped")]
    lens = np.log([r["n_instr"] for r in rows])
    table = {}
    for ruler in RULERS:
        ok = [r for r in rows if r["loss"].get(ruler) is not None]
        y = [r["loss"][ruler] for r in ok]
        yd = [r["dreward"][ruler] for r in ok]
        tops = [r["loss"][ruler] for r in ok if r["set"] == "c408_ordinary"]
        rest = [r["loss"][ruler] for r in ok if r["set"] != "c408_ordinary"]
        table[ruler] = {"n": len(ok), "mean_loss": float(np.mean(y)), "mean_dreward": float(np.mean(yd)), "length_slope": perm_slope(np.log([r["n_instr"] for r in ok]), y), "length_slope_dreward": perm_slope(np.log([r["n_instr"] for r in ok]), yd),
                        "set_effect": L.relabel_diff(rest, tops)}
    ref = table["bernoulli"]

    def sig(t):
        return (t["length_slope"]["outside"], int(np.sign(t["length_slope"]["slope"])), t["set_effect"]["below_p05"] or t["set_effect"]["above_p95"], int(np.sign(t["set_effect"]["effect"])))
    dependent = [r for r in ("exact_count", "reached_only", "disable") if sig(table[r]) != sig(ref)]
    positive_control = sig(table["contiguous"]) != sig(ref)
    material = bool(dependent or positive_control)
    out = {"perturbation_id": PID, "parent": TID, "table": table, "ruler_dependent_vs_bernoulli": dependent, "contiguous_differs_from_bernoulli": positive_control, "reading": "RULER_DEPENDENT" if dependent else "RULER_INVARIANT_ACROSS_SCATTERED_VARIANTS",
           "n_programs": len(rows), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "ruler geometry variants at f .10: %s; reading %s (dependent: %s; contiguous differs: %s)"
                      % ({k: (round(v["mean_loss"], 3), round(v["length_slope"]["slope"], 3), v["length_slope"]["outside"], round(v["set_effect"]["effect"], 3), v["set_effect"]["below_p05"]) for k, v in table.items()}, out["reading"], dependent, positive_control),
                      material, detail={"table": {k: {"mean_loss": v["mean_loss"], "slope": v["length_slope"], "set": {a: b for a, b in v["set_effect"].items() if a in ("effect", "below_p05", "above_p95")}} for k, v in table.items()}})
    print("DONE %s dependent=%s contiguous_differs=%s (%.0f s) %s" % (out["reading"], dependent, positive_control, time.time() - t0, {k: (round(v["mean_loss"], 3), round(v["length_slope"]["slope"], 3), v["length_slope"]["outside"]) for k, v in table.items()}))


if __name__ == "__main__":
    main()
