"""D15 demonstration: run_xtg's "competent" = held >= 0.5 AND probe >= cue_index + 1 admits a program that reads all
three inputs and then ignores the regime (echoes base = v XOR key). Under the ffa6 cell's NEUTRAL_BRIDGE it scores 0.75
in expectation without implementing the conditional transform. Pure scoring calls (tasks.competence), no Runner."""
from __future__ import annotations

import _paths
import run_dd
import run_ds
import tasks
import z8

a = run_ds.cells()[run_dd.CELLS["ffa6"]]
spec = tasks.spec_from_cell(a["cell"], n_episodes=8)
echo_base, _ = z8.asm("IN\nLD B,A\nIN\nXOR B\nLD B,A\nIN\nLD A,B\nOUT\nHALT")
wit = tasks.witness(spec)
out = {}
for name, g in (("reads_all_three_then_echoes_base", echo_base), ("witness", wit)):
    hs = [tasks.competence(g, spec, seed=s, held_seed=s + 500000) for s in range(200)]
    held = sum(h["held"] for h in hs) / len(hs)
    probe = sum(h["reads_at_answer"] for h in hs) / len(hs)
    passes = sum(h["held"] >= 0.5 and h["reads_at_answer"] >= spec.cue_index() + 1 for h in hs) / len(hs)
    out[name] = {"mean_held": round(held, 3), "mean_probe": round(probe, 3), "share_of_draws_counted_competent": passes}
_paths.dump("d7_xtg_competent_ruler.json", {"spec": spec.as_dict(), "programs": out})
