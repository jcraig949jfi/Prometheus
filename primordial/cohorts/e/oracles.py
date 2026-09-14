"""E-T3 (lane B ask 2026-09-14): brain-oracle cheats with measured power, for any brain family.

B's finding: E7.brain_oracle(cheat=True) (skip-odd features) caught only 13/16 int2 linear
elites. A fixed-structure cheat is only a cheat for a brain whose actions depend on that
structure; for some brains it is (near) invariant, so the oracle looks blind. The MECHANISM on
B's int2 elites is open: B's anomaly 1789418707943-0 shows it is NOT zero odd weights (blind
elites' odd zero-weight fraction .31-.34, inside the run's .19-.44). This tool does not explain
the blindness; it measures a cheat's power per elite instead of assuming it.

brain_oracle_cheats(g7, g, seeds) runs one honest logged rollout (E7.rollout) and replays the
logged live rows through three named cheat forwards. For each cheat, the oracle's detection is
"emitted action != float64 ref_logits argmax on the HONEST obs, on clear-margin rows":

  skip_odd       E7's cheat: fam.forward(..., cheat=True)
  ablate_top     per elite, the ONE obs feature whose reflection (x -> 65535 - x, the largest
                 single-feature move in value range) changes the fast forward's action on the most rows. The feature is
                 picked on even-indexed sampled rows and power is measured on odd-indexed rows only
                 (no selection on the rows that score). An elite whose actions never change under any
                 single-feature ablation on the selection rows is reported input_invariant: the oracle
                 is vacuous for it (it is open loop in effect), which is a finding, not a pass.
  shift_action   action index + 1 mod A (a wrong forward that cannot be invariant): the oracle's
                 floor power; if this is not caught on every elite, the oracle itself is broken.

Honest: 0 mismatched clear rows expected. Returned per cheat: elites caught (>=1 mismatched clear
row), mismatched rows, clear rows; plus input_invariant elites.
"""
from __future__ import annotations

import numpy as np

from primordial.brain import genomes as gm
from primordial.qd import e7_run as E7

ROWS_PER_ELITE = 256


def _sample_rows(L, q, k, rng, n):
    t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
    if len(t_i) == 0:
        return None
    pick = np.sort(rng.choice(len(t_i), size=min(n, len(t_i)), replace=False))
    return t_i[pick], e_i[pick] + q * k, s_i[pick]


def brain_oracle_cheats(g7, g, seeds, seed: int = 0, rows_per_elite: int = ROWS_PER_ELITE) -> dict:
    _, _, _, L = E7.rollout(g7, g, seeds, log=True)
    fam = g7.fam
    rng = np.random.Generator(np.random.PCG64(seed))
    k, P, D = len(seeds), len(g[1]), g7.D
    names = ("honest", "skip_odd", "ablate_top", "shift_action")
    out = {n: {"elites_caught": 0, "mismatched_rows": 0, "clear_rows": 0} for n in names}
    out["input_invariant_elites"] = 0
    out["elites"] = P
    out["ablate_top_features"] = []
    for q in range(P):
        s = _sample_rows(L, q, k, rng, rows_per_elite)
        if s is None:
            continue
        t_i, e_i, s_i = s
        obs = L["obs"][t_i, e_i, s_i]
        emitted = L["idx"][t_i, e_i, s_i]
        gidx = np.full(len(obs), q, np.int64)
        ref = fam.ref_logits(fam.one(g[0], q), obs)
        clear = gm.clear_rows(ref)
        want = ref.argmax(1)
        sel = np.arange(len(obs)) % 2 == 0
        ev = ~sel
        # pick the most consequential single feature on the selection rows (fast forward, no ref)
        best_f, best_n = -1, 0
        for f in range(D):
            ob = obs.copy()
            ob[:, f] = 65535 - ob[:, f]
            n = int((fam.forward(g[0], ob[sel], gidx[sel]) != emitted[sel]).sum())
            if n > best_n:
                best_f, best_n = f, n
        cheats = {"honest": (emitted, np.ones(len(obs), bool)),
                  "skip_odd": (fam.forward(g[0], obs, gidx, cheat=True), np.ones(len(obs), bool)),
                  "shift_action": ((emitted + 1) % E7.A, np.ones(len(obs), bool))}
        if best_f >= 0:
            ob = obs.copy()
            ob[:, best_f] = 65535 - ob[:, best_f]
            cheats["ablate_top"] = (fam.forward(g[0], ob, gidx), ev)
        else:
            out["input_invariant_elites"] += 1
        out["ablate_top_features"].append(int(best_f))
        for name, (act, rows) in cheats.items():
            c = clear & rows
            mm = int(((act != want) & c).sum())
            out[name]["clear_rows"] += int(c.sum())
            out[name]["mismatched_rows"] += mm
            out[name]["elites_caught"] += bool(mm)
    return out
