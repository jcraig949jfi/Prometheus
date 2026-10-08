"""B52 -- is SELF-MODIFYING CODE the route to two-value / update-on-condition memory? Replication of B51's counterexample.

B51 BASE seed 5101 solved jittered-wide L4 (.971 at 64 x 4) with a self-modifying-code state machine: it rewrites its
own genome every tick; forcing code_writable=False drops it to .062. B08J (FOUNDRY_C2, small tapes) had L4 0/8.
Arms (jittered-wide L4_order, CMP3 search, N=200, E=16, G=300, 8 seeds each, held-out 64 x 4):
  WRITABLE  gen 0 = FOUNDRY_BIG with code_writable_weights [0, 1] (all writable; mutation may still flip it)
  LOCKED    gen 0 = FOUNDRY_BIG; every evaluation forces code_writable=False (self-modification impossible)
PREDICTION (before running): WRITABLE >= 2/8 solved and every WRITABLE solver loses >= .5 when locked; LOCKED 0/8.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, REGIMES, TARGET
from archaeon.beta.b19_hidden_config_gate import FOUNDRY_BIG
from archaeon.beta.b51_coupled_pair_mutation import eps, heldout
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
FOUNDRY_WRITABLE = dict(FOUNDRY_BIG, code_writable_weights=[0, 1])
_orig = EV.evaluate


def cell(job):
    arm, seed, G_ = job["arm"], job["seed"], job["G"]
    if arm == "LOCKED":
        EV.evaluate = lambda m, e, intervention=None, rng_seed=0, reward_mode="per_ask": _orig(dict(m, code_writable=False), e, intervention=intervention, rng_seed=rng_seed, reward_mode=reward_mode)
    else:
        EV.evaluate = _orig
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=200, E=16, branch="b52",
                      foundry=FOUNDRY_WRITABLE if arm == "WRITABLE" else FOUNDRY_BIG)
    solved = None
    for g in range(G_):
        row = ev.evaluate_generation(episodes=eps("L4_order", "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        m = ev.scored[0][1]["manifest"]
        mm = dict(m, code_writable=False) if arm == "LOCKED" else m
        if row["best_reward"] >= .9 and heldout(mm, "L4_order") >= .9:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    m = ev.scored[0][1]["manifest"]
    mm = dict(m, code_writable=False) if arm == "LOCKED" else m
    return {"arm": arm, "seed": seed, "solved_gen": solved, "heldout": round(heldout(mm, "L4_order"), 4),
            "heldout_locked": round(heldout(dict(m, code_writable=False), "L4_order"), 4),
            "code_writable": m["code_writable"], "elite_manifest": m}


def main(argv):
    G_ = int(argv[0]) if argv else 300
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 5201 + s, "G": G_}): (a, s) for s in range(8) for a in ("WRITABLE", "LOCKED")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, s = futs[f]; r = {"arm": a, "seed": 5201 + s, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B52_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {a: sum(r.get("arm") == a and r.get("solved_gen") is not None for r in rows) for a in ("WRITABLE", "LOCKED")}
    print(json.dumps(summ), flush=True)
    (OUT / "B52_result.json").write_text(json.dumps({"probe": "B52", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
