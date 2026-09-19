"""Ares substrate: a generic, inspectable, batched graph organism.

One organism is a small directed graph. Every node has a primitive op, a
bias, a keep coefficient (how much of its previous value survives a
tick) and two weighted input ports. Edges carry scalar values and may
carry a local plasticity rate (zero unless mutation sets it). Nothing
here is named after a cognitive function; the ops are arithmetic.

A population is stored as stacked numpy arrays so that P organisms run
in lockstep on the same batched world (thousands of tiny evaluations
per second). Node layout: [0, OBS) inputs, [OBS, OBS+H) hidden,
[OBS+H, N) outputs. Action = argmax over the output nodes.
"""
from __future__ import annotations

import numpy as np

OBS_DIM = 6
N_OUT = 3
OPS = ["ADD", "MUL", "MAX", "MIN", "THRESH", "GATE", "TANH", "DIFF", "CONST"]
N_OPS = len(OPS)
V_CLIP = 8.0
W_CLIP = 4.0

MUTATIONS = [
    "add_node", "remove_node", "add_edge", "remove_edge", "alter_op",
    "alter_bias", "alter_keep", "perturb_weight", "alter_plasticity",
    "duplicate_node",
]


class Config:
    """Substrate limits. `n_hidden` and `ticks` are the scarcity knobs."""

    def __init__(self, n_hidden=8, ticks=2, allow_topology=True,
                 allow_keep=True, allow_plasticity=True, reset_each_step=False):
        self.n_hidden = int(n_hidden)
        self.ticks = int(ticks)
        self.allow_topology = bool(allow_topology)
        self.allow_keep = bool(allow_keep)
        self.allow_plasticity = bool(allow_plasticity)
        # reset_each_step: hidden/output values zeroed at every world step
        # (the "no persistent state" ablation; with keep forced to 0 the
        # only carrier left is within-step recurrence across ticks).
        self.reset_each_step = bool(reset_each_step)

    @property
    def n(self):
        return OBS_DIM + self.n_hidden + N_OUT

    def to_dict(self):
        return dict(n_hidden=self.n_hidden, ticks=self.ticks,
                    allow_topology=self.allow_topology, allow_keep=self.allow_keep,
                    allow_plasticity=self.allow_plasticity,
                    reset_each_step=self.reset_each_step)


class Population:
    """Stacked genomes. All arrays have leading dimension P."""

    def __init__(self, cfg: Config, P: int):
        n = cfg.n
        self.cfg = cfg
        self.P = P
        self.alive = np.zeros((P, n), dtype=bool)
        self.alive[:, :OBS_DIM] = True
        self.alive[:, n - N_OUT:] = True
        self.op = np.zeros((P, n), dtype=np.int8)
        self.bias = np.zeros((P, n), dtype=np.float32)
        self.keep = np.zeros((P, n), dtype=np.float32)
        self.W1 = np.zeros((P, n, n), dtype=np.float32)   # W1[p,i,j]: j -> i, port 1
        self.W2 = np.zeros((P, n, n), dtype=np.float32)   # port 2
        self.R = np.zeros((P, n, n), dtype=np.float32)    # plasticity rate on W1
        self.ids = np.arange(P, dtype=np.int64)
        self.parents = -np.ones(P, dtype=np.int64)

    # ----- slicing / copying -----
    def copy(self):
        q = Population(self.cfg, self.P)
        for k in ("alive", "op", "bias", "keep", "W1", "W2", "R", "ids", "parents"):
            setattr(q, k, getattr(self, k).copy())
        return q

    def select(self, idx):
        idx = np.asarray(idx)
        q = Population(self.cfg, len(idx))
        for k in ("alive", "op", "bias", "keep", "W1", "W2", "R", "ids", "parents"):
            setattr(q, k, getattr(self, k)[idx].copy())
        return q

    def genome(self, p):
        """One organism as a plain dict (for JSON fossils)."""
        n = self.cfg.n
        edges = []
        for i in range(n):
            for j in range(n):
                if self.W1[p, i, j] != 0 or self.W2[p, i, j] != 0 or self.R[p, i, j] != 0:
                    edges.append([int(j), int(i), float(self.W1[p, i, j]),
                                  float(self.W2[p, i, j]), float(self.R[p, i, j])])
        return dict(
            cfg=self.cfg.to_dict(), id=int(self.ids[p]), parent=int(self.parents[p]),
            alive=[int(a) for a in self.alive[p]],
            op=[OPS[o] for o in self.op[p]],
            bias=[float(b) for b in self.bias[p]],
            keep=[float(k) for k in self.keep[p]],
            edges=edges,  # [src, dst, w1, w2, plasticity]
        )

    @staticmethod
    def from_genomes(genomes, cfg=None):
        cfg = cfg or Config(**genomes[0]["cfg"])
        pop = Population(cfg, len(genomes))
        for p, g in enumerate(genomes):
            pop.alive[p] = np.array(g["alive"], dtype=bool)
            pop.op[p] = np.array([OPS.index(o) for o in g["op"]], dtype=np.int8)
            pop.bias[p] = np.array(g["bias"], dtype=np.float32)
            pop.keep[p] = np.array(g["keep"], dtype=np.float32)
            for src, dst, w1, w2, r in g["edges"]:
                pop.W1[p, dst, src] = w1
                pop.W2[p, dst, src] = w2
                pop.R[p, dst, src] = r
            pop.ids[p] = g.get("id", p)
            pop.parents[p] = g.get("parent", -1)
        return pop


