"""P-H08 [T-X17, anti-gravity]: IS 'HERITABLE ALONG NEUTRAL WALKS' JUST EDIT ROBUSTNESS? Random UNFILTERED
mutants at 4 / 8 / 16 grammar operations (8 draws) vs the neutral walkers at the same depths (4 walkers)
for representatives of every geometry: shares keeping the geometry and keeping reward. Computational
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

PID, TID = "P-H08", "T-X17"
SHAPES = {0: "start_anchored", 4: "periodic", 5: "ask_time", 1: "schedule"}
DEPTHS, BAND = (4, 8, 16), A.C1.BAND


def job(j):
    m = A.canonical(j["manifest"])
    eps = A.episodes(j["env"])
    v0 = MF.curve(m)[0]
    r0 = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    out = {"pid": j["pid"], "shape": j["shape"], "unfiltered": {}, "neutral": {}}
    for k in DEPTHS:
        keep, rew = [], []
        for d in range(8):
            rng = A.SplitMix64(A.seed_from("nestor.ph08", A.LOOP_SEED, j["pid"], k, d))
            cur = m
            for _ in range(k):
                for _try in range(8):
                    try:
                        cur, _ = A.GR.mutate(cur, rng, mate=None, name=None)
                        break
                    except A.ManifestError:
                        continue
            try:
                v = MF.curve(cur)[0]
                r = A.evaluate(cur, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            except Exception:      # noqa: BLE001
                continue
            keep.append(MF.dist(v, v0) < 0.2)
            rew.append(r >= r0 - BAND)
        out["unfiltered"][str(k)] = {"n": len(keep), "keep_shape": float(np.mean(keep)) if keep else None, "keep_reward": float(np.mean(rew)) if rew else None}
    for k in DEPTHS:
        out["neutral"][str(k)] = {"keep_shape": [], "keep_reward": []}
    for w in range(1, 5):
        wk = A.C5.walk(m, j["pid"], w, eps, 16, 32)
        for k in DEPTHS:
            mm = wk["archived"].get(k)
            if mm is None:
                continue
            v = MF.curve(mm)[0]
            r = A.evaluate(mm, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            out["neutral"][str(k)]["keep_shape"].append(MF.dist(v, v0) < 0.2)
            out["neutral"][str(k)]["keep_reward"].append(r >= r0 - BAND)
    for k in DEPTHS:
        d = out["neutral"][str(k)]
        out["neutral"][str(k)] = {"n": len(d["keep_shape"]), "keep_shape": float(np.mean(d["keep_shape"])) if d["keep_shape"] else None, "keep_reward": float(np.mean(d["keep_reward"])) if d["keep_reward"] else None}
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-G11"], "scope": CM.SCOPE, "claim_type": "anti-gravity", "shapes": SHAPES, "representatives": 8, "depths": DEPTHS, "unfiltered_draws": 8, "neutral_walkers": 4,
                         "keep_shape": "curve distance to the representative's own curve < .2", "keep_reward": "reward within the band of the representative's",
                         "reading": "EDIT_ROBUSTNESS if unfiltered mutants keep the shape within .15 of the neutral walkers' share at depth 16 for every shape; NEUTRALITY_PRESERVES if neutral walkers keep it by >= .25 more in >= 2 shapes; MIXED otherwise",
                         "material_rule": "the reading is EDIT_ROBUSTNESS (the heritability claim is not about neutrality) or NEUTRALITY_PRESERVES", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"pid": r["organism_id"], "shape": SHAPES[c], "manifest": r["manifest"], "env": r["env"]} for c in SHAPES for r in MF.representatives(c, 8)]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    table = {}
    for sh in SHAPES.values():
        rs = [r for r in rows if r["shape"] == sh]
        table[sh] = {}
        for k in DEPTHS:
            u = [r["unfiltered"][str(k)] for r in rs if r["unfiltered"][str(k)]["keep_shape"] is not None]
            n = [r["neutral"][str(k)] for r in rs if r["neutral"][str(k)]["keep_shape"] is not None]
            table[sh][str(k)] = {"unfiltered_keep_shape": float(np.mean([x["keep_shape"] for x in u])) if u else None, "unfiltered_keep_reward": float(np.mean([x["keep_reward"] for x in u])) if u else None,
                                 "neutral_keep_shape": float(np.mean([x["keep_shape"] for x in n])) if n else None, "neutral_keep_reward": float(np.mean([x["keep_reward"] for x in n])) if n else None}
    gaps = {sh: (v["16"]["neutral_keep_shape"] or 0) - (v["16"]["unfiltered_keep_shape"] or 0) for sh, v in table.items()}
    if all(abs(g) <= 0.15 for g in gaps.values()):
        reading = "EDIT_ROBUSTNESS"
    elif sum(1 for g in gaps.values() if g >= 0.25) >= 2:
        reading = "NEUTRALITY_PRESERVES"
    else:
        reading = "MIXED"
    material = reading in ("EDIT_ROBUSTNESS", "NEUTRALITY_PRESERVES")
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "gaps_at_16": gaps, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "heritability vs edit robustness: reading %s; gaps at depth 16 (neutral - unfiltered keep-shape) %s; table %s" % (reading, {k: round(v, 2) for k, v in gaps.items()}, {sh: {k: (round(x["unfiltered_keep_shape"], 2) if x["unfiltered_keep_shape"] is not None else None, round(x["neutral_keep_shape"], 2) if x["neutral_keep_shape"] is not None else None) for k, x in v.items()} for sh, v in table.items()}), material, detail=table)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, gaps))


if __name__ == "__main__":
    main()
