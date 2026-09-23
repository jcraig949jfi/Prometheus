"""E-R6-2: graphworld_b2 adapter as a compiled, batched rollout (numba, prange over episodes).

The authority is adapter.RefB2 (plain Python). This form reimplements the SAME tick for a batch of E episodes that
share one spec shape (L, n_pred, n_prey, n_food, ticks) and differ in their initial cells (seed):

  1 EAT    a live food dies if a live prey is co-located; +FOOD_CREDIT to the LOWEST-id co-located prey (a per-cell
           min-prey scratch filled in ascending prey id)
  2 PREY   a live prey dies if a live predator is co-located (state after 1)
  obs      [S, 8] uint16 exactly as adapter._obs: per-cell kind counts; SAME bit 4 excludes the slot itself,
           neighbour bit d reads step_cell(c, d) (never the own cell for L >= 2)
  3 MOVE   predators (id*7 + t*3) % 4; a live slot's action a % 8 (0 = stay, else dir (a-1) % 4); a nonzero action
           of a live slot counts as a moving action; cheat skip_mutation reads the action and does not move the prey
  4        +1 charge to each live slot, clipped to CHARGE_MAX

Policies: `run_table` (open-loop action tensor [E, ticks, S]), `run_linear` (float32 linear genome on the raw obs:
logit_k = b[k] + sum_f W[k, f] * float32(obs_f), accumulated in f order; action = first argmax), and `Batch`
(observe/step from Python, for any batched policy). record=True keeps per-tick cells / live actions / charges so
`digest` rebuilds adapter's sha256 trajectory hash for the oracle; the throughput path does not hash.
"""
from __future__ import annotations

import hashlib

import numpy as np
from numba import njit, prange

from .adapter import A, CHARGE_MAX, FOOD_CREDIT, SAME, W_OBS
from .graphworld import KNUTH, Spec, step_cell

CHEAT_CODE = {"": 0, "skip_mutation": 1}


def neighbours(L: int) -> np.ndarray:
    return np.array([[step_cell(L, c, d) for d in range(4)] for c in range(L * L)], dtype=np.int64)


def init_cells(s: Spec, seeds) -> np.ndarray:
    """[E, n] initial cells: Spec.init_cell with each episode's seed (the shape is s's)."""
    ids = np.arange(s.n, dtype=np.int64)
    return np.array([(ids * KNUTH + int(sd)) % s.cells for sd in seeds], dtype=np.int64).reshape(len(seeds), s.n)


@njit(cache=True, nogil=True, boundscheck=False)
def _phase12(n_pred, n_prey, n_food, cell, alive, charge, minprey, predmark):
    p1 = n_pred + n_prey
    for q in range(n_pred, p1):                                   # lowest live prey id per cell
        if alive[q] and minprey[cell[q]] < 0:
            minprey[cell[q]] = q
    for f in range(p1, p1 + n_food):                              # 1 EAT
        if alive[f]:
            q = minprey[cell[f]]
            if q >= 0:
                j = q - n_pred
                v = charge[j] + FOOD_CREDIT
                charge[j] = CHARGE_MAX if v > CHARGE_MAX else v
                alive[f] = False
    for q in range(n_pred, p1):
        if alive[q]:
            minprey[cell[q]] = -1
    for p in range(n_pred):                                       # 2 PREY
        predmark[cell[p]] = 1
    for q in range(n_pred, p1):
        if alive[q] and predmark[cell[q]] != 0:
            alive[q] = False
    for p in range(n_pred):
        predmark[cell[p]] = 0


