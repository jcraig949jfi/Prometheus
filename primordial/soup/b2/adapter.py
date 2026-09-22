"""E-R15-2: graphworld_b2 as a CONTROLLABLE world (operator 15 R15-2, predicate bus 1789455548741-0).

The B2 toy (graphworld.py) had no action channel, no observation vector and no objective. This adapter keeps its
relational state and rules (EAT, PREY, predator MOVE) and hands the PREY to a policy.

  world     B2 Spec(L, n_pred, n_prey, n_food, ticks, seed); initial cells = Spec.init_cell; predators keep the SPEC
            move dir (id*7 + t*3) % 4 (no flee); food never moves.  2 <= L <= 255.
  slots     S = n_prey; slot j = prey id n_pred + j. A dead prey keeps its slot (alive = 0).
  tick t    1 EAT   food f dies if a live prey is co-located; +FOOD_CREDIT charge to the LOWEST-id co-located prey
            2 PREY  a prey dies if a live predator is co-located (state after 1)
            obs     [S, W_OBS] uint16, read from the relations after 2:
                      0 alive  1 cell (y*L + x)  2 predator mask  3 food mask  4 other-prey mask  5 t
                      6 live food count  7 own charge
                    mask bit 4 = an entity of that kind in the same cell (COLOC), bit d = in MOVE-neighbour d (0..3)
            3 MOVE  action a per slot, read a % 8: 0 = ABSTAIN (no AT mutation, the prey stays);
                    1..7 = step along MOVE edge d = (a - 1) % 4. Predators move by SPEC. Dead slots ignore actions.
            4       +1 charge to every live prey
  charge    per slot, clipped to [0, CHARGE_MAX]; episode fitness = sum of final slot charges.
  trace     sha256 per tick over "t|" + live (id,cell) ascending + "|" + live-slot "id:action" + "|" + slot charges.

Forms: RefB2 (plain Python, the authority), GbB2 (python-graphblas relations: COLOC = AT.AT^T, neighbour relations
AT.MOVE_d.AT^T, AT row replacement), CyB2 (FalkorDB Cypher on the private substrate). Charge is a per-form Python
ledger; WHO is credited, who dies and where everyone is come from each form's own relational computation.
cheat="skip_mutation": the prey's action is read but its AT mutation is not applied (the prey stays).
"""
from __future__ import annotations

import hashlib
import os
import uuid

import numpy as np

from .graphworld import Spec, _line, step_cell

W_OBS = 8
A = 8
CHARGE_MAX = 65535
FOOD_CREDIT = 8
SAME = 4
CHEATS = ("", "skip_mutation")
PLANTED = dict(L=8, n_pred=1, n_prey=4, n_food=24, ticks=64)      # O3's planted world: dense food, one predator


def action_dir(a: int) -> int | None:
    a = int(a) % A
    return None if a == 0 else (a - 1) % 4


def planted(seed: int) -> Spec:
    return Spec(seed=int(seed), **PLANTED)


class _Base:
    def __init__(self, s: Spec, cheat: str = ""):
        if not 2 <= s.L <= 255:
            raise ValueError(f"L={s.L}: need 2 <= L <= 255 (uint16 cell ids, distinct neighbours)")
        if cheat not in CHEATS:
            raise ValueError(f"unknown cheat {cheat!r}")
        self.s, self.cheat, self.t = s, cheat, 0
        self.slots = list(range(s.n_pred, s.n_pred + s.n_prey))
        self.charge = {q: 0 for q in self.slots}
        self.moving_actions = 0                       # moving actions received by live prey (cheat detectability)
        self.h = hashlib.sha256()

    def _credit(self, q: int, v: int) -> None:
        self.charge[q] = min(CHARGE_MAX, self.charge[q] + v)

    def _live_acts(self, actions, live) -> list[tuple[int, int]]:
        a = np.asarray(actions, dtype=np.int64).reshape(-1)
        if len(a) != len(self.slots):
            raise ValueError(f"{len(a)} actions for {len(self.slots)} slots")
        acts = [(q, int(a[j]) % A) for j, q in enumerate(self.slots) if q in live]
        self.moving_actions += sum(1 for _, x in acts if x != 0)
        return acts

    def _prey_dirs(self, acts) -> dict[int, int]:
        if self.cheat == "skip_mutation":
            return {}
        return {q: d for q, x in acts if (d := action_dir(x)) is not None}

    def _pred_dirs(self, live) -> dict[int, int]:
        return {i: (i * 7 + self.t * 3) % 4 for i in live if self.s.kind(i) == 0}

    def _obs(self, cells: dict, masks: dict, nfood: int) -> np.ndarray:
        o = np.zeros((len(self.slots), W_OBS), np.uint16)
        for j, q in enumerate(self.slots):
            o[j, 5], o[j, 6], o[j, 7] = self.t, nfood, self.charge[q]
            if q in cells:
                m = masks.get(q, (0, 0, 0))
                o[j, 0], o[j, 1], o[j, 2], o[j, 3], o[j, 4] = 1, cells[q], m[0], m[2], m[1]
        return o

    def _end_tick(self, cells: dict, acts) -> None:
        for q in self.slots:
            if q in cells:
                self._credit(q, 1)
        self.h.update(_line(self.t, cells) + b"|" + ",".join(f"{q}:{x}" for q, x in acts).encode("ascii")
                      + b"|" + ",".join(str(self.charge[q]) for q in self.slots).encode("ascii"))
        self.t += 1

    def digest(self) -> str:
        return self.h.hexdigest()

    def total(self) -> int:
        return int(sum(self.charge.values()))

    def close(self) -> None:
        pass


