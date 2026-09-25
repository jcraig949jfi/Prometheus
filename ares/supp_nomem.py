"""Supplementary combined-memory ablation, added 2026-09-19 after the
sweep exposed that the `no_state` substrate ablation leaves plasticity
intact (LEDGER 2026-09-19). For each present-mode champion of the
memory-relevant worlds, evaluate the intact organism and three
ablations: no activation memory (keep off + reset each step), no
plasticity, and BOTH. Writes runs/sweep_c0/nomem.json. EXPLORATORY:
this is a post-hoc control, not part of the preregistered rule.

    python -m ares.supp_nomem
"""
import json
import os

from . import search as R
from . import substrate as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "sweep_c0")
WORLDS = ["W4", "W3", "W12", "W2", "W5"]
SEEDS = [1, 2, 3]


def main():
    rows = []
    for w in WORLDS:
        for sd in SEEDS:
            path = os.path.join(OUT, f"main_{w}_present_s{sd}.json")
            if not os.path.exists(path):
                continue
            g = json.load(open(path))["final"]["genome"]
            base_cfg = g["cfg"]
            variants = dict(
                intact=base_cfg,
                no_activation_mem={**base_cfg, "allow_keep": False, "reset_each_step": True},
                no_plasticity={**base_cfg, "allow_plasticity": False},
                no_memory_at_all={**base_cfg, "allow_keep": False, "reset_each_step": True, "allow_plasticity": False},
            )
            scores = {}
            for label, cfgd in variants.items():
                pop = S.Population.from_genomes([g], S.Config(**cfgd))
                scores[label] = float(R.rollout(pop, R.make_world(w, "present"), R.EVAL_SEEDS)[0])
            rows.append(dict(world=w, seed=sd, **scores))
            print(f"{w} s{sd}: intact {scores['intact']:8.2f} noact {scores['no_activation_mem']:8.2f} "
                  f"noplast {scores['no_plasticity']:8.2f} nomem {scores['no_memory_at_all']:8.2f}")
    json.dump(dict(note="EXPLORATORY post-hoc combined-memory ablation; see LEDGER 2026-09-19",
                   receipt=R.receipt(S.Config(), "nomem", "present", 1, 0, len(R.EVAL_SEEDS), 0), rows=rows),
              open(os.path.join(OUT, "nomem.json"), "w"), indent=1)
    print("wrote", os.path.join(OUT, "nomem.json"))


if __name__ == "__main__":
    main()