@njit(cache=True, nogil=True, boundscheck=False)
def _observe(n_pred, n_prey, n_food, t, nb, cell, alive, charge, cnt, obs):
    n = n_pred + n_prey + n_food
    nfood = 0
    for i in range(n):
        if alive[i]:
            k = 0 if i < n_pred else (1 if i < n_pred + n_prey else 2)
            cnt[cell[i], k] += 1
            if k == 2:
                nfood += 1
    for j in range(n_prey):
        q = n_pred + j
        obs[j, 5] = t
        obs[j, 6] = nfood
        obs[j, 7] = charge[j]
        if alive[q]:
            c = cell[q]
            m0 = 0
            m1 = 0
            m2 = 0
            if cnt[c, 0] > 0:
                m0 |= 1 << SAME
            if cnt[c, 1] > 1:                                     # other prey: exclude the slot itself
                m1 |= 1 << SAME
            if cnt[c, 2] > 0:
                m2 |= 1 << SAME
            for d in range(4):
                cc = nb[c, d]
                if cnt[cc, 0] > 0:
                    m0 |= 1 << d
                if cnt[cc, 1] > 0:
                    m1 |= 1 << d
                if cnt[cc, 2] > 0:
                    m2 |= 1 << d
            obs[j, 0] = 1
            obs[j, 1] = c
            obs[j, 2] = m0
            obs[j, 3] = m2
            obs[j, 4] = m1
        else:
            for f in range(5):
                obs[j, f] = 0
    for i in range(n):
        if alive[i]:
            k = 0 if i < n_pred else (1 if i < n_pred + n_prey else 2)
            cnt[cell[i], k] -= 1


@njit(cache=True, nogil=True, boundscheck=False)
def _phase34(n_pred, n_prey, t, nb, cheat, cell, alive, charge, acts, rec_act):
    """acts [S] int64; rec_act [S] int64 out (-1 = slot not live). -> moving actions this tick."""
    for p in range(n_pred):
        cell[p] = nb[cell[p], (p * 7 + t * 3) % 4]
    moving = 0
    for j in range(n_prey):
        q = n_pred + j
        if alive[q]:
            x = ((acts[j] % A) + A) % A
            rec_act[j] = x
            if x != 0:
                moving += 1
                if cheat == 0:
                    cell[q] = nb[cell[q], (x - 1) % 4]
        else:
            rec_act[j] = -1
    for j in range(n_prey):
        if alive[n_pred + j]:
            v = charge[j] + 1
            charge[j] = CHARGE_MAX if v > CHARGE_MAX else v
    return moving


@njit(cache=True, nogil=True, boundscheck=False)
def _record(t, cell, alive, charge, rec_act, rc, ra, rch):
    for i in range(cell.shape[0]):
        rc[t, i] = cell[i] if alive[i] else -1
    for j in range(charge.shape[0]):
        ra[t, j] = rec_act[j]
        rch[t, j] = charge[j]


@njit(parallel=True, nogil=True, boundscheck=False, cache=True)
def _run(L, n_pred, n_prey, n_food, ticks, nb, init, mode, table, W, b, genome_of_env, cheat, record,
         charges, moving, rec_cells, rec_acts, rec_charge):
    E = init.shape[0]
    n = n_pred + n_prey + n_food
    C = L * L
    for e in prange(E):
        cell = init[e].copy()
        alive = np.ones(n, dtype=np.bool_)
        charge = np.zeros(n_prey, dtype=np.int64)
        minprey = np.full(C, -1, dtype=np.int64)
        predmark = np.zeros(C, dtype=np.uint8)
        cnt = np.zeros((C, 3), dtype=np.int32)
        obs = np.zeros((n_prey, W_OBS), dtype=np.uint16)
        acts = np.zeros(n_prey, dtype=np.int64)
        rec_act = np.zeros(n_prey, dtype=np.int64)
        mv = 0
        for t in range(ticks):
            _phase12(n_pred, n_prey, n_food, cell, alive, charge, minprey, predmark)
            if mode == 0:
                for j in range(n_prey):
                    acts[j] = table[e, t, j]
            else:
                _observe(n_pred, n_prey, n_food, t, nb, cell, alive, charge, cnt, obs)
                g = genome_of_env[e]
                for j in range(n_prey):
                    best = 0
                    bv = np.float32(0.0)
                    for k in range(W.shape[1]):
                        s = b[g, k]
                        for f in range(W_OBS):
                            s += W[g, k, f] * np.float32(obs[j, f])
                        if k == 0 or s > bv:
                            bv = s
                            best = k
                    acts[j] = best
            mv += _phase34(n_pred, n_prey, t, nb, cheat, cell, alive, charge, acts, rec_act)
            if record:
                _record(t, cell, alive, charge, rec_act, rec_cells[e], rec_acts[e], rec_charge[e])
        for j in range(n_prey):
            charges[e, j] = charge[j]
        moving[e] = mv


