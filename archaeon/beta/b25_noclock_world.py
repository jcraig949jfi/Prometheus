"""B25 -- composed worlds WITHOUT the clock: does content sensing pay, and does it evolve? (world redesign)

B23/B24: the frontier's surviving composed-world competence is a clock-vs-position lap counter; nothing sensed the
world's CONTENT. Redesign: wrap a ComposedWorld so observe() drops words 0-1 (tick, position). Everything else
(pools, cells, hazard, signal; dynamics; reward) is unchanged.
Controls, on the P-boom_K_D_persist_s3 world (12-node ring, 3 pools, lethal hazards, history, coupling, K=4):
  CONTENT  hand policy: read the three local pool words; harvest the first non-empty pool, else move +1
  CONSTANT best fixed-output program (B23b grid);  ECHO best echo twin (B23c)
  SWEEP    the evolved clock-vs-position elite, on the CLOCK world (its home) and on the NOCLOCK world
This file holds the wrapper and the controls; the evolution arms (B25 EXP) run under a lease in the budget window.
"""
import gzip
import json
import sys
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import _prog, IN, JZ, LDC, OUT_, HALT
from archaeon.beta.b23b_composed_world_audit import RUNS, CONSTS, constant_manifest, score
from archaeon.beta.b23c_attack_artifacts import echo_manifest
from archaeon.campaign6.segment import resolve_world

OUT = Path(__file__).resolve().parent / "results"
NAME = "P-boom_K_D_persist_s3"


class NoClock:
    def __init__(self, w):
        self.w = w; self.K = w.K; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        return [ch[2:] for ch in self.w.observe(st)]


CONTENT = _prog([(IN, 1, 0), (IN, 2, 0), (IN, 3, 0),
                 (JZ, 1, 3), (OUT_, 0, 0), (HALT,),
                 (JZ, 2, 4), (LDC, 4, 1), (OUT_, 4, 0), (HALT,),
                 (JZ, 3, 4), (LDC, 4, 2), (OUT_, 4, 0), (HALT,),
                 (LDC, 5, 1), (OUT_, 0, 5), (HALT,)])


def content_manifest():
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 6, "tape_words": 128, "genome": CONTENT,
            "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 1}


def load():
    exp = [f / NAME for f in RUNS.iterdir() if (f / NAME).is_dir()][0]
    c = json.load(gzip.open(sorted(exp.glob("chunk_*.json.gz"))[-1]))
    world = resolve_world(c["spec"]["world"]); seed = c["spec"].get("provenance", {}).get("seed", 0) or 0
    elite = max(((score(o["manifest"], world, seed), o["manifest"]) for o in c["out"]["checkpoint_out"]["population"]), key=lambda z: z[0])[1]
    return world, seed, elite


def controls():
    world, seed, elite = load()
    nc = NoClock(world)
    out = {}
    for name, w in (("CLOCK", world), ("NOCLOCK", nc)):
        n_in = len(w.observe(w.reset(seed, 0, None))[0])
        out[name] = {"content": round(score(content_manifest(), w, seed), 4),
                     "constant": round(max(score(constant_manifest(v, w.K), w, seed) for v in CONSTS), 4),
                     "echo": round(max(score(echo_manifest(0, j, w.K), w, seed) for j in range(min(8, n_in))), 4),
                     "sweep_elite": round(score(elite, w, seed), 4), "obs_words": n_in}
    return out


def _main():
    if len(sys.argv) > 1 and sys.argv[1] == "exp":
        return main_exp(sys.argv[2:])
    r = controls(); print(json.dumps(r))
    OUT.mkdir(exist_ok=True)
    (OUT / "B25_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
    return 0


# ---------------------------------------------------------------- B25 EXP (evolution arms; budget window, leased)
# PREDICTION (written 2026-10-07 ~17:00Z, before any evolution): on NOCLOCK, evolved elites beat the constant twin
# (.076) by >= .05 in >= 3/6 seeds, and their B24-style load-bearing core reads at least one POOL word (content
# sensing); on CLOCK the clock-sweep strategy reappears (elite reads words 0-1) in >= 3/6.
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET  # noqa: E402
from archaeon.campaign6.worlds.runtime import evaluate_world  # noqa: E402
from archaeon.wse import evolve as EV  # noqa: E402


def cell(job):
    world, seed, _ = load()
    w = NoClock(world) if job["arm"] == "NOCLOCK" else world
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": evaluate_world(m, w, seed, 8, rng_seed=7)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=job["N"], E=8, branch="b25", foundry=FOUNDRY_C2)
    best = []
    for g in range(job["G"]):
        row = ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        best.append(round(row["best_reward"], 4))
        if g < job["G"] - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    return {"arm": job["arm"], "seed": job["seed"], "elite": round(score(elite, w, seed), 4),
            "constant": round(max(score(constant_manifest(v, w.K), w, seed) for v in CONSTS), 4),
            "trace_best": best, "elite_manifest": elite}


def main_exp(argv):
    G_ = int(argv[0]) if argv else 200
    workers = int(argv[1]) if len(argv) > 1 else 12
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 2501 + s, "G": G_, "N": 200}): (a, s) for s in range(6) for a in ("NOCLOCK", "CLOCK")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, s = futs[f]; r = {"arm": a, "seed": 2501 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B25_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B25_result.json").write_text(json.dumps({"probe": "B25", "G": G_, "controls": controls(), "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
