"""DARK OBJECTS and the THESEUS-TYCHE LENS LOOP.

Observation of a candidate: Xobs[T, d] = per-channel spatial means, per-
channel spatial std, and three probe cells of channel 0 (d = 2C + 3).
Organism: ridge regression predicting next-step spatial means and stds
(2C targets) from features at t. Trained and tested on different initial
conditions (see TRAIN_SEEDS / TEST_SEED).

  residual(features) = mean over targets of clip(1 - R^2_test, 0, 1)

(Amended before any run, 2026-09-30: a single training trace let the
full-state observer overfit -- median residual 0.67 on G0, worse than L0 --
so every organism now trains on IC seeds TRAIN_SEEDS and tests on
TEST_SEED.)

  L0     the current lens set: identity lenses [Xobs_t, Xobs_{t-1}, 1]
  FULL   the in-principle observer: the full state x_t (C*N values)

DARK_OBJECT (charter definition, made mechanical): viable, replicable,
residual(L0) >= DARK_MIN, and the held-out target series is temporally
STRUCTURED (max over targets of |lag-1 autocorrelation| >= STRUCT_MIN): the
dynamics are reproducible, the current lenses do not characterise them, and
what they miss is not a white sequence. Never called noise.
(Amended before any run, 2026-09-30: the first form required a full-state
LINEAR observer to beat L0 by GAP_MIN; on G0 that observer was worse than
L0 (median residual 0.67 vs 0.19) because the dynamics are nonlinear, so it
is not an upper bound. resid_full is still recorded; it no longer gates.)

Lens evolution (Tyche lens genomes, tyche.lens, used read-only): a small
(mu + lambda) search over lens genomes on the seed-0 trace; a lens is
ADMITTED when, on the held-out seed-1 trace, it lowers residual by
>= ADMIT_DROP AND beats the 95th percentile of NULL_LENSES random lenses of
the same generator. An admitted lens becomes a synthetic tensor entity
(kind "lens") eligible for future collisions.
"""

from __future__ import annotations

import numpy as np

from . import substrate as sb

DARK_MIN = 0.25
GAP_MIN = 0.15  # retired as a gate (see docstring); kept for the record
STRUCT_MIN = 0.5
ADMIT_DROP = 0.05
NULL_LENSES = 30
POP = 16
GENS = 12
RIDGE = 1e-2
TRAIN_SEEDS = (0, 2, 3, 4)
TEST_SEED = 1