def _outputs(s: Spec, E: int, record: bool):
    shape = (E, s.ticks) if record else (1, 1)
    return (np.zeros((E, s.n_prey), np.int64), np.zeros(E, np.int64),
            np.full(shape + (s.n,), -1, np.int64), np.full(shape + (s.n_prey,), -1, np.int64),
            np.zeros(shape + (s.n_prey,), np.int64))


def _result(s, charges, moving, rc, ra, rch, record):
    out = {"charges": charges, "charge": charges.sum(1), "moving_actions": moving}
    if record:
        out["hashes"] = [digest(s, rc[e], ra[e], rch[e]) for e in range(len(charges))]
    return out


def run_table(s: Spec, seeds, table: np.ndarray, cheat: str = "", record: bool = False) -> dict:
    """table [E, ticks, S] (or [ticks, S], broadcast). -> {charges [E, S], charge [E], moving_actions [E], hashes?}."""
    E = len(seeds)
    table = np.ascontiguousarray(np.broadcast_to(np.asarray(table, np.int64), (E, s.ticks, s.n_prey)))
    out = _outputs(s, E, record)
    _run(s.L, s.n_pred, s.n_prey, s.n_food, s.ticks, neighbours(s.L), init_cells(s, seeds), 0, table,
         np.zeros((1, 1, W_OBS), np.float32), np.zeros((1, 1), np.float32), np.zeros(E, np.int64),
         CHEAT_CODE[cheat], record, *out)
    return _result(s, *out, record)


def run_linear(s: Spec, seeds, W: np.ndarray, b: np.ndarray, genome_of_env=None, cheat: str = "",
               record: bool = False) -> dict:
    """W [G, A, 8] float32, b [G, A] float32, genome_of_env [E] (default: all genome 0)."""
    E = len(seeds)
    W, b = np.ascontiguousarray(W, np.float32), np.ascontiguousarray(b, np.float32)
    goe = np.zeros(E, np.int64) if genome_of_env is None else np.ascontiguousarray(genome_of_env, np.int64)
    out = _outputs(s, E, record)
    _run(s.L, s.n_pred, s.n_prey, s.n_food, s.ticks, neighbours(s.L), init_cells(s, seeds), 1,
         np.zeros((1, 1, 1), np.int64), W, b, goe, CHEAT_CODE[cheat], record, *out)
    return _result(s, *out, record)


def digest(s: Spec, rc, ra, rch) -> str:
    """adapter._Base's sha256 from recorded [ticks, n] cells, [ticks, S] live actions, [ticks, S] charges."""
    h = hashlib.sha256()
    slots = range(s.n_pred, s.n_pred + s.n_prey)
    for t in range(s.ticks):
        line = f"{t}|" + ";".join(f"{i},{int(c)}" for i, c in enumerate(rc[t]) if c >= 0)
        acts = ",".join(f"{q}:{int(ra[t, j])}" for j, q in enumerate(slots) if ra[t, j] >= 0)
        h.update(line.encode("ascii") + b"|" + acts.encode("ascii") + b"|"
                 + ",".join(str(int(v)) for v in rch[t]).encode("ascii"))
    return h.hexdigest()


