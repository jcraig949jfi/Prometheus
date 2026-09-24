"""P1 / P2 certificate (roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md s2).

P1: D_bits = CE(c | O_t) - CE(c | S_t, O_t) at the query time, held-out; tau from permutations of the
    cue WITHIN strata of O_t (O_t's own information preserved). P1 iff D_bits > tau and > FLOOR_BITS.
P2: paired episodes sharing distractors and noise; at t = k the full states of the two rows are
    exchanged; effect = J_intact - J_ablated (paired, scored against each row's own cue);
    eps = 3 x bootstrap SE. P2 iff effect > eps and > FLOOR_J.
"""
from __future__ import annotations

from typing import Any, Dict

import numpy as np

from prometheus.cosmos.c3.probe import cv_ce_bits
from prometheus.cosmos.c3.system import System, rollout, train_readout
from prometheus.cosmos.c3.task import Task, batch, onehot, paired_batch

FLOOR_BITS = 0.0      # v2 (A1): removed; P1 is a pure permutation test
FLOOR_J = 0.0         # v2 (A1): removed; P2 is a pure 3-SE test
N_PERM = 49


def p1(sys: System, task: Task, pol, E: int, rng, t_probe: int = None, n_perm: int = N_PERM) -> Dict[str, Any]:
    """v3 (A2): statistic = max(D_generic, D_readout); max-statistic permutation null within O strata;
    p-value with ties counted against the claim."""
    t_probe = task.k + 1 if t_probe is None else t_probe
    cues, obs = batch(task, E, rng)
    r = rollout(sys, obs, rng, record=(t_probe,))
    S = r["states"][t_probe]
    O = onehot(obs[:, t_probe], task.n_symbols)
    R = np.log(np.clip(pol.proba(r["features"]), 1e-9, None))       # the system's own readout, trained elsewhere
    SO, RO = np.hstack([S, O]), np.hstack([R, O])

    def stat(c):
        ce_o = cv_ce_bits(O, c, task.V)
        return ce_o - cv_ce_bits(SO, c, task.V), ce_o - cv_ce_bits(RO, c, task.V)

    dg, dr = stat(cues)
    d = max(dg, dr)
    keys = obs[:, t_probe]
    null = []
    prng = np.random.default_rng(12345)
    for _ in range(n_perm):
        cp = cues.copy()
        for kv in np.unique(keys):
            m = np.nonzero(keys == kv)[0]
            cp[m] = cp[m][prng.permutation(len(m))]
        null.append(max(stat(cp)))
    null = np.array(null)
    pval = float((1 + np.sum(null >= d - 1e-12)) / (1 + n_perm))       # ties (to 1e-12) count against
    return {"t": t_probe, "D_bits": float(d), "D_generic": float(dg), "D_readout": float(dr),
            "null_max": float(null.max()), "null_median": float(np.median(null)), "p": pval,
            "held": bool(pval <= 0.02), "indeterminate": bool(0.02 < pval <= 0.10)}


def p2(sys: System, task: Task, pol, n_pairs: int, rng, n_boot: int = 400) -> Dict[str, Any]:
    cues, obs = paired_batch(task, n_pairs, rng)
    seed = int(rng.integers(0, 2 ** 31))
    ri = rollout(sys, obs, np.random.default_rng(seed), paired=True)
    ra = rollout(sys, obs, np.random.default_rng(seed), paired=True, swap_at=task.k)
    ji = (pol.predict(ri["features"]) == cues).astype(float)
    ja = (pol.predict(ra["features"]) == cues).astype(float)
    diff = ji - ja
    brng = np.random.default_rng(7)
    boots = [diff[brng.integers(0, len(diff), len(diff))].mean() for _ in range(n_boot)]
    se = float(np.std(boots, ddof=1))
    eff = float(diff.mean())
    z = eff / se if se > 0 else (float("inf") if eff > 0 else 0.0)
    return {"J_intact": float(ji.mean()), "J_ablated": float(ja.mean()), "effect": eff, "se": se,
            "eps": 3 * se, "z": z, "held": bool(eff > 3 * se and eff > FLOOR_J), "indeterminate": bool(2 <= z < 3)}


def certify(sys: System, task: Task, seed: int, E_train: int = 2000, E_test: int = 3000,
            n_perm: int = N_PERM) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    pol = train_readout(sys, task, E_train, rng, batch)
    a = p1(sys, task, pol, E_test, rng, n_perm=n_perm)
    b = p2(sys, task, pol, E_test // 2, rng)
    if a["indeterminate"] or b["indeterminate"]:
        cls = "INDETERMINATE"
    elif a["held"] and b["held"]:
        cls = "FUNCTIONAL"
    elif a["held"]:
        cls = "PASSIVE"
    elif b["held"]:
        cls = "INCOHERENT"
    else:
        cls = "NONE"
    return {"system": sys.name, "seed": seed, "class": cls, "P1": a, "P2": b}
