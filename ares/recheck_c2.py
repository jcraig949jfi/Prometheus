"""Cycle-2 post-hoc repair and re-derivation (2026-09-23, EXPLORATORY
where marked). Two defects were found in the cycle-2 apparatus by the
audit of its own output, AFTER the gates first ran:

 D1 SELECTION ON THE HELD-OUT SET. search.run picks the final champion
    with argmax over the whole final population evaluated on the
    held-out episodes, so `final.heldout` is a max-of-128 statistic and
    is inflated wherever the score is noisy (the shuffled controls).
    The per-generation log's `champ_heldout` is the clean number: that
    champion is selected on TRAINING episodes and then evaluated on
    held-out. Everything here re-derives from the clean number.
    Arms sitting at the structural cap are unaffected (40.0 of 40.0
    cannot be inflated), which is where every headline result sits.
 D2 BIASED SWAP STATISTIC. cycle2.phase_gates scored gate C with the
    BEST donor per host (max over 9). The operator's criterion is that
    a carrier's function survives substantial genomic-context change,
    so the per-PAIR statistic is the right one, restricted to pairs
    where cutting the host's carrier actually broke the host.

Also measures the USEFUL-carrier opportunity: a keep of 0.06 is
"created" but useless, whereas one self-loop edge of weight 1 is
immediately usable. This is the sharper denominator the time-to-
threshold gap asks for.

    python -m ares.recheck_c2
"""
import json
import os

import numpy as np

from . import carriers as C
from . import cycle2 as V
from . import substrate as S

OUT = V.OUT


def clean_heldout(name):
    """The training-selected champion's held-out score (defect D1)."""
    r = V._load(name)
    return float(r["log"][-1]["champ_heldout"])


def main():
    out = {}
    arms = list(V.Q1_ARMS) + list(V.Q2_ARMS) + [f"{w}_{m}" for w in V.HOSTILE for m in ("present", "shuffled")] + ["c1_shuffled_ref"]
    rows = {}
    print(f"{'arm':20s} {'world':10s} {'clean median':>12s} {'reported':>9s} {'above(clean)':>13s} {'thr':>6s}")
    for arm in arms:
        w, mode = V.arm_world(arm)
        thr = V.THRESH[w]
        cl, rep = [], []
        for sd in V.SEEDS:
            if os.path.exists(V._path(f"{arm}_s{sd}")):
                cl.append(clean_heldout(f"{arm}_s{sd}"))
                rep.append(V._load(f"{arm}_s{sd}")["final"]["heldout"])
        if not cl:
            continue
        rows[arm] = dict(world=w, mode=mode, threshold=thr, clean=cl, reported=rep,
                         clean_median=float(np.median(cl)), reported_median=float(np.median(rep)),
                         above_clean=int(sum(1 for x in cl if x >= thr)))
        print(f"{arm:20s} {w + '/' + mode:10s} {np.median(cl):12.2f} {np.median(rep):9.2f} "
              f"{rows[arm]['above_clean']:10d}/10 {thr:6.2f}")
    out["clean_heldout"] = rows

    # shuffled controls give the empirical selection floor per world
    floors = {}
    for arm in ("c1_shuffled_ref", "W14_shuffled", "W15_shuffled", "W16_shuffled"):
        if arm in rows:
            w = rows[arm]["world"]
            floors[w] = dict(clean_median=rows[arm]["clean_median"], reported_median=rows[arm]["reported_median"],
                             clean_max=float(max(rows[arm]["clean"])), reported_max=float(max(rows[arm]["reported"])))
    out["empirical_floor_from_shuffled"] = floors
    print("\nempirical floors (shuffled controls):")
    for w, f in floors.items():
        print(f"  {w}: clean median {f['clean_median']:.2f} max {f['clean_max']:.2f} | "
              f"reported(inflated) median {f['reported_median']:.2f} max {f['reported_max']:.2f}")

    # ---- D2: per-pair swap statistic
    sw = V._load("swaps")
    deep = [r for r in sw if (r["host_intact"] - r["host_carrier_cut"]) >= 0.25 * r["host_intact"]
            and r["recovery_fraction"] is not None]
    rec = [r["recovery_fraction"] for r in deep]
    per_host_best = {}
    for r in deep:
        per_host_best[r["host"]] = max(per_host_best.get(r["host"], -9), r["recovery_fraction"])
    out["swap_recheck"] = dict(
        n_pairs=len(sw), n_pairs_with_real_cut=len(deep),
        per_pair_median=float(np.median(rec)), per_pair_mean=float(np.mean(rec)),
        per_pair_ge_half=int(sum(1 for x in rec if x >= 0.5)),
        per_host_best_ge_half=int(sum(1 for v in per_host_best.values() if v >= 0.5)),
        per_host_best_median=float(np.median(list(per_host_best.values()))))
    print(f"\nswap (per PAIR, real cuts only): n={len(deep)} median {np.median(rec):.2f} "
          f">=0.5 in {out['swap_recheck']['per_pair_ge_half']}/{len(deep)}")
    print(f"swap (per HOST best-of-9, the biased statistic gate C first used): "
          f">=0.5 in {out['swap_recheck']['per_host_best_ge_half']}/{len(per_host_best)}")

    # ---- EXPLORATORY: useful-carrier opportunity
    print("\nEXPLORATORY useful-carrier opportunity (create a USABLE carrier in one mutation):")
    useful = {}
    for label, cfg in (("default", S.Config()), ("keep_subsidy", S.Config(keep_mut_weight=8.0))):
        rng = np.random.default_rng(77)
        n = 8000
        made = dict(any_keep=0, useful_keep=0, any_self=0, useful_self=0)
        for _ in range(n):
            pop = S.random_population(cfg, 1, rng)
            d = np.arange(cfg.n)
            pop.W1[0, d, d] = 0; pop.W2[0, d, d] = 0; pop.R[0, d, d] = 0
            S.strip_cycles(pop, 0, rng)
            pop.keep[:] = 0
            S.mutate_one(pop, 0, rng, n_mut=1)
            k = pop.keep[0][pop.alive[0]]
            if (k > 0.05).any():
                made["any_keep"] += 1
            if (k >= 0.90).any():
                made["useful_keep"] += 1
            rec_m = S.recurrent_edge_mask(pop)[0]
            if rec_m.any():
                made["any_self"] += 1
                w = np.maximum(np.abs(pop.W1[0][rec_m]), np.abs(pop.W2[0][rec_m]))
                if (w >= 1.0).any():
                    made["useful_self"] += 1
        useful[label] = {k: v / n for k, v in made.items()}
        print(f"  {label:12s} any_keep {useful[label]['any_keep']:.4f} useful_keep(>=0.90) {useful[label]['useful_keep']:.4f} "
              f"| any_recur {useful[label]['any_self']:.4f} useful_recur(|w|>=1) {useful[label]['useful_self']:.4f}")
    out["useful_opportunity"] = useful

    json.dump(out, open(os.path.join(OUT, "recheck.json"), "w"), indent=1)
    print("\nwrote", os.path.join(OUT, "recheck.json"))


if __name__ == "__main__":
    main()
