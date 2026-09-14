"""M1 / D-open (round 3, builder G): trivial-policy floors for the held64 metric.

A held64 number (per-seed mean of summed clipped final charge on E6's 64 held-out seeds) means little
unless it is read against what a policy with no brain gets. Floors per world x pressure:

  abstain        every slot abstains every tick (action 0)
  best_fixed     the constant action (same W-vector on every slot, every tick) with the best TRAIN
                 score, found exhaustively over the 8^W distinct actions (the world reads action % 8);
                 ties -> the smallest action index. Scored on HELD64. Pressure = which TRAIN seeds.
  random_action  every slot draws a uniform action in [0, 8)^W every tick from a seeded PCG64;
                 one score per policy seed.

Also reported, NOT a floor (selected on the test seeds): const_ceiling_held64, the best constant
action's HELD64 score when chosen on HELD64 itself -- the easy-metric discriminator of anomaly
1789419655457-0.

Everything runs on NpEncounter (the numpy reference world); tests check it against wforge.
"""
from __future__ import annotations

import numpy as np

from primordial.qd import e4_run as E4
from primordial.soup.b1.np_world import NpEncounter

TRAIN8 = np.arange(9100, 9108, dtype=np.int64)
TRAIN128 = np.arange(9100, 9228, dtype=np.int64)
HELD64 = np.arange(30000, 30064, dtype=np.int64)
PRESSURES = {"train8_held64": TRAIN8, "train128_held64": TRAIN128}
MAX_ENVS = 1 << 16


def all_actions(W: int) -> np.ndarray:
    """[8^W, W] every distinct action vector, index order = base-8 digits, most significant first."""
    idx = np.arange(8 ** W)
    return np.stack([(idx // 8 ** (W - 1 - j)) % 8 for j in range(W)], axis=1).astype(np.int32)


def _run(spec: E4.Spec, seeds: np.ndarray, K: int, act_fn) -> np.ndarray:
    """K policies x seeds on one batched world; act_fn(t, n) -> [n, S, W] actions (env e = policy e // k).
    Returns the per-seed score of each policy [K] (float64)."""
    k = len(seeds)
    n = K * k
    w = NpEncounter(spec.mech, spec.wid, with_obs=False)
    w.reset(np.tile(seeds, K))
    for t in range(spec.T):
        _, _, done = w.step(act_fn(t, n))
        if done.all():
            break
    return np.clip(w.charge, 0, None).sum(1).reshape(K, k).sum(1) / k


def const_scores(spec: E4.Spec, actions: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    """Per-seed score of each constant action policy; actions [K, W]."""
    actions = np.asarray(actions, np.int32)
    k, out = len(seeds), []
    step = max(1, MAX_ENVS // k)
    for i in range(0, len(actions), step):
        a = actions[i:i + step]
        full = np.repeat(np.broadcast_to(a[:, None, :], (len(a), spec.S, spec.W)), k, axis=0)
        out.append(_run(spec, seeds, len(a), lambda t, n, full=full: full))
    return np.concatenate(out)


def random_scores(spec: E4.Spec, seeds: np.ndarray, policy_seeds) -> np.ndarray:
    """Per-seed score of the uniform random-action policy, one value per policy seed."""
    out = []
    for ps in policy_seeds:
        rng = np.random.Generator(np.random.PCG64([7001, int(ps), spec.gen_seed]))
        out.append(_run(spec, seeds, 1, lambda t, n: rng.integers(0, 8, (n, spec.S, spec.W), dtype=np.int32))[0])
    return np.array(out)


def floors(gen_seed: int, pressure: str, policy_seeds=range(8)) -> dict:
    """All floors of one world x pressure, plus the (not-a-floor) constant ceiling on HELD64."""
    spec = E4.Spec(gen_seed)
    acts = all_actions(spec.W)
    train = const_scores(spec, acts, PRESSURES[pressure])
    held = const_scores(spec, acts, HELD64)
    b = int(np.argmax(train))                  # argmax returns the first (smallest) index on ties
    c = int(np.argmax(held))
    rnd = random_scores(spec, HELD64, policy_seeds)
    return {
        "world": f"w{gen_seed}", "pressure": pressure, "W": spec.W, "S": spec.S, "T": spec.T,
        "n_actions": len(acts),
        "abstain_held64": float(held[0]),
        "best_fixed_action": acts[b].tolist(), "best_fixed_train": float(train[b]),
        "best_fixed_held64": float(held[b]),
        "random_action_held64_median": float(np.median(rnd)),
        "random_action_held64_iqr": float(np.percentile(rnd, 75) - np.percentile(rnd, 25)),
        "random_action_held64_by_policy_seed": rnd.tolist(),
        "const_ceiling_action": acts[c].tolist(), "const_ceiling_held64": float(held[c]),
        "const_held64_quantiles": {q: float(np.percentile(held, q)) for q in (0, 50, 90, 100)},
        "floor_held64": float(max(held[0], held[b], np.median(rnd))),
    }
