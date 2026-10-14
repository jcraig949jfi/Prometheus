"""B84 -- NEUTRAL-NETWORK REACH: does drift distance to an improving RESET predict conversion? (follow-up to the B83 retraction)

B83: one-step RESET-like density does not predict conversion (rho .43). The hand latch (6/6) and H_6929 (7/9) have
zero improving one-step mutants, so they must reach RESET through neutral or near-neutral intermediates.
Instrument, per latch:
- R=12 neutral walks of up to K=15 steps;
- at each step, sample M=40 mutants (lineage.descend);
- a mutant whose screen exceeds the ORIGINAL latch's screen by >= .005 is held-out scored and classified RESET-like
  (full dependence >= .02 AND re-find >= .31; reward > the original latch's held score);
- the walk moves to a uniformly chosen mutant within -.002 of the current screen (near-neutral), if any;
- a walk 'finds' when its first RESET-like improver appears.
Screen = solo relocating pulse, 2 world seeds x 8 episodes.
Readout per latch: fraction of walks that find; mean first-find step.
PREDICTION (committed before running):
- Spearman(find fraction, observed conversion rate) >= .6 over the 10 B83 latches;
- the hand latch and H_6929 find in >= 50% of walks;
- the five zero-rate latches find in <= 25% each.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
from archaeon.beta.b83_density_predicts_rate import RATES, genome, spearman

OUT = Path(__file__).resolve().parent / "results" / "B84_neutral"
MASK62 = (1 << 62) - 1


def cell(job):
    key, R, K, M = job["latch"], job["R"], job["K"], job["M"]
    world, s, _ = B75.load(); w = NoClock(world)
    screen = lambda m: sum(group_reloc([m], w, s + 2000 + k, 8, P=4, Q=16, mode="random")[0] for k in range(2)) / 2
    held = lambda m: sum(group_reloc([m], w, s + 1000 + k, 16, P=4, Q=16, mode="random")[0] for k in range(4)) / 4
    m0 = genome(key); rec0 = G.organism_record(copy.deepcopy(m0), None, 0); s0, h0 = screen(m0), held(m0)
    finds = []
    for walk in range(R):
        rng = SplitMix64(seed_from("b84", key, walk)); cur, cs = rec0, s0; found = None
        for step in range(K):
            neutral = []
            for _ in range(M):
                child, _ = descend(cur, rng.next_u64() & MASK62); m = child["manifest"]; sc = screen(m)
                if sc >= s0 + .005:
                    r = held(m)
                    if r > h0:
                        lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
                        if r - held(lk) >= .02:
                            rf = B75.refind(m, w, s, world.R)
                            if rf is not None and rf >= .31:
                                found = step; break
                if sc >= cs - .002:
                    neutral.append((child, sc))
            if found is not None or not neutral:
                break
            cur, cs = neutral[rng.randbelow(len(neutral))]
        finds.append(found)
    hits = [f for f in finds if f is not None]
    return {"latch": key, "R": R, "K": K, "M": M, "find_fraction": round(len(hits) / R, 3),
            "mean_first_step": round(sum(hits) / len(hits), 2) if hits else None, "finds": finds,
            "rate": round(RATES[key][0] / RATES[key][1], 3)}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    R, K, M = (int(argv[0]), int(argv[1]), int(argv[2])) if len(argv) >= 3 else (12, 15, 40)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[3]) if len(argv) > 3 else 10) as ex:
        futs = {ex.submit(cell, {"latch": k, "R": R, "K": K, "M": M}): k for k in RATES}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"latch": futs[f], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B84_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    ok = [r for r in rows if "find_fraction" in r]
    rho = spearman([r["find_fraction"] for r in ok], [r["rate"] for r in ok])
    byk = {r["latch"]: r for r in ok}
    summ = {"spearman": round(rho, 3),
            "hand_and_6929_ge_.5": all(byk.get(k, {}).get("find_fraction", 0) >= .5 for k in ("HAND_LATCH", "H_6929")),
            "zero_rate_le_.25": all(r["find_fraction"] <= .25 for r in ok if r["rate"] == 0)}
    summ["pred_rho"] = summ["spearman"] >= .6
    print(json.dumps(summ))
    (OUT / "B84_result.json").write_text(json.dumps({"probe": "B84", "R": R, "K": K, "M": M, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
