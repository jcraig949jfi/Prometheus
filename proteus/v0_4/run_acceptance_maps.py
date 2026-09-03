"""Acceptance-rate maps for coupled structural operators (V0.4 brief section 9).

For each structural operator, the probability that it actually CHANGES the manifest, conditional
on (genome_length, tape_words). The question is not whether marginal drift is zero but whether
some region of state space systematically permits one direction of a reversible-looking operation
while suppressing its reverse. Measured on the live operators, not modelled.

    python proteus/v0_4/run_acceptance_maps.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.foundry.vm import SCHEMA  # noqa: E402
from proteus.v0_4 import nc5  # noqa: E402

IW = 4
OPS = ("insertion", "deletion", "duplication", "splice", "unreachable_removal",
       "movement", "region_swap", "config_perturbation")
TRIALS = 400


def make(rng, L, T):
    return {"schema_version": SCHEMA, "n_regs": 8, "tape_words": T,
            "genome": [rng.next_u32() for _ in range(IW * L)],
            "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 4}


def main():
    rng = SplitMix64(seed_from("proteus.v0_4.acceptance", 20260904))
    grid = []
    for T in nc5.TAPES:
        cap = T // IW
        for L in sorted({1, 2, max(1, cap // 8), max(1, cap // 2), max(1, cap - 1), cap}):
            if L < 1 or L * IW > T or L > nc5.GMAX:
                continue
            grid.append((L, T))
    rows = []
    for (L, T) in grid:
        cell = {"genome_length": L, "tape_words": T,
                "genome_words": L * IW, "occupancy": L * IW / T, "operators": {}}
        for op in OPS:
            changed = grew = shrank = 0
            tape_up = tape_down = tape_noop = 0
            for _ in range(TRIALS):
                m = make(rng, L, T)
                mate = make(rng, L, T)
                c, rec = grammar.mutate(m, rng, mate, op)
                dl = rec["len_after"] - rec["len_before"]
                if dl > 0:
                    grew += 1
                elif dl < 0:
                    shrank += 1
                if c != m:
                    changed += 1
                if op == "config_perturbation" and rec["args"].get("field") == "tape_words":
                    if "noop" in rec["args"]:
                        tape_noop += 1
                    elif c["tape_words"] > T:
                        tape_up += 1
                    else:
                        tape_down += 1
            e = {"accepted": changed / TRIALS, "grew": grew / TRIALS, "shrank": shrank / TRIALS}
            if op == "config_perturbation":
                tot = max(1, tape_up + tape_down + tape_noop)
                e.update({"tape_proposals": tot, "tape_up": tape_up / tot,
                          "tape_down": tape_down / tot, "tape_noop": tape_noop / tot})
            cell["operators"][op] = e
        rows.append(cell)

    # the reversibility question, stated as a number per cell
    asym = []
    for c in rows:
        ins = c["operators"]["insertion"]["grew"]
        dele = c["operators"]["deletion"]["shrank"]
        up = c["operators"]["config_perturbation"].get("tape_up", 0.0)
        dn = c["operators"]["config_perturbation"].get("tape_down", 0.0)
        asym.append({"genome_length": c["genome_length"], "tape_words": c["tape_words"],
                     "occupancy": c["occupancy"],
                     "insertion_accept": ins, "deletion_accept": dele,
                     "insertion_minus_deletion": ins - dele,
                     "tape_up_rate": up, "tape_down_rate": dn, "tape_up_minus_down": up - dn})
    out = {"schema_version": "proteus.acceptance_maps.v0_4",
           "grammar_hash": grammar.GRAMMAR_HASH, "runtime_hash": RUNTIME_HASH,
           "trials_per_cell": TRIALS, "cells": rows, "reversibility_summary": asym}
    with open(os.path.join(HERE, "RESULT_ACCEPTANCE_MAPS.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"{'L':>5} {'T':>5} {'occ':>5} {'ins':>6} {'del':>6} {'i-d':>7} "
          f"{'t_up':>6} {'t_dn':>6} {'up-dn':>7}")
    for a in asym:
        print(f"{a['genome_length']:>5} {a['tape_words']:>5} {a['occupancy']:>5.2f} "
              f"{a['insertion_accept']:>6.3f} {a['deletion_accept']:>6.3f} "
              f"{a['insertion_minus_deletion']:>+7.3f} {a['tape_up_rate']:>6.3f} "
              f"{a['tape_down_rate']:>6.3f} {a['tape_up_minus_down']:>+7.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
