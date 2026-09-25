"""P-H10 [T-ARCH5 x T-X17, serendipity]: REPRESENTATION CHANGE - neutral walks under Campaign 5's grammar B
(archaeon.campaign5.repb.grammar_b.mutate_b; same VM, different operator set) from representatives of
every geometry; the share keeping the geometry and reward vs the grammar-v0.4 walkers. Computational
scope: integer programs on a bounded VM.
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
import manifold as MF          # noqa: E402
A, L = CM.A, CM.L
try:
    from archaeon.campaign5.repb import grammar_b as GB
    GB_OK, GB_ERR = True, None
except Exception as e:          # noqa: BLE001
    GB, GB_OK, GB_ERR = None, False, repr(e)[:120]

PID, TID = "P-H10", "T-ARCH5"
SHAPES = {0: "start_anchored", 4: "periodic", 5: "ask_time", 1: "schedule"}
DEPTHS, BAND, MAXP = (4, 8, 16), A.C1.BAND, 32


def walk_b(m, org, w, eps):
    rng = A.SplitMix64(A.seed_from("nestor.ph10", A.LOOP_SEED, org, w))
    r0 = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    cur, d, archived = m, 0, {}
    while d < 16:
        acc, tries = None, 0
        while tries < MAXP:
            try:
                child, rec = GB.mutate_b(cur, rng, None, None)
            except Exception:          # noqa: BLE001
                tries += 1
                continue
            if isinstance(rec, dict) and "noop" in (rec.get("args") or {}):
                continue
            tries += 1
            try:
                r = A.evaluate(child, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            except Exception:          # noqa: BLE001
                continue
            if abs(r - r0) <= BAND:
                acc = child
                break
        if acc is None:
            break
        cur, d = acc, d + 1
        if d in DEPTHS:
            archived[d] = json.loads(json.dumps(cur))
    return {"depth": d, "archived": archived, "r0": r0}


def job(j):
    m = A.canonical(j["manifest"])
    eps = A.episodes(j["env"])
    v0 = MF.curve(m)[0]
    out = {"pid": j["pid"], "shape": j["shape"], "B": {str(k): [] for k in DEPTHS}, "A": {str(k): [] for k in DEPTHS}, "depth_B": [], "depth_A": []}
    for w in (1, 2):
        wb = walk_b(m, j["pid"], w, eps)
        out["depth_B"].append(wb["depth"])
        for k, mm in wb["archived"].items():
            v = MF.curve(mm)[0]
            r = A.evaluate(mm, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            out["B"][str(k)].append({"keep_shape": MF.dist(v, v0) < 0.2, "keep_reward": r >= wb["r0"] - BAND})
        wa = A.C5.walk(m, j["pid"], w, eps, 16, MAXP)
        out["depth_A"].append(wa["depth"])
        for k in DEPTHS:
            mm = wa["archived"].get(k)
            if mm is None:
                continue
            v = MF.curve(mm)[0]
            r = A.evaluate(mm, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            out["A"][str(k)].append({"keep_shape": MF.dist(v, v0) < 0.2, "keep_reward": r >= wa["r0"] - BAND})
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X17"], "scope": CM.SCOPE, "claim_type": "serendipity-representation", "grammar_b_available": GB_OK, "shapes": SHAPES, "representatives": 8, "depths": DEPTHS, "walkers": 2,
                         "walk": "band acceptance in the home world; proposals from grammar B (mutate_b) vs grammar v0.4 (C4-05 walk)", "keep_shape": "curve distance < .2", "keep_reward": "within band of r0",
                         "reading": "REPRESENTATION_INVARIANT if grammar-B walkers keep the shape within .15 of grammar-A walkers at depth 16 for every shape; REPRESENTATION_IS_A_COORDINATE if they differ by >= .25 in >= 2 shapes; MIXED otherwise; NOT_RUNNABLE if grammar B does not import",
                         "material_rule": "the reading is not MIXED", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    if not GB_OK:
        out = {"perturbation_id": PID, "parent": TID, "reading": "NOT_RUNNABLE", "why": GB_ERR, "material": False, "elapsed_s": round(time.time() - t0, 1)}
        L.result(HERE, out, ph)
        L.append_evidence(TID, PID, "grammar B not importable (%s): NOT_RUNNABLE (infrastructure, not a disposition)" % GB_ERR, False)
        print("NOT_RUNNABLE", GB_ERR)
        return
    jobs = [{"pid": r["organism_id"], "shape": SHAPES[c], "manifest": r["manifest"], "env": r["env"]} for c in SHAPES for r in MF.representatives(c, 8)]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    table = {}
    for sh in SHAPES.values():
        rs = [r for r in rows if r["shape"] == sh]
        table[sh] = {"depth_B": float(np.mean([d for r in rs for d in r["depth_B"]])), "depth_A": float(np.mean([d for r in rs for d in r["depth_A"]]))}
        for k in DEPTHS:
            b = [x for r in rs for x in r["B"][str(k)]]
            a = [x for r in rs for x in r["A"][str(k)]]
            table[sh][str(k)] = {"B_keep_shape": float(np.mean([x["keep_shape"] for x in b])) if b else None, "A_keep_shape": float(np.mean([x["keep_shape"] for x in a])) if a else None,
                                 "B_keep_reward": float(np.mean([x["keep_reward"] for x in b])) if b else None, "A_keep_reward": float(np.mean([x["keep_reward"] for x in a])) if a else None, "nB": len(b), "nA": len(a)}
    gaps = {sh: ((v["16"]["B_keep_shape"] or 0) - (v["16"]["A_keep_shape"] or 0)) if v["16"]["B_keep_shape"] is not None and v["16"]["A_keep_shape"] is not None else None for sh, v in table.items()}
    g = [x for x in gaps.values() if x is not None]
    reading = "REPRESENTATION_INVARIANT" if g and all(abs(x) <= 0.15 for x in g) else "REPRESENTATION_IS_A_COORDINATE" if sum(1 for x in g if abs(x) >= 0.25) >= 2 else "MIXED"
    material = reading != "MIXED"
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "gaps_at_16": gaps, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "grammar B walks: reading %s; gaps at 16 (B - A keep-shape) %s; depths B/A %s" % (reading, {k: (round(v, 2) if v is not None else None) for k, v in gaps.items()}, {sh: (round(v["depth_B"], 1), round(v["depth_A"], 1)) for sh, v in table.items()}), material, detail=table,
                      state="ACTIVE", state_reason="reactivated through a representation read of the temporal geometries")
    L.append_evidence("T-X17", PID, "cross: representation invariance reads %s" % reading, material)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, gaps))


if __name__ == "__main__":
    main()
