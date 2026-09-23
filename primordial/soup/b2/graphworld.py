"""B2 GraphWorld toy: world state as boolean sparse relations, rules as graph algebra.

SPEC (every form implements exactly this; integer only, no randomness beyond ids/ticks)
  lattice   L x L torus, cell c = y*L + x
  entities  n_pred predators (kind 0), n_prey prey (kind 1), n_food food (kind 2),
            id order: predators, prey, food. Initial cell of id i: (i * 2654435761 + seed) % (L*L)
  state     AT (entity x cell, one-hot per live entity), ALIVE (entity)
  derived   COLOC = AT . AT^T                        (same cell)
            SEES  = AT . (ADJ + I) . AT^T            (same or 4-adjacent cell)
            THREATENS = SEES masked rows=pred, cols=prey
            OWNS  = COLOC masked rows=prey, cols=food
  tick t, in order:
    1 EAT     food f dies if any live prey is co-located (OWNS column any)
    2 PREY    prey q dies if any live predator is co-located (COLOC pred->prey any)
              (computed on the state AFTER step 1)
    3 MOVE    every live pred/prey moves one cell: dir = (id*7 + t*3 + flee) % 4,
              flee = 1 iff a live prey is THREATENED (computed after step 2); predators flee = 0.
              dir 0:+x 1:+y 2:-x 3:-y on the torus. Food never moves.
  trace     sha256 over per tick: "t|" + ";".join(f"{id},{cell}" for live ids ascending)

Forms: `ref` (plain Python, the authority), `gb` (python-graphblas: mxm / ewise / masks),
FalkorDB Cypher in cypher_world.py. cheat="no_flee" ignores THREATENS.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

KNUTH = 2654435761


@dataclass(frozen=True)
class Spec:
    L: int
    n_pred: int
    n_prey: int
    n_food: int
    ticks: int
    seed: int

    @property
    def n(self) -> int:
        return self.n_pred + self.n_prey + self.n_food

    @property
    def cells(self) -> int:
        return self.L * self.L

    def kind(self, i: int) -> int:
        return 0 if i < self.n_pred else (1 if i < self.n_pred + self.n_prey else 2)

    def init_cell(self, i: int) -> int:
        return (i * KNUTH + self.seed) % self.cells


def step_cell(L: int, c: int, d: int) -> int:
    x, y = c % L, c // L
    if d == 0:
        x = (x + 1) % L
    elif d == 1:
        y = (y + 1) % L
    elif d == 2:
        x = (x - 1) % L
    else:
        y = (y - 1) % L
    return y * L + x


def _line(t: int, cells: dict) -> bytes:
    return (f"{t}|" + ";".join(f"{i},{cells[i]}" for i in sorted(cells))).encode("ascii")


# ------------------------------------------------------------------ reference
def run_ref(s: Spec, cheat: str = "") -> str:
    cell = {i: s.init_cell(i) for i in range(s.n)}
    h = hashlib.sha256()
    for t in range(s.ticks):
        pred = [i for i in cell if s.kind(i) == 0]
        prey = [i for i in cell if s.kind(i) == 1]
        food = [i for i in cell if s.kind(i) == 2]
        prey_cells = {cell[q] for q in prey}
        for f in food:                                   # 1 EAT
            if cell[f] in prey_cells:
                del cell[f]
        pred_cells = {cell[p] for p in pred}
        for q in prey:                                   # 2 PREY
            if cell[q] in pred_cells:
                del cell[q]
        prey = [q for q in prey if q in cell]
        near = set()                                     # 3 MOVE: cells a predator sees
        for p in pred:
            c = cell[p]
            near.add(c)
            near.update(step_cell(s.L, c, d) for d in range(4))
        for i in pred + prey:
            flee = 1 if (s.kind(i) == 1 and cell[i] in near and cheat != "no_flee") else 0
            cell[i] = step_cell(s.L, cell[i], (i * 7 + t * 3 + flee) % 4)
        h.update(_line(t, cell))
    return h.hexdigest()


# ------------------------------------------------------------------ graphblas
def run_gb(s: Spec, cheat: str = "") -> str:
    import graphblas as gb
    from graphblas import Matrix, Vector, binary, monoid, semiring

    n, C, L = s.n, s.cells, s.L
    lor_land = semiring.lor_land
    # static relations
    move = []
    for d in range(4):
        src = np.arange(C)
        dst = np.array([step_cell(L, c, d) for c in range(C)])
        move.append(Matrix.from_coo(src, dst, True, nrows=C, ncols=C, dtype=bool))
    adj_i = move[0].ewise_add(move[1], binary.lor).new()
    for d in (2, 3):
        adj_i = adj_i.ewise_add(move[d], binary.lor).new()
    eye = Matrix.from_coo(np.arange(C), np.arange(C), True, nrows=C, ncols=C, dtype=bool)
    adj_i = adj_i.ewise_add(eye, binary.lor).new()                # ADJ + I
    kind = np.array([s.kind(i) for i in range(n)])
    ids = np.arange(n)
    kvec = [Vector.from_coo(ids[kind == k], True, size=n, dtype=bool) for k in range(3)]

    AT = Matrix.from_coo(ids, [s.init_cell(i) for i in ids], True, nrows=n, ncols=C, dtype=bool)
    h = hashlib.sha256()
    for t in range(s.ticks):
        alive = AT.reduce_rowwise(monoid.lor).new()               # live ids
        # 1 EAT: OWNS = COLOC masked prey x food -> food column any
        prey_rows = alive.ewise_mult(kvec[1], binary.land).new()
        food_rows = alive.ewise_mult(kvec[2], binary.land).new()
        pred_rows = alive.ewise_mult(kvec[0], binary.land).new()
        prey_cells = AT.T.mxv(prey_rows, lor_land).new()          # cell has a live prey
        food_hit = AT.mxv(prey_cells, lor_land).new(mask=food_rows.S)
        AT = _drop_rows(AT, food_hit)
        # 2 PREY
        pred_cells = AT.T.mxv(pred_rows, lor_land).new()
        prey_hit = AT.mxv(pred_cells, lor_land).new(mask=prey_rows.S)
        AT = _drop_rows(AT, prey_hit)
        prey_rows = prey_rows.dup(mask=~prey_hit.S) if prey_hit.nvals else prey_rows
        # 3 MOVE: THREATENED prey = AT . (ADJ+I) . AT^T  over pred->prey, as a vector
        seen_cells = adj_i.T.mxv(pred_cells, lor_land).new()      # cells within 1 of a predator
        threatened = AT.mxv(seen_cells, lor_land).new(mask=prey_rows.S)
        movers = pred_rows.ewise_add(prey_rows, binary.lor).new()
        idx, _ = movers.to_coo()
        flee = np.zeros(n, dtype=np.int64)
        if cheat != "no_flee" and threatened.nvals:
            ti, tv = threatened.to_coo()
            flee[ti[tv]] = 1
        dirs = (ids * 7 + t * 3 + flee) % 4
        new_at = Matrix(bool, n, C)
        stay = food_rows.dup(mask=~food_hit.S) if food_hit.nvals else food_rows
        if stay.nvals:
            new_at << _select_rows(AT, stay)
        for d in range(4):
            sel = idx[dirs[idx] == d]
            if len(sel) == 0:
                continue
            rows = Vector.from_coo(sel, True, size=n, dtype=bool)
            moved = _select_rows(AT, rows).mxm(move[d], lor_land).new()
            new_at = new_at.ewise_add(moved, binary.lor).new()
        AT = new_at
        r, c, _ = AT.to_coo()
        h.update(_line(t, dict(zip(r.tolist(), c.tolist()))))
    return h.hexdigest()


def _select_rows(M, rows):
    """M restricted to rows where `rows` is True: D(rows) . M"""
    from graphblas import semiring
    from graphblas import Matrix
    n = M.nrows
    ri, rv = rows.to_coo()
    D = Matrix.from_coo(ri[rv], ri[rv], True, nrows=n, ncols=n, dtype=bool)
    return D.mxm(M, semiring.lor_land).new()


def _drop_rows(M, hit):
    if hit.nvals == 0:
        return M
    hi, hv = hit.to_coo()
    dead = hi[hv]
    if len(dead) == 0:
        return M
    from graphblas import Vector
    keep = Vector.from_coo(np.setdiff1d(np.arange(M.nrows), dead), True, size=M.nrows, dtype=bool)
    return _select_rows(M, keep)
