"""Sense streams for the PTE-C4 tasks on the CPU oracle (C-019-T040, Argus). No torch.

SOURCE AND INDEPENDENCE (recorded, not hidden). DESIGN.md s7 (roles/Ananke/pte/DESIGN.md @ f58362c5e) fixes the
families' semantics (mirror pairs, balanced targets, readout sign rule, cue amplitude) but NOT the order of the ENV
draws, so a bit-exact stream cannot be written from the DESIGN text alone. The draw order below was therefore read
from the owner's prometheus/ananke/envs.py:121-252 (pinned at the worktree base SHA) and re-written here without
torch; the GATE family is the C4 addition (envs.py:185-207, FAMILY_ID 6). This module is a RE-IMPLEMENTATION FROM A
READING of the engine's world generator, not an independent derivation; its correctness is pinned by end-to-end
conformance to the owner's committed numbers (tests/test_conformance.py, admission_R4.json), not by independence.
The dynamics (oracle.py) and the ruler (ruler.py) are the independent parts.

Task envs at a C4 cell (run_c4.task_env, roles/Ananke/pte/c4/run_c4.py:52-62 @ f58362c5e):
    FLIP    = the cell's env;  GATE = the cell's env with family GATE;
    RELAY1H = RELAY with d = 1, trials = 12;  HOLD = EnvSpec defaults with gap 8, trials 12.
"""
from __future__ import annotations

import dataclasses

import numpy as np

from prometheus.ananke.oracle import H, build_topology

ENV_STREAM = 10                                   # DESIGN.md s2 stream id ENV
FAMILY_ID = {"RELAY": 1, "XOR": 2, "MAJ": 3, "FLIP": 4, "HOLD": 5, "GATE": 6}
WORLD_KEY = 0xA11A                                # assays.world_seeds: H(base, 0xA11A, m)


def world_seeds(base: int, M: int) -> list:
    return [H(base, WORLD_KEY, m) for m in range(M)]


@dataclasses.dataclass(frozen=True)
class Env:
    family: str = "RELAY"
    d: int = 3
    delta: int = 8
    gap: int = 8
    cue_len: int = 2
    amp: int = 256
    amp_teacher: int = 128
    amp_dist: int = 64
    trials: int = 16
    block: int = 4
    flip_p: float = 0.3
    n_maj: int = 5
    iti: int = 2
    variant: int = 0

    def period(self) -> int:
        if self.family == "HOLD":
            return self.cue_len + self.gap + 1 + self.iti
        if self.family in ("FLIP", "GATE"):
            return self.delta + 1 + self.cue_len + self.iti
        return self.delta + 1 + self.iti

    def T(self) -> int:
        return self.trials * self.period()


TASKS = ("RELAY1H", "HOLD", "GATE", "FLIP")
TASK_ID = {"RELAY1H": 1, "HOLD": 2, "GATE": 3, "FLIP": 4}
ROLE = {"RELAY1H": "RELAY-mh", "HOLD": "RELAY-mh", "GATE": "RELAY-mh", "FLIP": "FLIP"}
C4_NS = 0xC4001007
REPS = {"R4": dict(prog_len=24, state_dim=3), "R5": dict(prog_len=24, state_dim=3)}


def task_env(cell_env: dict, task: str) -> Env:
    e = Env(**cell_env)
    if task == "FLIP":
        return e
    if task == "GATE":
        return dataclasses.replace(e, family="GATE")
    if task == "RELAY1H":
        return dataclasses.replace(e, family="RELAY", d=1, trials=12)
    if task == "HOLD":
        return Env(family="HOLD", gap=8, trials=12)
    raise KeyError(task)


def rep_physics(cell_phys: dict, rep: str = "R4") -> dict:
    p = dict(cell_phys)
    p.update(REPS[rep])
    return p


_DIST: dict = {}


def dist_matrix(phys: dict) -> np.ndarray:
    """Env distance = BFS hops over the directed neighbour table (random/smallworld), geometric on ring/torus,
    1 off-diagonal for global; unreachable = 10**6."""
    key = tuple(sorted((k, phys[k]) for k in ("topology", "n_sites", "radius", "k_random", "rewire", "topo_seed")))
    if key in _DIST:
        return _DIST[key]
    N = int(phys["n_sites"])
    topo = phys["topology"]
    if topo == "torus":
        s = int(round(N ** 0.5))
        y, x = np.divmod(np.arange(N), s)
        dx = np.abs(x[:, None] - x[None, :]); dy = np.abs(y[:, None] - y[None, :])
        M = np.minimum(dx, s - dx) + np.minimum(dy, s - dy)
    elif topo == "ring":
        i = np.arange(N); dd = np.abs(i[:, None] - i[None, :]); M = np.minimum(dd, N - dd)
    elif topo == "global":
        M = 1 - np.eye(N, dtype=np.int64)
    else:
        nbr, _ = build_topology(phys)
        M = np.full((N, N), 10 ** 6, dtype=np.int64)
        for src in range(N):
            d = {src: 0}
            front = [src]
            while front:
                nxt = []
                for u in front:
                    for v in nbr[u]:
                        v = int(v)
                        if v not in d:
                            d[v] = d[u] + 1
                            nxt.append(v)
                front = nxt
            for v, k in d.items():
                M[src, v] = k
    _DIST[key] = M.astype(np.int64)
    return _DIST[key]


