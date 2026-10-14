"""B82 -- why does H_6913 convert to RESET 5/6 but H_6923 only 1/6? Mutation-neighbourhood census (evaluation only, 1 process).

B80+B81: conversion is a property of specific latch genomes, not of quality, length or persist mode (H_6913 .139 -> 5/6;
H_6923 .120 -> 1/6; low control L_6916 0/6).
Hypothesis: H_6913 lies closer to RESET in the search's own mutation space.
For each latch, sample 1000 one-step and 1000 two-step mutants with the search's operator
(proteus.foundry.lineage.descend, as used by CMP3), and screen every mutant in the relocating pulse world. Screening:
solo, 2 world seeds x 8 episodes. Mutants that beat their parent on the screen are re-scored on held-out seeds
(4 x 16) and classified RESET-like (full state dependence >= .02 AND re-find >= .31).
Readouts per latch and step: share of mutants that improve on the parent (held-out); number RESET-like.
PREDICTION (committed before running): H_6913 has MORE RESET-like mutants than H_6923 at step 1 or 2 (strictly more in
the sum over both steps), and L_6916 has the fewest.
"""
import copy
import json
import sys
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc
import archaeon.beta.b75_reset_evolution as B75
from archaeon.beta.b80_latch_quality import latch_genome

OUT = Path(__file__).resolve().parent / "results" / "B82_neighbourhood"
LATCHES = ("H_6913", "H_6923", "L_6916")


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    N = int(argv[0]) if argv else 1000
    world, s, _ = B75.load(); w = NoClock(world)
    screen = lambda m: sum(group_reloc([m], w, s + 2000 + k, 8, P=4, Q=16, mode="random")[0] for k in range(2)) / 2
    held = lambda m: sum(group_reloc([m], w, s + 1000 + k, 16, P=4, Q=16, mode="random")[0] for k in range(4)) / 4
    rows = []
    for key in LATCHES:
        m0, _ = latch_genome(key); rec0 = G.organism_record(copy.deepcopy(m0), None, 0)
        p_screen = screen(m0); p_held = held(m0)
        for step in (1, 2):
            rng = SplitMix64(seed_from("b82", key, step)); improved = 0; reset_like = 0; best = p_held
            for i in range(N):
                child, _ = descend(rec0, rng.next_u64() & ((1 << 62) - 1))
                if step == 2:
                    child, _ = descend(child, rng.next_u64() & ((1 << 62) - 1))
                m = child["manifest"]
                if screen(m) <= p_screen:
                    continue
                r = held(m)
                if r <= p_held:
                    continue
                improved += 1; best = max(best, r)
                lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
                if r - held(lk) >= .02:
                    rf = B75.refind(m, w, s, world.R)
                    reset_like += bool(rf is not None and rf >= .31)
            row = {"latch": key, "step": step, "n": N, "parent_held": round(p_held, 4), "improved": improved, "reset_like": reset_like, "best": round(best, 4)}
            rows.append(row); print(json.dumps(row), flush=True)
    (OUT / "B82_result.json").write_text(json.dumps({"probe": "B82", "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