# ----------------------------------------------------------------------
# initialisation and mutation
# ----------------------------------------------------------------------

def _hidden_slots(cfg):
    return np.arange(OBS_DIM, OBS_DIM + cfg.n_hidden)


def _out_slots(cfg):
    return np.arange(cfg.n - N_OUT, cfg.n)


def random_population(cfg: Config, P: int, rng: np.random.Generator, next_id=0):
    """Near-minimal random organisms: 0-2 hidden nodes, a few edges."""
    pop = Population(cfg, P)
    n = cfg.n
    pop.op[:] = rng.integers(0, N_OPS, size=(P, n)).astype(np.int8)
    pop.bias[:] = rng.normal(0, 0.5, size=(P, n)).astype(np.float32)
    for p in range(P):
        k = rng.integers(0, 3) if cfg.n_hidden > 0 else 0
        hs = rng.choice(_hidden_slots(cfg), size=min(k, cfg.n_hidden), replace=False)
        pop.alive[p, hs] = True
        targets = np.concatenate([hs, _out_slots(cfg)])
        sources = np.concatenate([np.arange(OBS_DIM), hs])
        for _ in range(rng.integers(2, 6)):
            i = rng.choice(targets)
            j = rng.choice(sources)
            port = pop.W1 if rng.random() < 0.5 else pop.W2
            port[p, i, j] = rng.normal(0, 1.0)
    pop.ids = np.arange(next_id, next_id + P, dtype=np.int64)
    return pop


def _valid_targets(pop, p):
    a = pop.alive[p].copy()
    a[:OBS_DIM] = False
    return np.flatnonzero(a)


def _valid_sources(pop, p):
    return np.flatnonzero(pop.alive[p])


def _existing_edges(pop, p):
    m = (pop.W1[p] != 0) | (pop.W2[p] != 0)
    return np.argwhere(m)  # rows of [i, j]


def mutate_one(pop: Population, p: int, rng: np.random.Generator, n_mut=None):
    """Apply 1 + Poisson(1) mutations in place to organism p. Returns the
    list of mutation names applied (for ancestry)."""
    cfg = pop.cfg
    if n_mut is None:
        n_mut = 1 + rng.poisson(1.0)
    applied = []
    weights = np.array([1.0, 0.6, 2.0, 1.0, 1.0, 1.5, 1.0 if cfg.allow_keep else 0.0,
                        3.0, 0.7 if cfg.allow_plasticity else 0.0, 0.5])
    if not cfg.allow_topology:
        for name in ("add_node", "remove_node", "add_edge", "remove_edge", "duplicate_node"):
            weights[MUTATIONS.index(name)] = 0.0
    weights = weights / weights.sum()
    for _ in range(n_mut):
        m = MUTATIONS[rng.choice(len(MUTATIONS), p=weights)]
        ok = _apply(pop, p, m, rng)
        if ok:
            applied.append(m)
    return applied