def _pick_at(g, row: np.ndarray, d: int, exclude=()) -> int:
    ex = np.asarray(exclude, dtype=np.int64)
    cand = np.setdiff1d(np.flatnonzero(row == d), ex)
    if cand.size == 0:
        ok = np.setdiff1d(np.flatnonzero((row <= d) & (row > 0)), ex)
        if ok.size:
            cand = ok[row[ok] == row[ok].max()]
        else:
            ok = np.setdiff1d(np.flatnonzero(row > 0), ex)
            if ok.size == 0:
                ok = np.setdiff1d(np.arange(row.size), ex)
            cand = ok[row[ok] == row[ok].min()]
    return int(cand[g.integers(cand.size)])


def _coin(g, n: int) -> np.ndarray:
    return np.where(g.random(n) < 0.5, 1, -1)


@dataclasses.dataclass
class Episode:
    sidx: np.ndarray        # [M, K] sensed sites (duplicates add)
    sval: np.ndarray        # [T, M, K] values (0 = silent)
    read_site: np.ndarray   # [M]
    ro_tick: np.ndarray     # [M, trials]
    y: np.ndarray           # [M, trials]
    scored: np.ndarray      # [M, trials] bool
    env: Env
    N: int

    def sense(self, sval=None) -> np.ndarray:
        """[T, M, N] SENSE field: scatter-ADD of the K channels (engine.py:303 scatter_add_)."""
        sv = self.sval if sval is None else sval
        T, M, K = sv.shape
        out = np.zeros((T, M, self.N), dtype=np.int64)
        for m in range(M):
            for k in range(K):
                out[:, m, self.sidx[m, k]] += sv[:, m, k]
        return out


def build(phys: dict, env: Env, seeds) -> Episode:
    Mw = len(seeds)
    assert Mw % 2 == 0, "worlds come in mirror pairs"
    N = int(phys["n_sites"])
    T, tr, Pd, fam = env.T(), env.trials, env.period(), env.family
    assert tr % 2 == 0
    if fam not in ("RELAY", "FLIP", "HOLD", "GATE"):
        raise ValueError(f"family {fam} not supported by this evaluator (C4 ladder only)")
    Dm = dist_matrix(phys)
    K = {"RELAY": 1, "FLIP": 2, "HOLD": 1, "GATE": 2}[fam]
    sidx = np.zeros((Mw, K), dtype=np.int64)
    sval = np.zeros((T, Mw, K), dtype=np.int64)
    rd = np.zeros(Mw, dtype=np.int64)
    ro = np.zeros((Mw, tr), dtype=np.int64)
    y = np.zeros((Mw, tr), dtype=np.int64)
    scored = np.ones((Mw, tr), dtype=bool)
    for b in range(Mw):
        lead = int(seeds[b - (b % 2)])
        sg = -1 if b % 2 else 1
        g = np.random.default_rng(H(lead, ENV_STREAM, FAMILY_ID[fam], env.variant))
        if fam == "HOLD":
            a = int(g.integers(N))
            sidx[b, 0] = a; rd[b] = a
            yy = _coin(g, tr)
            for k in range(tr):
                t0 = k * Pd
                sval[t0:t0 + env.cue_len, b, 0] = sg * env.amp * yy[k]
                ds = g.choice([-1, 1], size=env.gap)
                sval[t0 + env.cue_len:t0 + env.cue_len + env.gap, b, 0] = sg * env.amp_dist * ds
                ro[b, k] = t0 + env.cue_len + env.gap
            y[b] = sg * yy
            continue
        s = int(g.integers(N))
        a = _pick_at(g, Dm[s], env.d)
        sidx[b, 0] = s; rd[b] = a
        if fam == "GATE":
            sidx[b, 1] = a                                   # context sensed at the actuator
            assert tr % env.block == 0
            x = _coin(g, tr)
            cc = np.repeat(_coin(g, tr // env.block), env.block)
            for k in range(tr):
                t0 = k * Pd
                sval[t0:t0 + env.cue_len, b, 0] = sg * env.amp * x[k]
                if k % env.block == 0:
                    sval[t0:t0 + env.cue_len, b, 1] = env.amp_teacher * cc[k]   # twins share the context
                ro[b, k] = t0 + env.delta
            y[b] = sg * cc * x
            continue
        x = _coin(g, tr)
        if fam == "RELAY":
            yy = x
        else:                                                # FLIP
            sidx[b, 1] = a                                   # teacher at the actuator
            assert tr % env.block == 0 and (tr // env.block) % 2 == 0
            m0 = int(g.choice([-1, 1]))
            m = np.array([m0 * (-1) ** (k // env.block) for k in range(tr)])
            yy = m * x
            scored[b] = (np.arange(tr) % env.block) != 0
        for k in range(tr):
            t0 = k * Pd
            sval[t0:t0 + env.cue_len, b, 0] = sg * env.amp * x[k]
            ro[b, k] = t0 + env.delta
            if fam == "FLIP":
                t1 = t0 + env.delta + 1
                sval[t1:t1 + env.cue_len, b, 1] = sg * env.amp_teacher * yy[k]
        y[b] = sg * yy
    return Episode(sidx, sval, rd, ro, y, scored, env, N)


def per_trial(ep: Episode, s0_trace: np.ndarray) -> np.ndarray:
    """DESIGN s7 readout: 1 if sign(S0) == y, .5 if S0 == 0, else 0. s0_trace [T, M, N]."""
    Mw = ep.y.shape[0]
    s0 = s0_trace[ep.ro_tick, np.arange(Mw)[:, None], ep.read_site[:, None]]
    return np.where(s0 == 0, 0.5, (np.sign(s0) == ep.y).astype(float))