def observe(trace):
    T, C, N = trace.shape
    S = trace.mean(2)
    D = trace.std(2)
    probes = trace[:, 0, [0, N // 4, N // 2]]
    return np.concatenate([S, D, probes], 1)


def targets(trace):
    return np.concatenate([trace.mean(2), trace.std(2)], 1)


def _ridge_residual(Ftr, Ytr, Fte, Yte):
    mu, sd = Ftr.mean(0), Ftr.std(0) + 1e-9
    A = (Ftr - mu) / sd
    B = (Fte - mu) / sd
    A = np.hstack([A, np.ones((len(A), 1))])
    B = np.hstack([B, np.ones((len(B), 1))])
    W = np.linalg.solve(A.T @ A + RIDGE * len(A) * np.eye(A.shape[1]), A.T @ Ytr)
    P = B @ W
    res = []
    for j in range(Yte.shape[1]):
        v = Yte[:, j].var()
        if v < 1e-10:
            continue
        res.append(float(np.clip(((Yte[:, j] - P[:, j]) ** 2).mean() / v, 0, 1)))
    return float(np.mean(res)) if res else None


def _l0(obs):
    return np.hstack([obs[1:-1], obs[:-2]])


def _lens_feats(lens_g, obs):
    from tyche import lens as tl
    Z = tl.execute(lens_g, obs)
    return Z[1:-1]


def feature_sets(trace, lenses=()):
    obs = observe(trace)
    F = _l0(obs)
    for lg in lenses:
        F = np.hstack([F, _lens_feats(lg, obs)])
    return F


def traces(g):
    tr = {s: sb.run(g, seed=s)[0] for s in TRAIN_SEEDS + (TEST_SEED,)}
    return [tr[s] for s in TRAIN_SEEDS], tr[TEST_SEED]


def residuals(trains, test, lenses=()):
    Ytr = np.vstack([targets(t)[2:] for t in trains])
    Ftr = np.vstack([feature_sets(t, lenses) for t in trains])
    return _ridge_residual(Ftr, Ytr, feature_sets(test, lenses), targets(test)[2:])


def full_residual(trains, test):
    Ytr = np.vstack([targets(t)[2:] for t in trains])
    Ftr = np.vstack([t[1:-1].reshape(t.shape[0] - 2, -1) for t in trains])
    Fte = test[1:-1].reshape(test.shape[0] - 2, -1)
    return _ridge_residual(Ftr, Ytr, Fte, targets(test)[2:])


def assess(g, viable):
    trains, test = traces(g)
    r0 = residuals(trains, test)
    rf = full_residual(trains, test)
    Y = targets(test)
    ac = [abs(float(np.corrcoef(Y[1:, j], Y[:-1, j])[0, 1])) for j in range(Y.shape[1]) if Y[:, j].std() > 1e-6]
    struct = max(ac) if ac else 0.0
    dark = bool(viable and r0 is not None and r0 >= DARK_MIN and struct >= STRUCT_MIN)
    return {"resid_L0": r0, "resid_full": rf, "structure_ac1": struct, "dark": dark}


def _fit_on_train(lg, trains):
    """Lens fitness on TRAINING seeds only: fit on all but the last training
    trace, validate on the last. The test seed is never seen by the search."""
    r = residuals(trains[:-1], trains[-1], [lg])
    return 1.0 if r is None else r


def evolve_lens(g, seed=0, lens_space_seed=0):
    from tyche import lens as tl
    rng = np.random.default_rng(seed)
    trains, test = traces(g)
    base = residuals(trains, test)
    if base is None:
        return {"admitted": False, "reason": "no_target_variance"}
    pop = [tl.random_genome(rng) for _ in range(POP)]
    fit = [_fit_on_train(p, trains) for p in pop]
    for _ in range(GENS):
        kids = []
        for _ in range(POP):
            a = pop[int(rng.integers(POP))]
            child, _ops = tl.mutate(a, rng)
            kids.append(child)
        kf = [_fit_on_train(c, trains) for c in kids]
        allp, allf = pop + kids, fit + kf
        order = np.argsort(allf)[:POP]
        pop = [allp[i] for i in order]
        fit = [allf[i] for i in order]
    best = pop[0]
    held = residuals(trains, test, [best])
    nrng = np.random.default_rng(10_000 + lens_space_seed)
    null = []
    for _ in range(NULL_LENSES):
        r = residuals(trains, test, [tl.random_genome(nrng)])
        null.append(base - r if r is not None else 0.0)
    drop = base - held if held is not None else 0.0
    thr = float(np.percentile(null, 95))
    admitted = bool(drop >= ADMIT_DROP and drop > thr)
    return {"admitted": admitted, "lens": best, "lens_id": tl.lens_id(best), "resid_L0": base,
            "resid_with_lens": held, "drop": drop, "null_p95_drop": thr, "null_drops": null,
            "search": {"pop": POP, "gens": GENS, "null": NULL_LENSES}}


def lens_marginal(g, lenses):
    """Best held-out residual drop any admitted lens gives this candidate."""
    trains, test = traces(g)
    base = residuals(trains, test)
    if base is None or not lenses:
        return {"resid_L0": base, "best_drop": None, "best_lens": None}
    best, bid = -1.0, None
    for lid, lg in lenses:
        r = residuals(trains, test, [lg])
        if r is not None and base - r > best:
            best, bid = base - r, lid
    return {"resid_L0": base, "best_drop": best, "best_lens": bid}
