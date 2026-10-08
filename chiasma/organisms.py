"""E1 organisms: one positive geometry, four ways of holding failure and revision.

Shared positive geometry P (every arm):
  - Per target, a set of cells. A cell is a simplex over primitive vertices (a
    conjunction); the target is predicted true when any cell's premise is a face of
    the object (premise subset of x).
  - Weld (generalize): on a false negative, the new positive is welded into an
    unconsolidated cell as the intersection of their vertex sets (the cells' shared
    face), if the arm's weld test allows it; otherwise it becomes a new cell.
  - Retract: a cell that fires on a negative is deleted, unless the arm can repair it.
  - Consolidate (compress): after S_CONS supporting positives a cell drops each literal
    implied by another literal of the cell in every object seen so far (implication
    table Imp, part of P), and discards its anchor. This is where a cheap false
    abstraction comes from: while the world forces c -> f, f is pruned.

Arms (one mechanism changes per step O1 -> O2 -> O3 -> O4):
  O1  neg=none   positive-only: welds freely (no failure memory to check against)
  O2  neg=raw    stores raw failures (object, target), FIFO under the byte cap
  O3  neg=proj   compressed shadow boundary: failures projected onto the target's own
                 vertex support (N_eps), kept only if maximal (a stored negative n
                 refutes every conjunction that is a subset of n)
  O4  O3 + U     provenance (pruned literal, justifying literal) per consolidated cell,
                 and revision seams: when a justification breaks in Imp, every cell
                 that relied on it gets the literal back and is marked disputed;
                 evidence then confirms or reverses each one separately
Controls:
  O0    O3 without consolidation (keeps anchors, never prunes): the cheapest
        counter-organism, immune to the false foundation by construction
  O3R   O3 whose stored negatives are random masks of the same size (counterfeit shadow)
  O4R   O4 whose justifications name a random literal (counterfeit seams)
  O4L   ABLATION added after development run 1: O4 without eager seams. Keeps the
        provenance and repairs a cell from it when the cell itself fails, but does
        not restore literals when a justification breaks in Imp
  CEIL  raw failures, no consolidation, no byte cap (unbounded-capacity ceiling)
  EMB   static embedding: stores whole labelled examples, predicts by 5-nearest
        neighbours in Hamming distance, same byte cap (replay masquerading as memory)

Byte ruler (canonical, see nbytes): 1 byte per vertex id, 1 length byte per stored
set, 2 bytes per support counter, 1 byte per target id; Imp is m*ceil(m/8) bytes.
Op ruler: one unit per subset test, intersection, or stored item scanned.
"""
import random
from typing import Dict, List, Optional

from .world import popcount, bits

S_CONS = 6


class Cell:
    __slots__ = ("premise", "anchor", "support", "consolidated", "prov", "disputed", "born")

    def __init__(self, x: int, born: int):
        self.premise = x
        self.anchor: Optional[int] = x
        self.support = 1
        self.consolidated = False
        self.prov: List = []        # [(pruned_literal_bit, justifier_bit)] (O4 only)
        self.disputed = 0           # mask of literals restored by an open seam (O4 only)
        self.born = born