# ------------------------------------------------------------------ reference
class RefB2(_Base):
    def __init__(self, s: Spec, cheat: str = "", init: dict | None = None):
        super().__init__(s, cheat)
        self.cell = dict(init) if init is not None else {i: s.init_cell(i) for i in range(s.n)}

    def phase12(self) -> None:
        s, cell = self.s, self.cell
        prey = sorted(i for i in cell if s.kind(i) == 1)
        at: dict[int, list[int]] = {}
        for q in prey:
            at.setdefault(cell[q], []).append(q)
        for f in sorted(i for i in cell if s.kind(i) == 2):           # 1 EAT
            if cell[f] in at:
                self._credit(min(at[cell[f]]), FOOD_CREDIT)
                del cell[f]
        pc = {cell[p] for p in cell if s.kind(p) == 0}
        for q in prey:                                                 # 2 PREY
            if cell[q] in pc:
                del cell[q]

    def observe(self) -> np.ndarray:
        s, cell, L = self.s, self.cell, self.s.L
        occ: dict[int, list[int]] = {}
        for i, c in cell.items():
            occ.setdefault(c, []).append(i)
        masks = {}
        for q in self.slots:
            if q not in cell:
                continue
            m = [0, 0, 0]
            for bit, cc in [(SAME, cell[q])] + [(d, step_cell(L, cell[q], d)) for d in range(4)]:
                for i in occ.get(cc, ()):
                    if i != q:
                        m[s.kind(i)] |= 1 << bit
            masks[q] = m
        return self._obs(cell, masks, sum(1 for i in cell if s.kind(i) == 2))

    def phase34(self, actions) -> None:
        cell, L = self.cell, self.s.L
        acts = self._live_acts(actions, cell)
        dirs = self._pred_dirs(cell) | self._prey_dirs(acts)
        for i, d in dirs.items():                                      # 3 MOVE (simultaneous; no interaction)
            cell[i] = step_cell(L, cell[i], d)
        self._end_tick(cell, acts)


