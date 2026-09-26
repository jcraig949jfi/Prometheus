"""WTP-LM01 world families (directive s4 items 1-5) on WTP's own field generators (ensorain.wtp.world.base_field).

Not a new engine: the fields come from WTP's generator families. Exposure is a walk on WTP's tensor-index geometry
(one coordinate changes per step). There is no economy and no carrier learner, so no arm's inductive bias chooses which
cells are seen. That choice is a design declaration for the prereg: it removes the WTP-03 admission path that
manufactured completion.

Class-agnostic: F2/F3/F4 draw the generator uniformly from LATENT_GENS (all WTP generators with low-dimensional
structure, not only completion-friendly ones). F1 uses WTP's "random" generator (no structure). The family
mixture is fixed here, before any dev row.

  F1 EPISODIC  iid field ("random"), walk with a revisit probability. Exact detail is the only thing that helps.
               Declared in advance: F1 cannot feed the R2 headline (no never-seen cell is predictable). It is where
               LOSSLESS must win on exact-hit / revisit prediction (a branch-trigger family).
  F2 LATENT    one field per life from a LATENT_GENS generator.
  F3 SWITCH    K episodes per life, each a fresh field from the same generator. The relevant structure changes
               between episodes. Scored on the final episode.
  F4 TRANSFER  family field = w*C + (1-w)*I_f, with the common component C shared across the family and I_f
               field-specific (same generator). The life is on field A, then a short exposure to a FRESH field B,
               scored on B's never-seen cells (the fresh-field transfer that repairs WTP-03's W1).
  F5 NUISANCE  one extra mode of size K_NUIS appended. In training the nuisance coordinate is the quantile bin of the
               noisy observed value (predictive). OOD tests draw it uniformly (irrelevant: the generator ignores the
               mode). Relevance oracle = the generator.

Every world returns exact noise-free truth (signal) for HR2_signal and for relevance (memo G2)."""
import hashlib

import numpy as np

from ensorain.wtp.world import base_field, _std

LATENT_GENS = ("lowrank", "cp", "tt", "pairwise", "spectral", "sum")   # FROZEN (#655/#656 JOINT, 2026-09-26)
FAMILIES = ("F1_episodic", "F2_latent", "F3_switch", "F4_transfer", "F5_nuisance")
LEVELS = {                      # complexity/horizon levels (directive s6); coverage < 1 is checked by coverage_table()
    "L1": dict(dims=(8, 8, 8), n_obs=700),
    "L2": dict(dims=(12, 12, 12), n_obs=1600),
    "L3": dict(dims=(16, 16, 16), n_obs=2800),
}
NOISE = 0.1                    # observation noise SD on standardised fields
K_EPIS, W_COMMON, B_FRAC, K_NUIS, P_REV, P_JUMP = 3, 0.6, 0.15, 4, 0.5, 0.02
DEV_SEEDS = range(9_100_000, 9_900_000)
LIFE_MULT = 4.0                # P1 (#644 JOINT): one value for all families and levels; LOSSLESS's 4x store/reads charged
NUIS_P = 0.5                   # P2 (#644 JOINT): F5 headline reliability; nuis_p=1.0 is the declared "everyone falls" control


def _rng(seed, tag):
    return np.random.default_rng(int(hashlib.sha256(f"lm01:{tag}:{seed}".encode()).hexdigest()[:15], 16))


def walk(dims, n, rng, p_rev=0.0, p_jump=P_JUMP):
    """Exposure on the tensor-index geometry: each step changes one coordinate to a random value. With p_rev it
    returns to a uniformly chosen previously visited cell; with p_jump it teleports (restart)."""
    D = len(dims)
    A = np.empty((n, D), int)
    cur = np.array([rng.integers(d) for d in dims])
    for t in range(n):
        u = rng.random()
        if t > 0 and u < p_rev:
            cur = A[rng.integers(t)].copy()
        elif u < p_rev + p_jump:
            cur = np.array([rng.integers(d) for d in dims])
        else:
            m = rng.integers(D)
            cur[m] = rng.integers(dims[m])
        A[t] = cur
    return A


def _field(gen, dims, rank, rng):
    return _std(np.real(base_field(gen, list(dims), rank, rng)))


def _obs(x, A, rng, noise=NOISE):
    s = x[tuple(A.T)]
    return s + noise * rng.normal(size=len(A)), s


def _unseen(dims, A, rng, n=512):
    seen = np.zeros(dims, bool)
    seen[tuple(A.T)] = True
    idx = np.flatnonzero(~seen.reshape(-1))
    pick = np.sort(rng.choice(idx, size=min(n, len(idx)), replace=False)) if len(idx) else idx
    return np.array(np.unravel_index(pick, dims)).T.reshape(-1, len(dims)), int(len(idx)), float(seen.mean())


def _seen_cells(A, rng, n=512):
    u = np.unique(A, axis=0)
    return u[np.sort(rng.choice(len(u), size=min(n, len(u)), replace=False))]


