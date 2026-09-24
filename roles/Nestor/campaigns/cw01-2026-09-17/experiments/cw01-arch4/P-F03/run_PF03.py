"""P-F03 [T-X17, deformation B]: EVOLUTION UNDER IDLE TICKS and TRANSPLANT.

Arms: selection on W0 and on W2_K2, each with the generation's episodes carrying an idle (empty)
tick at a random position (before an ask / between PUTs / before the first PUT) in half of the
episodes ('idle'), versus plain episodes; 40 generations, 2 seeds, N 96 from the walkers. The raw
temporal response vector (ticks.response_vector, 7 constructions) of the top-32 of every arm.
TRANSPLANT: W0-idle tops seeded into plain W2_K2 selection for 20 generations and W2-idle tops into
plain W0 selection; the vector read again. Computational scope: integer programs on a bounded VM.
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
import evolver as EV           # noqa: E402
import ticks as TK             # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-F03", "T-X17"
SEEDS, G1, G2, TOP = (1, 2), 40, 20, 32
ARMS = [("W0", "plain"), ("W0", "idle"), ("W2_K2", "plain"), ("W2_K2", "idle")]


def idle_transform(env):
    def f(eps, g):
        rng = A.SplitMix64(A.seed_from("nestor.pf03.idle", A.LOOP_SEED, env, g))
        out = []
        for ep in eps:
            if rng.unit() < 0.5:
                which = rng.randbelow(3)
                puts, asks = TK.put_ticks(ep), TK.ask_ticks(ep)
                pos = asks[0] if which == 0 else (puts[1] if (which == 1 and len(puts) > 1) else puts[0])
                out.append(TK.insert(ep, pos, [[]]))
            else:
                out.append(TK.clone(ep))
        return out
    return f


def evo_job(j):
    r = EV.run("select", j["seed"], j["init"], G_=j["G"], env=j["env"], ep_transform=(idle_transform(j["env"]) if j["mode"] == "idle" else None), label=j["label"])
    tops = sorted(r["final"], key=lambda x: -x["reward"])[:TOP]
    vecs = [TK.response_vector(x["m"]) for x in tops]
    return {"env": j["env"], "mode": j["mode"], "seed": j["seed"], "stage": j["stage"], "tops": [{"m": x["m"], "reward": x["reward"], "anc": x["anc"]} for x in tops],
            "vectors": [v["vector"] for v in vecs], "answered": [v["answered"] for v in vecs], "reward_mean": r["history"][-1]["reward_mean"], "len_mean": r["history"][-1]["len_mean"]}


def centroid(vs):
    a = np.array(vs, float)
    return np.nanmean(a, axis=0).tolist() if len(a) else None


def dist(a, b):
    a, b = np.array(a, float), np.array(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.mean(np.abs(a[ok] - b[ok]))) if ok.any() else float("nan")


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "B", "scope": CM.SCOPE, "claim_type": "evolution-transplant",
                         "arms": ARMS, "generations": G1, "transplant_generations": G2, "seeds": SEEDS, "idle": "half the episodes get one empty tick at a random position (before ask / between PUTs / before first PUT)",
                         "vector": TK.VECTOR_KEYS, "ruler": "L1 distance between 7-vectors (NaN components skipped); nearest-centroid assignment",
                         "reading_rules": {"TRAVELS": "after transplant, >= 2/3 of tops stay nearest the ORIGIN arm's centroid", "RECONSTRUCTED": ">= 2/3 nearest the HOST world's plain-arm centroid", "MIXED": "otherwise"},
                         "material_rule": "idle vs plain centroids differ by >= .10 L1 in either world, OR the transplant reading is TRAVELS or RECONSTRUCTED",
                         "continuation": ["longer transplant", "idle probability dose", "single-program neutral walk in the host world"], "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    init, _ = EV.init_population()
    jobs = [{"env": e, "mode": m, "seed": s, "init": init, "G": G1, "stage": "evolve", "label": "nestor.pf03"} for e, m in ARMS for s in SEEDS]
    with A.pool(8) as ex:
        runs = list(ex.map(evo_job, jobs))
    by = {(r["env"], r["mode"], r["seed"]): r for r in runs}
    # transplant: W0-idle tops -> W2 plain; W2-idle tops -> W0 plain (each seed), populations = tops repeated to N
    tj = []
    for s in SEEDS:
        for src, host in (("W0", "W2_K2"), ("W2_K2", "W0")):
            tops = by[(src, "idle", s)]["tops"]
            pop = [{"m": t["m"], "anc": i % len(tops), "anc_parent": None, "anc_stratum": None, "anc_walker": None} for i, t in enumerate([tops[i % len(tops)] for i in range(EV.N)])]
            tj.append({"env": host, "mode": "plain", "seed": s, "init": pop, "G": G2, "stage": "transplant_from_" + src, "label": "nestor.pf03.transplant"})
    with A.pool(4) as ex:
        trans = list(ex.map(evo_job, tj))
    cents = {"%s|%s" % (e, m): centroid([v for r in runs if r["env"] == e and r["mode"] == m for v in r["vectors"]]) for e, m in ARMS}
    idle_effect = {e: dist(cents["%s|idle" % e], cents["%s|plain" % e]) for e in ("W0", "W2_K2")}
    readings = {}
    for r in trans:
        src = r["stage"].replace("transplant_from_", "")
        origin, host = cents["%s|idle" % src], cents["%s|plain" % r["env"]]
        stay = sum(1 for v in r["vectors"] if dist(v, origin) < dist(v, host))
        n = len(r["vectors"])
        readings["%s->%s|s%d" % (src, r["env"], r["seed"])] = {"stay_origin": stay, "n": n, "reading": "TRAVELS" if stay >= 2 * n / 3 else "RECONSTRUCTED" if stay <= n / 3 else "MIXED",
                                                              "centroid_after": centroid(r["vectors"]), "d_origin": dist(centroid(r["vectors"]), origin), "d_host": dist(centroid(r["vectors"]), host)}
    overall = [v["reading"] for v in readings.values()]
    material = bool(any(x >= 0.10 for x in idle_effect.values() if np.isfinite(x)) or any(x in ("TRAVELS", "RECONSTRUCTED") for x in overall))
    out = {"perturbation_id": PID, "parent": TID, "centroids": cents, "idle_minus_plain_L1": idle_effect, "transplant": readings, "vector_keys": TK.VECTOR_KEYS,
           "runs": [{k: v for k, v in r.items() if k != "tops"} for r in runs + trans], "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{"env": r["env"], "mode": r["mode"], "seed": r["seed"], "stage": r["stage"], "tops": r["tops"]} for r in runs + trans], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "evolution under idle ticks: centroids %s; idle-plain L1 %s; transplant %s"
                      % ({k: [round(x, 2) if x == x else None for x in v] for k, v in cents.items()}, {k: round(v, 3) for k, v in idle_effect.items()}, {k: (v["reading"], v["stay_origin"], v["n"], round(v["d_origin"], 3), round(v["d_host"], 3)) for k, v in readings.items()}),
                      material, detail={"centroids": cents, "transplant": readings})
    print("DONE material=%s (%.0f s) idle effect %s | transplant %s" % (material, time.time() - t0, idle_effect, {k: v["reading"] for k, v in readings.items()}))


if __name__ == "__main__":
    main()