class Organism:
    ARMS = {
        "O1": dict(neg="none", consolidate=True, seams="none"),
        "O2": dict(neg="raw", consolidate=True, seams="none"),
        "O3": dict(neg="proj", consolidate=True, seams="none"),
        "O4": dict(neg="proj", consolidate=True, seams="true"),
        "O0": dict(neg="proj", consolidate=False, seams="none"),
        "O3R": dict(neg="proj_rand", consolidate=True, seams="none"),
        "O4R": dict(neg="proj", consolidate=True, seams="rand"),
        "O4L": dict(neg="proj", consolidate=True, seams="lazy"),
        "CEIL": dict(neg="raw", consolidate=False, seams="none", uncapped=True),
    }

    def __init__(self, arm: str, m: int, cap: Optional[int], seed: int = 0):
        cfg = self.ARMS[arm]
        self.arm, self.m = arm, m
        self.neg, self.do_cons, self.seams = cfg["neg"], cfg["consolidate"], cfg["seams"]
        self.cap = None if cfg.get("uncapped") else cap
        self.rng = random.Random("{}:{}".format(arm, seed))
        self.cells: Dict[str, List[Cell]] = {}
        self.tid: Dict[str, int] = {}
        self.imp = [(1 << m) - 1] * m          # imp[u]: literals present whenever u was
        self.seen = [False] * m
        self.raw: List = []                    # O2/CEIL: [(tid, x)]
        self.proj: Dict[str, List[int]] = {}   # O3/O4/O0: per target, maximal negatives
        self.proj_order: List = []             # eviction order: (name, mask)
        self.ops = 0
        self.t = 0
        self.events = {"fn": 0, "fp": 0, "weld": 0, "weld_refused": 0, "new_cell": 0,
                       "retract": 0, "repair": 0, "consolidate": 0, "seam_open": 0,
                       "seam_confirm": 0, "seam_reverse": 0, "neg_seen": 0,
                       "neg_stored": 0, "evicted": 0, "over_budget": 0}

    # ---- queries -------------------------------------------------------------
    def predict(self, x: int, name: str) -> int:
        for c in self.cells.get(name, ()):
            self.ops += 1
            if c.premise & x == c.premise:
                return 1
        return 0

    # ---- learning ------------------------------------------------------------
    def observe(self, x: int, labels: Dict[str, int]) -> None:
        self.t += 1
        self._update_imp(x)
        for name in sorted(labels):
            if name not in self.tid:
                self.tid[name] = len(self.tid)
                self.cells[name] = []
            self._learn(name, x, labels[name])
        self._enforce_cap()

    def _update_imp(self, x: int) -> None:
        for u in bits(x):
            self.ops += 1
            if not self.seen[u]:
                self.seen[u] = True
                self.imp[u] = x                  # first sighting sets, never breaks
                continue
            new = self.imp[u] & x
            broken = self.imp[u] & ~new
            self.imp[u] = new
            if broken and self.seams in ("true", "rand"):
                self._open_seams(1 << u, broken)

    def _learn(self, name: str, x: int, y: int) -> None:
        cells = self.cells[name]
        fired = []
        for c in cells:
            self.ops += 1
            if c.premise & x == c.premise:
                fired.append(c)
        if y:
            if fired:
                for c in fired:
                    c.support += 1
                    self._maybe_consolidate(c)
            else:
                self.events["fn"] += 1
                self._on_fn(name, x)
        else:
            self.events["neg_seen"] += 1
            if self.seams != "none":
                self._confirm_seams(name, x)
            self._store_negative(name, x)
            if fired:
                self.events["fp"] += 1
                self._on_fp(name, x, fired)

    def _on_fn(self, name: str, x: int) -> None:
        cells = self.cells[name]
        if self.seams != "none":
            for c in cells:
                if c.disputed:
                    self.ops += 1
                    base = c.premise & ~c.disputed
                    if base & x == base:      # fires without the restored literal: reverse
                        c.premise = base
                        c.disputed = 0
                        c.support += 1
                        self.events["seam_reverse"] += 1
                        return
        for c in sorted(cells, key=lambda c: (-c.support, c.born)):
            if c.consolidated:
                continue
            self.ops += 1
            inter = c.anchor & x
            if inter and self._weld_ok(name, inter):
                c.anchor = c.premise = inter
                c.support += 1
                self.events["weld"] += 1
                self._maybe_consolidate(c)
                return
            self.events["weld_refused"] += 1
        cells.append(Cell(x, self.t))
        self.events["new_cell"] += 1

    def _weld_ok(self, name: str, inter: int) -> bool:
        if self.neg == "none":
            return True
        if self.neg == "raw":
            tid = self.tid[name]
            for t, n in self.raw:
                self.ops += 1
                if t == tid and inter & n == inter:
                    return False
            return True
        for n in self.proj.get(name, ()):
            self.ops += 1
            if inter & n == inter:
                return False
        return True

    def _on_fp(self, name: str, x: int, fired: List[Cell]) -> None:
        cells = self.cells[name]
        for c in fired:
            if self.seams != "none" and c.consolidated and c.prov:
                restore = 0
                for lit, _j in c.prov:
                    if not (lit & x):
                        restore |= lit
                if restore:
                    c.premise |= restore
                    c.prov = [(l, j) for l, j in c.prov if not (l & restore)]
                    self.events["repair"] += 1
                    continue
            cells.remove(c)
            self.events["retract"] += 1

    def _maybe_consolidate(self, c: Cell) -> None:
        if not self.do_cons or c.consolidated or c.support < S_CONS:
            return
        premise = c.anchor
        prov = []
        for l in bits(c.anchor):
            lb = 1 << l
            for u in bits(premise & ~lb):
                self.ops += 1
                if self.imp[u] & lb:
                    premise &= ~lb
                    j = 1 << u
                    if self.seams == "rand":
                        others = bits(premise)
                        j = 1 << self.rng.choice(others) if others else j
                    prov.append((lb, j))
                    break
        c.premise = premise
        c.anchor = None
        c.consolidated = True
        if self.seams != "none":
            c.prov = prov
        self.events["consolidate"] += 1

    # ---- seams (O4, O4R) ------------------------------------------------------
    def _open_seams(self, u_bit: int, broken: int) -> None:
        for name in sorted(self.cells):
            for c in self.cells[name]:
                if not c.prov:
                    continue
                hit = 0
                for lit, j in c.prov:
                    self.ops += 1
                    if j == u_bit and lit & broken:
                        hit |= lit
                if hit:
                    c.premise |= hit
                    c.disputed |= hit
                    c.prov = [(l, j) for l, j in c.prov if not (l & hit)]
                    self.events["seam_open"] += 1

    def _confirm_seams(self, name: str, x: int) -> None:
        for c in self.cells[name]:
            if c.disputed:
                self.ops += 1
                base = c.premise & ~c.disputed
                if base & x == base and not (c.disputed & x):
                    c.disputed = 0                # the restored literal excluded a negative
                    self.events["seam_confirm"] += 1

    # ---- shadow memory -------------------------------------------------------
    def _store_negative(self, name: str, x: int) -> None:
        if self.neg == "none":
            return
        if self.neg == "raw":
            self.raw.append((self.tid[name], x))
            self.events["neg_stored"] += 1
            return
        support = 0
        for c in self.cells[name]:
            support |= c.premise if c.anchor is None else c.anchor
        n = x & support
        if not n:
            return
        if self.neg == "proj_rand":
            k = popcount(n)
            n = sum(1 << b for b in self.rng.sample(range(self.m), k))
        lst = self.proj.setdefault(name, [])
        for e in lst:
            self.ops += 1
            if n & e == n:
                return                          # subsumed by a stored maximal negative
        keep = [e for e in lst if e & n != e]
        self.ops += len(lst)
        if len(keep) != len(lst):
            dropped = set(lst) - set(keep)
            self.proj_order = [(nm, e) for nm, e in self.proj_order
                               if not (nm == name and e in dropped)]
        keep.append(n)
        self.proj[name] = keep
        self.proj_order.append((name, n))
        self.events["neg_stored"] += 1

    # ---- rulers --------------------------------------------------------------
    def nbytes(self) -> Dict[str, int]:
        P = self.m * ((self.m + 7) // 8)
        U = 0
        for name, cells in self.cells.items():
            P += 1
            for c in cells:
                P += 1 + popcount(c.premise) + 2
                if c.anchor is not None and c.anchor != c.premise:
                    P += 1 + popcount(c.anchor)
                U += 2 * len(c.prov) + (1 + popcount(c.disputed) if c.disputed else 0)
        N = sum(2 + popcount(x) for _t, x in self.raw)
        N += sum(1 + 1 + popcount(n) for lst in self.proj.values() for n in lst)
        return {"P": P, "N": N, "U": U, "total": P + N + U}

    def _enforce_cap(self) -> None:
        if self.cap is None:
            return
        b = self.nbytes()
        total = b["total"]
        if total <= self.cap:
            return
        while total > self.cap and (self.raw or self.proj_order):
            if self.raw:
                _t, x = self.raw.pop(0)
                total -= 2 + popcount(x)
            else:
                name, n = self.proj_order.pop(0)
                lst = self.proj.get(name, [])
                if n in lst:
                    lst.remove(n)
                    total -= 2 + popcount(n)
            self.events["evicted"] += 1
        while total > self.cap:
            victim = None
            for cells in self.cells.values():
                for c in cells:
                    if c.prov and (victim is None or c.born < victim.born):
                        victim = c
            if victim is None:
                break
            total -= 2 * len(victim.prov)
            victim.prov = []
            self.events["evicted"] += 1
        if total > self.cap:
            self.events["over_budget"] += 1

    def summary(self) -> Dict:
        return {"cells": sum(len(v) for v in self.cells.values()),
                "raw_neg": len(self.raw),
                "proj_neg": sum(len(v) for v in self.proj.values()),
                "events": dict(self.events)}


class Embedding:
    """EMB control: a static store of labelled examples, k-NN by Hamming distance."""
    K = 5

    def __init__(self, arm: str, m: int, cap: Optional[int], seed: int = 0):
        self.arm, self.m, self.cap = arm, m, cap
        self.store: List = []      # [(x, labels dict)]
        self._bytes = 0            # running sum of 1 + popcount(x) over the store
        self.names: Dict[str, int] = {}
        self.ops = 0
        self.events = {"evicted": 0, "over_budget": 0}

    def observe(self, x: int, labels: Dict[str, int]) -> None:
        for n in labels:
            self.names.setdefault(n, len(self.names))
        self.store.append((x, dict(labels)))
        self._bytes += 1 + popcount(x)
        lab_bytes = (len(self.names) + 7) // 8
        while self.cap is not None and self._bytes + lab_bytes * len(self.store) > self.cap and len(self.store) > 1:
            ex, _l = self.store.pop(0)
            self._bytes -= 1 + popcount(ex)
            self.events["evicted"] += 1

    def predict(self, x: int, name: str) -> int:
        cand = []
        for ex, lab in self.store:
            if name in lab:
                self.ops += 1
                cand.append((popcount(ex ^ x), lab[name]))
        if not cand:
            return 0
        cand.sort()
        top = cand[:self.K]
        return int(2 * sum(v for _d, v in top) > len(top))

    def nbytes(self) -> Dict[str, int]:
        lab_bytes = (len(self.names) + 7) // 8
        N = sum(1 + popcount(x) + lab_bytes for x, _l in self.store)
        return {"P": 0, "N": N, "U": 0, "total": N}

    def summary(self) -> Dict:
        return {"stored": len(self.store), "events": dict(self.events)}


ARMS = list(Organism.ARMS) + ["EMB"]


def make(arm: str, m: int, cap: Optional[int], seed: int = 0):
    if arm == "EMB":
        return Embedding(arm, m, cap, seed)
    return Organism(arm, m, cap, seed)
