"""B48 -- is the update-on-condition wall an INSTRUCTION-SET fact? Switching-evidence world on the SEL VM.

Memory law (B08J/B22b/B40/B45/B47): write-once state is reachable, update-on-condition state is not. In the stock VM a
conditional update needs a branch whose relative offset must land correctly. With B10's SEL opcode
(op 24: r_a = r_a ? r_b : r_c) the STICKY update is straight-line:
    IN r1 ; EQ r4, r1, r2 ; SEL r4, r1, r3 ; MOV r3, r4 ; MOV r2, r1 ; OUT r3 ; HALT     (r2 prev hint, r3 choice)
World: B47 switching evidence (noise .6, switch at tick 16). Evolution on the SEL VM (8 seeds, G=300); scoring on the
SEL VM, E=64 x 4 new world keys. Controls on the SEL VM: SEL_STICKY, REACTIVE, LATCH.
PREDICTION (before running): 0/8 elites beat REACTIVE by >= .025 (the wall is not the branch structure). A positive
result would locate the wall in the instruction set.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, FOUNDRY_C2, REGIMES, TARGET, _prog
from archaeon.beta.b10_select_primitive import SELVM
from archaeon.beta.b43_evidence_world import REACTIVE, _m
from archaeon.beta.b47_switching_evidence import LATCH, world
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
IN, EQ, SEL, MOV, OUT_, HALT = 21, 16, 24, 4, 23, 1
SEL_STICKY = _m(_prog([(IN, 1, 0), (EQ, 4, 1, 2), (SEL, 4, 1, 3), (MOV, 3, 4), (MOV, 2, 1), (OUT_, 3, 0), (HALT,)]))


def sc(m, keys):
    return sum(evaluate_world(m, *world(k), 64, rng_seed=7, player_factory=SELVM.Player)["reward"] for k in keys) / len(keys)


def controls():
    keys = [320, 321, 322, 323]
    return {"SEL_STICKY": round(sc(SEL_STICKY, keys), 4), "REACTIVE": round(sc(REACTIVE, keys), 4), "LATCH": round(sc(LATCH, keys), 4)}


def cell(job):
    EV.Player = SELVM.Player
    w, s = world(0)
    EV.evaluate = lambda m, eps, intervention=None, rng_seed=0, reward_mode="per_ask": evaluate_world(m, w, s, 16, rng_seed=7, player_factory=SELVM.Player)
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, job["seed"], N=200, E=16, branch="b48", foundry=FOUNDRY_C2)
    for g in range(job["G"]):
        ev.evaluate_generation(episodes=[], last=(g == job["G"] - 1))
        if g < job["G"] - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    keys = [330, 331, 332, 333]
    g_ = m["genome"]
    return {"seed": job["seed"], "elite": round(sc(m, keys), 4), "reactive": round(sc(REACTIVE, keys), 4),
            "sel_sticky": round(sc(SEL_STICKY, keys), 4), "persist_none": round(sc(dict(m, persist="none"), keys), 4),
            "elite_sel_instrs": sum(1 for i in range(0, len(g_), 4) if g_[i] % 25 == SEL), "elite_manifest": m}


def main(argv):
    if argv and argv[0] == "controls":
        r = controls(); print(json.dumps(r)); (OUT / "B48_controls.json").write_text(json.dumps(r, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"seed": 4801 + s, "G": G_}): s for s in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 4801 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B48_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    (OUT / "B48_result.json").write_text(json.dumps({"probe": "B48", "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