def make_world(family, level, seed, life_mult=LIFE_MULT, noise=NOISE, nuis_p=NUIS_P, gen=None):
    """One world. Returns dict: family, level, gen, dims, train=[(A, y, signal) segments in order],
    tests={name: (A, truth)}, coverage, n_unseen (the eligible count for the R2 headline)."""
    assert seed in DEV_SEEDS or seed >= 10 ** 9, "LM01: dev seeds 9.1M-9.9M; campaign seeds come only from the sealed procedure"
    L = LEVELS[level]
    dims, n = tuple(L["dims"]), int(round(L["n_obs"] * life_mult))
    rw, rx, rt = _rng(seed, f"{family}:world"), _rng(seed, f"{family}:walk"), _rng(seed, f"{family}:test")
    g_draw = "random" if family == "F1_episodic" else LATENT_GENS[int(rw.integers(len(LATENT_GENS)))]
    gen = g_draw if gen is None else gen          # stratum override (#655): the stream draw is consumed either way
    rank = int(rw.integers(1, 4))
    out = dict(family=family, level=level, seed=int(seed), life_mult=life_mult, noise=noise, gen=gen, rank=rank, dims=list(dims), tests={})
    if family in ("F1_episodic", "F2_latent"):
        x = _field(gen, dims, rank, rw)
        A = walk(dims, n, rx, p_rev=P_REV if family == "F1_episodic" else 0.0)
        y, s = _obs(x, A, rx, noise)
        out["train"] = [(A, y, s)]
        U, nu, cov = _unseen(dims, A, rt)
        H = _seen_cells(A, rt)
        out["tests"] = dict(never_seen=(U, x[tuple(U.T)]), exact_hit=(H, x[tuple(H.T)]))
    elif family == "F3_switch":
        segs, m = [], n // K_EPIS
        for k in range(K_EPIS):
            x = _field(gen, dims, rank, rw)
            A = walk(dims, m, rx)
            y, s = _obs(x, A, rx, noise)
            segs.append((A, y, s))
        out["train"] = segs
        U, nu, cov = _unseen(dims, segs[-1][0], rt)
        H = _seen_cells(segs[-1][0], rt)
        out["tests"] = dict(never_seen=(U, x[tuple(U.T)]), exact_hit=(H, x[tuple(H.T)]))
    elif family == "F4_transfer":
        C = _field(gen, dims, rank, rw)
        xa = _std(W_COMMON * C + (1 - W_COMMON) * _field(gen, dims, rank, rw))
        xb = _std(W_COMMON * C + (1 - W_COMMON) * _field(gen, dims, rank, rw))
        nb = max(20, int(B_FRAC * n))
        Aa = walk(dims, n - nb, rx)
        Ab = walk(dims, nb, rx)
        ya, sa = _obs(xa, Aa, rx, noise)
        yb, sb = _obs(xb, Ab, rx, noise)
        out["train"] = [(Aa, ya, sa), (Ab, yb, sb)]
        U, nu, cov = _unseen(dims, Ab, rt)
        out["tests"] = dict(fresh_field=(U, xb[tuple(U.T)]))
        UA, _, _ = _unseen(dims, Aa, rt)
        out["tests"]["never_seen_A"] = (UA, xa[tuple(UA.T)])
    elif family == "F5_nuisance":
        x = _field(gen, dims, rank, rw)
        A = walk(dims, n, rx)
        y, s = _obs(x, A, rx, noise)
        q = np.quantile(y, np.linspace(0, 1, K_NUIS + 1)[1:-1])
        nz = np.searchsorted(q, y)
        flip = rx.random(len(y)) >= nuis_p                         # nuis_p < 1: the nuisance is only partly reliable
        nz[flip] = rx.integers(0, K_NUIS, int(flip.sum()))
        An = np.hstack([A, nz[:, None]])     # predictive in training only
        out["train"] = [(An, y, s)]
        out["dims"] = list(dims) + [K_NUIS]
        U, nu, cov = _unseen(dims, A, rt)
        Uo = np.hstack([U, rt.integers(0, K_NUIS, (len(U), 1))])   # OOD: nuisance coordinate uniform
        out["tests"] = dict(ood_never_seen=(Uo, x[tuple(U.T)]))
    else:
        raise KeyError(family)
    out["coverage"], out["n_unseen"] = cov, nu
    return out


def coverage_table(seeds, families=FAMILIES, levels=LEVELS):
    """#591 R2b / #594: coverage per level and the eligible never-seen count, before freezing."""
    rows = []
    for lv in levels:
        for fam in families:
            cs, ns = [], []
            for sd in seeds:
                w = make_world(fam, lv, sd)
                cs.append(w["coverage"])
                ns.append(w["n_unseen"])
            rows.append(dict(level=lv, family=fam, coverage_mean=float(np.mean(cs)), coverage_max=float(np.max(cs)),
                             unseen_min=int(np.min(ns)), unseen_total=int(np.sum(ns))))
    return rows