def _apply(pop, p, m, rng):
    cfg = pop.cfg
    n = cfg.n
    if m == "add_node":
        dead = np.flatnonzero(~pop.alive[p, OBS_DIM:OBS_DIM + cfg.n_hidden]) + OBS_DIM
        if len(dead) == 0:
            return False
        h = rng.choice(dead)
        pop.alive[p, h] = True
        pop.op[p, h] = rng.integers(0, N_OPS)
        pop.bias[p, h] = rng.normal(0, 0.5)
        pop.keep[p, h] = 0.0
        src = rng.choice(_valid_sources(pop, p))
        dst = rng.choice(_valid_targets(pop, p))
        pop.W1[p, h, src] = rng.normal(0, 1.0)
        port = pop.W1 if rng.random() < 0.5 else pop.W2
        port[p, dst, h] = rng.normal(0, 1.0)
        return True
    if m == "remove_node":
        hs = np.flatnonzero(pop.alive[p, OBS_DIM:OBS_DIM + cfg.n_hidden]) + OBS_DIM
        if len(hs) == 0:
            return False
        h = rng.choice(hs)
        pop.alive[p, h] = False
        pop.W1[p, h, :] = 0; pop.W1[p, :, h] = 0
        pop.W2[p, h, :] = 0; pop.W2[p, :, h] = 0
        pop.R[p, h, :] = 0; pop.R[p, :, h] = 0
        pop.keep[p, h] = 0
        return True
    if m == "add_edge":
        i = rng.choice(_valid_targets(pop, p))
        j = rng.choice(_valid_sources(pop, p))
        port = pop.W1 if rng.random() < 0.5 else pop.W2
        port[p, i, j] = rng.normal(0, 1.0)
        return True
    if m == "remove_edge":
        e = _existing_edges(pop, p)
        if len(e) == 0:
            return False
        i, j = e[rng.integers(len(e))]
        pop.W1[p, i, j] = 0; pop.W2[p, i, j] = 0; pop.R[p, i, j] = 0
        return True
    if m == "alter_op":
        t = _valid_targets(pop, p)
        i = rng.choice(t)
        pop.op[p, i] = rng.integers(0, N_OPS)
        return True
    if m == "alter_bias":
        i = rng.choice(_valid_targets(pop, p))
        pop.bias[p, i] += rng.normal(0, 0.5)
        return True
    if m == "alter_keep":
        hs = np.flatnonzero(pop.alive[p, OBS_DIM:]) + OBS_DIM
        i = rng.choice(hs)
        pop.keep[p, i] = float(np.clip(pop.keep[p, i] + rng.normal(0, 0.3), 0.0, 0.98))
        return True
    if m == "perturb_weight":
        e = _existing_edges(pop, p)
        if len(e) == 0:
            return False
        i, j = e[rng.integers(len(e))]
        if pop.W1[p, i, j] != 0 and (pop.W2[p, i, j] == 0 or rng.random() < 0.5):
            pop.W1[p, i, j] = np.clip(pop.W1[p, i, j] + rng.normal(0, 0.5), -W_CLIP, W_CLIP)
        else:
            pop.W2[p, i, j] = np.clip(pop.W2[p, i, j] + rng.normal(0, 0.5), -W_CLIP, W_CLIP)
        return True
    if m == "alter_plasticity":
        e = np.argwhere(pop.W1[p] != 0)
        if len(e) == 0:
            return False
        i, j = e[rng.integers(len(e))]
        if pop.R[p, i, j] != 0 and rng.random() < 0.3:
            pop.R[p, i, j] = 0.0
        else:
            pop.R[p, i, j] = float(np.clip(pop.R[p, i, j] + rng.normal(0, 0.05), -0.2, 0.2))
        return True
    if m == "duplicate_node":
        hs = np.flatnonzero(pop.alive[p, OBS_DIM:OBS_DIM + cfg.n_hidden]) + OBS_DIM
        dead = np.flatnonzero(~pop.alive[p, OBS_DIM:OBS_DIM + cfg.n_hidden]) + OBS_DIM
        if len(hs) == 0 or len(dead) == 0:
            return False
        h = rng.choice(hs); d = rng.choice(dead)
        pop.alive[p, d] = True
        pop.op[p, d] = pop.op[p, h]; pop.bias[p, d] = pop.bias[p, h]; pop.keep[p, d] = pop.keep[p, h]
        pop.W1[p, d, :] = pop.W1[p, h, :]; pop.W2[p, d, :] = pop.W2[p, h, :]; pop.R[p, d, :] = pop.R[p, h, :]
        pop.W1[p, :, d] = pop.W1[p, :, h]; pop.W2[p, :, d] = pop.W2[p, :, h]; pop.R[p, :, d] = pop.R[p, :, h]
        return True
    raise ValueError(m)