# ------------------------------------------------------------------ graphblas
class GbB2(_Base):
    def __init__(self, s: Spec, cheat: str = ""):
        super().__init__(s, cheat)
        from graphblas import Matrix
        n, C, L = s.n, s.cells, s.L
        self.move = [Matrix.from_coo(np.arange(C), np.array([step_cell(L, c, d) for c in range(C)]), True,
                                     nrows=C, ncols=C, dtype=bool) for d in range(4)]
        self.kind = np.array([s.kind(i) for i in range(n)])
        self.AT = Matrix.from_coo(np.arange(n), np.array([s.init_cell(i) for i in range(n)]), True,
                                  nrows=n, ncols=C, dtype=bool)

    def _live(self) -> dict:
        r, c, _ = self.AT.to_coo()
        return dict(zip(r.tolist(), c.tolist()))

    def _diag(self, ids):
        from graphblas import Matrix
        n = self.s.n
        ids = np.array(sorted(ids), dtype=np.int64)
        if len(ids) == 0:
            return Matrix(bool, n, n)
        return Matrix.from_coo(ids, ids, True, nrows=n, ncols=n, dtype=bool)

    def _coloc(self):
        from graphblas import semiring
        return self.AT.mxm(self.AT.T, semiring.lor_land).new()

    def _pairs(self, rows_ids, M, cols_ids) -> list[tuple[int, int]]:
        from graphblas import semiring
        R = self._diag(rows_ids).mxm(M, semiring.lor_land).new().mxm(self._diag(cols_ids), semiring.lor_land).new()
        r, c, _ = R.to_coo()
        return list(zip(r.tolist(), c.tolist()))

    def _keep(self, drop) -> None:
        from graphblas import semiring
        if drop:
            self.AT = self._diag(set(range(self.s.n)) - set(drop)).mxm(self.AT, semiring.lor_land).new()

    def phase12(self) -> None:
        live = self._live()
        kind_ids = lambda k, lv: [i for i in lv if self.kind[i] == k]
        first: dict[int, int] = {}
        for f, q in self._pairs(kind_ids(2, live), self._coloc(), kind_ids(1, live)):   # OWNS: food x prey
            first[f] = min(q, first.get(f, q))
        for f in sorted(first):
            self._credit(first[f], FOOD_CREDIT)
        self._keep(list(first))
        live = self._live()
        eaten = {q for q, _ in self._pairs(kind_ids(1, live), self._coloc(), kind_ids(0, live))}
        self._keep(sorted(eaten))

    def observe(self) -> np.ndarray:
        from graphblas import semiring
        live = self._live()
        slots = [q for q in self.slots if q in live]
        masks = {q: [0, 0, 0] for q in slots}
        rels = [(SAME, self._coloc())] + [(d, self.AT.mxm(self.move[d], semiring.lor_land).new()
                                              .mxm(self.AT.T, semiring.lor_land).new()) for d in range(4)]
        for bit, M in rels:
            for q, o in self._pairs(slots, M, list(live)):
                if o != q:
                    masks[q][int(self.kind[o])] |= 1 << bit
        return self._obs(live, masks, sum(1 for i in live if self.kind[i] == 2))

    def phase34(self, actions) -> None:
        from graphblas import Matrix, binary, semiring
        live = self._live()
        acts = self._live_acts(actions, live)
        dirs = self._pred_dirs(live) | self._prey_dirs(acts)
        n, C = self.s.n, self.s.cells
        new = Matrix(bool, n, C)
        stay = [i for i in live if i not in dirs]
        if stay:
            new = new.ewise_add(self._diag(stay).mxm(self.AT, semiring.lor_land).new(), binary.lor).new()
        for d in range(4):
            ids = [i for i, dd in dirs.items() if dd == d]
            if ids:
                moved = self._diag(ids).mxm(self.AT, semiring.lor_land).new().mxm(self.move[d], semiring.lor_land).new()
                new = new.ewise_add(moved, binary.lor).new()
        self.AT = new
        self._end_tick(self._live(), acts)


# ------------------------------------------------------------------ cypher
CY_HOST, CY_PORT = "127.0.0.1", int(os.environ.get("PM_B2_CYPHER_PORT", os.environ.get("PM_B_PORT", "6391")))
CY_EAT = "MATCH (f:Ent {k: 2})-[:AT]->(:Cell)<-[:AT]-(q:Ent {k: 1}) RETURN f.i, min(q.i)"
CY_PREY = ("MATCH (q:Ent {k: 1})-[:AT]->(:Cell)<-[:AT]-(:Ent {k: 0}) "
           "WITH DISTINCT q DETACH DELETE q")
CY_SAME = ("MATCH (q:Ent {k: 1})-[:AT]->(:Cell)<-[:AT]-(o:Ent) WHERE o.i <> q.i "
           "RETURN DISTINCT q.i, o.k")
CY_NEAR = ("MATCH (q:Ent {k: 1})-[:AT]->(:Cell)-[m:MOVE]->(:Cell)<-[:AT]-(o:Ent) WHERE o.i <> q.i "
           "RETURN DISTINCT q.i, m.d, o.k")
CY_MOVE = ("UNWIND $moves AS mv "
           "MATCH (e:Ent {i: mv[0]})-[r:AT]->(:Cell)-[:MOVE {d: mv[1]}]->(n:Cell) "
           "DELETE r CREATE (e)-[:AT]->(n)")
CY_READ = "MATCH (e:Ent)-[:AT]->(c:Cell) RETURN e.i, c.c"


