"""B40 -- the distribution lever applied to KEYED MEMORY (after B39 showed it works for foraging).

B39: when the world distribution removes the payoff of world-specific mappings, evolution reaches the general foraging
rule. Keyed memory never got that lever (B03-B22 trained on a fixed K=2 episode structure, where slots and delay lines
pay). B40: every training episode draws K from {1,2,3,4,6} (D=1, 4-bit values, random ask order), with B08K wide
jitter (0-7 NOISE ticks before each ask) so delay lines cannot score. Slot programs cannot scale across K; the
11-instruction indexed store (tape[tag]) scores ~1.0 on every K -- the only general solution.
Arms (N=200, E=20 episodes/generation = 4 per K value, E0, G=400, 4 seeds each):
  C2   FOUNDRY_C2 (gen-0 tapes 16..256)
  BIG  FOUNDRY_BIG (gen-0 tape 4096, persist tape/all; B19)
Readout (held-out, wide jitter, 48 episodes each): K = 1, 2, 3, 4, 6, 8 (8 never trained). GENERAL = K6 >= .90 AND
K8 >= .90. Controls first: hand indexed solver (GENERAL), hand slot solver (fails K >= 3).
PREDICTION (before running): 0/8 GENERAL (the indexed solver stays an isolated peak, B20); best held-out K6 <= .5.
A GENERAL solve would make keyed memory, like foraging, a fact about the training distribution.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, SOLVER, TARGET, manifest
from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.beta.b19_hidden_config_gate import FOUNDRY_BIG
from archaeon.beta.b20_hash_neighbourhood import MANIFEST as INDEXED
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
TRAIN_K = (1, 2, 3, 4, 6)
TEST_K = (1, 2, 3, 4, 6, 8)
SPEC = {k: WorldSpec("W%d_K%d" % (k, k), K=k, value_bits=4) for k in set(TRAIN_K) | set(TEST_K)}


def train_eps(g, seed):
    eps = []
    for k in TRAIN_K:
        eps += episodes_for(SPEC[k], CAMPAIGN_SEED, "train", g * 100003 + seed, 4)
    return wide(eps, ("b40", g, seed))


def profile(m):
    return {"K%d" % k: round(evaluate(m, wide(episodes_for(SPEC[k], CAMPAIGN_SEED, "heldout", 7, 48), ("b40ho", k)), rng_seed=7)["reward"], 4)
            for k in TEST_K}


def controls():
    return {"indexed": profile(INDEXED), "slot_solver": profile(manifest(SOLVER))}


def cell(job):
    fm = FOUNDRY_BIG if job["arm"] == "BIG" else FOUNDRY_C2
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=20, branch="b40", foundry=fm)
    best, checkpoints = [], {}
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=train_eps(g, job["seed"]), last=(g == job["G"] - 1))
        best.append(round(row["best_reward"], 4))
        if g in (99, 199, 299) or g == job["G"] - 1:
            checkpoints[str(g)] = profile(ev.scored[0][1]["manifest"])
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    prof = profile(m)
    return {"arm": job["arm"], "seed": job["seed"], "final": prof, "general": prof["K6"] >= .9 and prof["K8"] >= .9,
            "checkpoints": checkpoints, "max_train": max(best), "elite_manifest": m}


def main(argv):
    if argv and argv[0] == "controls":
        r = controls(); print(json.dumps(r)); return 0
    G_ = int(argv[0]) if argv else 400
    workers = int(argv[1]) if len(argv) > 1 else 8
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 4001 + s, "G": G_}): (a, s) for s in range(4) for a in ("C2", "BIG")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, s = futs[f]; r = {"arm": a, "seed": 4001 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B40_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B40_result.json").write_text(json.dumps({"probe": "B40", "G": G_, "controls": ctl, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