def splice_subgraph(dst_pop, dp, src_pop, sp, nodes, rng):
    """Transplant hidden nodes `nodes` (indices in src organism sp) with
    their mutual edges into organism dp. External connections of the
    subgraph are re-attached to random valid nodes of the host. Returns
    the list of host slots used, or None if the host has no room."""
    cfg = dst_pop.cfg
    dead = np.flatnonzero(~dst_pop.alive[dp, OBS_DIM:OBS_DIM + cfg.n_hidden]) + OBS_DIM
    if len(dead) < len(nodes):
        return None
    slots = rng.choice(dead, size=len(nodes), replace=False)
    m = {int(s): int(d) for s, d in zip(nodes, slots)}
    for s, d in m.items():
        dst_pop.alive[dp, d] = True
        dst_pop.op[dp, d] = src_pop.op[sp, s]
        dst_pop.bias[dp, d] = src_pop.bias[sp, s]
        dst_pop.keep[dp, d] = src_pop.keep[sp, s]
    n = cfg.n
    for s, d in m.items():
        # incoming edges of s
        for j in range(src_pop.cfg.n):
            for A_src, A_dst in ((src_pop.W1, dst_pop.W1), (src_pop.W2, dst_pop.W2), (src_pop.R, dst_pop.R)):
                w = A_src[sp, s, j]
                if w == 0:
                    continue
                if j in m:
                    A_dst[dp, d, m[j]] = w
                elif j < OBS_DIM:
                    A_dst[dp, d, j] = w            # inputs share layout
                else:
                    A_dst[dp, d, rng.choice(_valid_sources(dst_pop, dp))] = w
        # outgoing edges of s to nodes outside the subgraph
        for i in range(src_pop.cfg.n):
            if i in m:
                continue
            for A_src, A_dst in ((src_pop.W1, dst_pop.W1), (src_pop.W2, dst_pop.W2), (src_pop.R, dst_pop.R)):
                w = A_src[sp, i, s]
                if w == 0:
                    continue
                if i >= src_pop.cfg.n - N_OUT:
                    A_dst[dp, n - N_OUT + (i - (src_pop.cfg.n - N_OUT)), d] = w
                else:
                    A_dst[dp, rng.choice(_valid_targets(dst_pop, dp)), d] = w
    return [int(x) for x in slots]


# ----------------------------------------------------------------------
# execution
# ----------------------------------------------------------------------

class Runtime:
    """Mutable per-lifetime state for a population: node values and the
    (possibly plastic) live copy of W1."""

    def __init__(self, pop: Population):
        self.pop = pop
        self.cfg = pop.cfg
        self.v = np.zeros((pop.P, pop.cfg.n), dtype=np.float32)
        self.W1 = pop.W1.copy()
        self.plastic = bool(pop.cfg.allow_plasticity) and bool(np.any(pop.R != 0))
        self.keep = pop.keep if pop.cfg.allow_keep else np.zeros_like(pop.keep)
        self.mask = pop.alive.astype(np.float32)

    def reset(self):
        self.v[:] = 0.0
        self.W1[:] = self.pop.W1

    def step(self, obs: np.ndarray) -> np.ndarray:
        """One world step: `obs` (P, OBS_DIM) -> actions (P,) ints."""
        pop, cfg = self.pop, self.cfg
        if cfg.reset_each_step:
            self.v[:, OBS_DIM:] = 0.0
        v = self.v
        for _ in range(cfg.ticks):
            v[:, :OBS_DIM] = obs
            pre1 = np.einsum("pij,pj->pi", self.W1, v)
            pre2 = np.einsum("pij,pj->pi", pop.W2, v)
            f = _apply_ops(pop.op, pre1, pre2, pop.bias)
            new = self.keep * v + (1.0 - self.keep) * f
            new = np.clip(new, -V_CLIP, V_CLIP) * self.mask
            v[:, OBS_DIM:] = new[:, OBS_DIM:]
            if self.plastic:
                dw = pop.R * (v[:, :, None] * v[:, None, :])
                self.W1 = np.clip(self.W1 + dw, -W_CLIP, W_CLIP)
        out = v[:, cfg.n - N_OUT:]
        return np.argmax(out, axis=1)


def _apply_ops(op, pre1, pre2, b):
    f = np.empty_like(pre1)
    s = pre1 + pre2 + b
    np.copyto(f, s)                                              # ADD default
    f = np.where(op == 1, pre1 * pre2 + b, f)                    # MUL
    f = np.where(op == 2, np.maximum(pre1, pre2) + b, f)         # MAX
    f = np.where(op == 3, np.minimum(pre1, pre2) + b, f)         # MIN
    f = np.where(op == 4, (pre1 > pre2 + b).astype(np.float32), f)  # THRESH
    f = np.where(op == 5, np.where(pre2 > b, pre1, 0.0), f)      # GATE
    f = np.where(op == 6, np.tanh(s), f)                         # TANH
    f = np.where(op == 7, pre1 - pre2 + b, f)                    # DIFF
    f = np.where(op == 8, b, f)                                  # CONST
    return f.astype(np.float32)