# ------------------------------------------------------------------ Python-driven batch (any batched policy)
@njit(parallel=True, nogil=True, boundscheck=False, cache=True)
def _batch_p12_obs(n_pred, n_prey, n_food, t, nb, cells, alive, charge, obs):
    C = nb.shape[0]
    for e in prange(cells.shape[0]):
        minprey = np.full(C, -1, dtype=np.int64)
        predmark = np.zeros(C, dtype=np.uint8)
        cnt = np.zeros((C, 3), dtype=np.int32)
        _phase12(n_pred, n_prey, n_food, cells[e], alive[e], charge[e], minprey, predmark)
        _observe(n_pred, n_prey, n_food, t, nb, cells[e], alive[e], charge[e], cnt, obs[e])


@njit(parallel=True, nogil=True, boundscheck=False, cache=True)
def _batch_p34(n_pred, n_prey, t, nb, cheat, cells, alive, charge, acts, rec_act, moving):
    for e in prange(cells.shape[0]):
        moving[e] += _phase34(n_pred, n_prey, t, nb, cheat, cells[e], alive[e], charge[e], acts[e], rec_act[e])


class Batch:
    """E episodes of one spec shape stepped from Python: obs = observe() after phases 1-2, then step(actions [E, S])."""

    def __init__(self, s: Spec, seeds, cheat: str = "", record: bool = False):
        self.s, self.t, self.cheat, self.record = s, 0, CHEAT_CODE[cheat], record
        E = len(seeds)
        self.nb, self.cells = neighbours(s.L), init_cells(s, seeds)
        self.alive = np.ones((E, s.n), np.bool_)
        self.charge = np.zeros((E, s.n_prey), np.int64)
        self.moving = np.zeros(E, np.int64)
        self.obs = np.zeros((E, s.n_prey, W_OBS), np.uint16)
        self.rec_act = np.zeros((E, s.n_prey), np.int64)
        _, _, self.rc, self.ra, self.rch = _outputs(s, E, record)

    def observe(self) -> np.ndarray:
        s = self.s
        _batch_p12_obs(s.n_pred, s.n_prey, s.n_food, self.t, self.nb, self.cells, self.alive, self.charge, self.obs)
        return self.obs

    def step(self, actions) -> None:
        s = self.s
        acts = np.ascontiguousarray(np.asarray(actions, np.int64).reshape(len(self.cells), s.n_prey))
        _batch_p34(s.n_pred, s.n_prey, self.t, self.nb, self.cheat, self.cells, self.alive, self.charge, acts,
                   self.rec_act, self.moving)
        if self.record:
            for e in range(len(self.cells)):
                _record(self.t, self.cells[e], self.alive[e], self.charge[e], self.rec_act[e], self.rc[e], self.ra[e],
                        self.rch[e])
        self.t += 1

    def result(self) -> dict:
        return _result(self.s, self.charge.copy(), self.moving.copy(), self.rc, self.ra, self.rch, self.record)


def run_policy(s: Spec, seeds, policy, cheat: str = "", record: bool = False) -> dict:
    """policy(obs [E, S, 8] uint16, t) -> actions [E, S]."""
    bt = Batch(s, seeds, cheat, record)
    for t in range(s.ticks):
        bt.step(policy(bt.observe(), t))
    return bt.result()


# ------------------------------------------------------------------ reference-side policies for the oracle
def linear_ref_policy(W: np.ndarray, b: np.ndarray, g: int = 0):
    """The linear genome as a RefB2 policy, in plain Python float32 with the kernel's accumulation order."""
    W, b = np.asarray(W, np.float32), np.asarray(b, np.float32)

    def pol(o, t):
        a = np.zeros(len(o), np.int64)
        for j, row in enumerate(o):
            best, bv = 0, None
            for k in range(W.shape[1]):
                s = b[g, k]
                for f in range(W_OBS):
                    s = np.float32(s + W[g, k, f] * np.float32(row[f]))
                if bv is None or s > bv:
                    best, bv = k, s
            a[j] = best
        return a
    return pol


def random_linear(G: int, seed, scale: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    return ((rng.standard_normal((G, A, W_OBS)) * scale).astype(np.float32),
            rng.standard_normal((G, A)).astype(np.float32))