class CyB2(_Base):
    def __init__(self, s: Spec, cheat: str = "", graph: str | None = None):
        super().__init__(s, cheat)
        from falkordb import FalkorDB
        self.db = FalkorDB(host=CY_HOST, port=CY_PORT)
        self.name = graph or f"e_b2_{os.getpid()}_{uuid.uuid4().hex[:8]}"
        self.g = self.db.select_graph(self.name)
        try:
            self.g.delete()
        except Exception:
            pass
        C, L = s.cells, s.L
        self.q("UNWIND range(0, $C - 1) AS c CREATE (:Cell {c: c})", {"C": C})
        self.q("CREATE INDEX FOR (c:Cell) ON (c.c)")
        self.q("CREATE INDEX FOR (e:Ent) ON (e.i)")
        self.q("UNWIND $E AS e MATCH (a:Cell {c: e[0]}), (b:Cell {c: e[1]}) CREATE (a)-[:MOVE {d: e[2]}]->(b)",
               {"E": [[c, step_cell(L, c, d), d] for c in range(C) for d in range(4)]})
        self.q("UNWIND $X AS x MATCH (c:Cell {c: x[2]}) CREATE (:Ent {i: x[0], k: x[1]})-[:AT]->(c)",
               {"X": [[i, s.kind(i), s.init_cell(i)] for i in range(s.n)]})

    def q(self, text: str, params: dict | None = None) -> list:
        return self.g.query(text, params or {}).result_set

    def _live(self) -> dict:
        return {int(i): int(c) for i, c in self.q(CY_READ)}

    def phase12(self) -> None:
        rows = sorted((int(f), int(q)) for f, q in self.q(CY_EAT))
        for _, q in rows:
            self._credit(q, FOOD_CREDIT)
        if rows:
            self.q("UNWIND $ids AS x MATCH (f:Ent {i: x}) DETACH DELETE f", {"ids": [f for f, _ in rows]})
        self.q(CY_PREY)

    def observe(self) -> np.ndarray:
        live = self._live()
        masks = {q: [0, 0, 0] for q in self.slots if q in live}
        for q, k in self.q(CY_SAME):
            masks[int(q)][int(k)] |= 1 << SAME
        for q, d, k in self.q(CY_NEAR):
            masks[int(q)][int(k)] |= 1 << int(d)
        return self._obs(live, masks, sum(1 for i in live if self.s.kind(i) == 2))

    def phase34(self, actions) -> None:
        live = self._live()
        acts = self._live_acts(actions, live)
        dirs = self._pred_dirs(live) | self._prey_dirs(acts)
        if dirs:
            self.q(CY_MOVE, {"moves": [[i, d] for i, d in sorted(dirs.items())]})
        self._end_tick(self._live(), acts)

    def close(self) -> None:
        try:
            self.g.delete()
        except Exception:
            pass


FORMS = {"ref": RefB2, "gb": GbB2, "cy": CyB2}


# ------------------------------------------------------------------ episodes, policies, rollout
def episode(form: str, s: Spec, policy, cheat: str = "") -> dict:
    """policy(obs [S, W_OBS] uint16, t) -> actions [S]. -> {hash, charge, charges, moving_actions}."""
    w = FORMS[form](s, cheat)
    try:
        for t in range(s.ticks):
            w.phase12()
            w.phase34(policy(w.observe(), t))
        return {"hash": w.digest(), "charge": w.total(), "charges": [w.charge[q] for q in w.slots],
                "moving_actions": w.moving_actions}
    finally:
        w.close()


def table_policy(table: np.ndarray):
    """A fixed action stream [ticks, S] (identical across forms: it never reads the observation)."""
    return lambda o, t: table[t]


def random_table(s: Spec, seed) -> np.ndarray:
    return np.random.Generator(np.random.PCG64(seed)).integers(0, A, size=(s.ticks, s.n_prey))


def abstain(o, t):
    return np.zeros(len(o), np.int64)


def constant(a: int):
    return lambda o, t: np.full(len(o), int(a), np.int64)


def forager(o, t):
    """Planted obs-reading policy (predicate O3): step onto neighbouring food (lowest direction bit), else step away
    from a neighbouring predator (opposite of its lowest direction bit), else action 1. Dead slots abstain."""
    a = np.ones(len(o), np.int64)
    for j, row in enumerate(o):
        if not row[0]:
            a[j] = 0
            continue
        food, pred = int(row[3]), int(row[2])
        fd = [d for d in range(4) if food >> d & 1]
        pd = [d for d in range(4) if pred >> d & 1]
        if fd:
            a[j] = fd[0] + 1
        elif pd:
            a[j] = (pd[0] + 2) % 4 + 1
    return a


def rollout(spec_of_seed, policy, seeds, form: str = "ref") -> np.ndarray:
    """Per-seed episode fitness (sum of final clipped slot charges) for G's screen: policy as in `episode`."""
    return np.array([episode(form, spec_of_seed(int(sd)), policy)["charge"] for sd in seeds], dtype=np.int64)