# ----------------------------------------------------------------------
# structural measures
# ----------------------------------------------------------------------

def adjacency(pop: Population):
    """(P, n, n) bool, A[p,i,j] = edge j -> i among alive nodes."""
    A = (pop.W1 != 0) | (pop.W2 != 0)
    a = pop.alive
    return A & a[:, :, None] & a[:, None, :]


def structure_stats(pop: Population):
    """Per-organism structural measures, vectorised. Returns dict of (P,) arrays."""
    cfg = pop.cfg
    n = cfg.n
    A = adjacency(pop)
    hid = np.zeros(n, dtype=bool); hid[OBS_DIM:OBS_DIM + cfg.n_hidden] = True
    n_hidden = (pop.alive & hid).sum(1)
    n_edges = A.sum((1, 2))
    keep_eff = pop.keep if cfg.allow_keep else np.zeros_like(pop.keep)
    alive_nonin = pop.alive.copy(); alive_nonin[:, :OBS_DIM] = False
    n_keep = ((keep_eff > 0.3) & alive_nonin).sum(1)
    mean_keep = np.where(alive_nonin.sum(1) > 0,
                         (keep_eff * alive_nonin).sum(1) / np.maximum(alive_nonin.sum(1), 1), 0.0)
    n_plastic = ((pop.R != 0) & A).sum((1, 2)) if cfg.allow_plasticity else np.zeros(pop.P, int)
    # recurrence: nodes on a directed cycle (reachability via boolean powers)
    reach = A.copy()
    Ai = A.astype(np.int32)
    Ri = reach.astype(np.int32)
    for _ in range(n):
        Ri = ((Ri + np.matmul(Ri, Ai)) > 0).astype(np.int32)
    on_cycle = (np.diagonal(Ri, axis1=1, axis2=2) > 0) & pop.alive
    n_cyclic = on_cycle.sum(1)
    self_loops = (np.diagonal(A, axis1=1, axis2=2) & pop.alive).sum(1)
    two_cycles = (A & A.transpose(0, 2, 1)).sum((1, 2)) // 2 - 0  # counts i<->j pairs (self loops counted once each below)
    two_cycles = two_cycles - self_loops
    gate_like = ((pop.op == 5) | (pop.op == 1) | (pop.op == 4)) & alive_nonin
    n_gate_like = gate_like.sum(1)
    op_hist = np.stack([((pop.op == k) & alive_nonin).sum(1) for k in range(N_OPS)], axis=1)
    return dict(n_hidden=n_hidden, n_edges=n_edges, n_keep=n_keep, mean_keep=mean_keep,
                n_plastic=n_plastic, n_cyclic=n_cyclic, self_loops=self_loops,
                two_cycles=two_cycles, n_gate_like=n_gate_like, op_hist=op_hist)


def structural_diversity(pop: Population, rng, k=32):
    """Mean pairwise distance among k sampled organisms: op-vector Hamming
    over alive slots plus 1 - Jaccard of edge sets."""
    idx = rng.choice(pop.P, size=min(k, pop.P), replace=False)
    A = adjacency(pop)[idx].reshape(len(idx), -1)
    ops = np.where(pop.alive[idx], pop.op[idx], -1)
    d = []
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            ham = np.mean(ops[a] != ops[b])
            inter = np.sum(A[a] & A[b]); union = np.sum(A[a] | A[b])
            jac = 1.0 - (inter / union if union > 0 else 1.0)
            d.append(ham + jac)
    return float(np.mean(d)) if d else 0.0


def ablation_population(pop: Population, p: int):
    """Champion p plus one variant per alive hidden node with that node
    removed. Returns (Population, list of removed node indices; first
    entry is None for the intact original)."""
    cfg = pop.cfg
    hs = np.flatnonzero(pop.alive[p, OBS_DIM:OBS_DIM + cfg.n_hidden]) + OBS_DIM
    idx = [p] * (1 + len(hs))
    var = pop.select(idx)
    removed = [None]
    for k, h in enumerate(hs, start=1):
        var.alive[k, h] = False
        var.W1[k, h, :] = 0; var.W1[k, :, h] = 0
        var.W2[k, h, :] = 0; var.W2[k, :, h] = 0
        var.R[k, h, :] = 0; var.R[k, :, h] = 0
        removed.append(int(h))
    return var, removed
