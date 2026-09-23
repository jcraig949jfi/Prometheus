"""Form (e): Encounter semantics as FalkorDB Cypher, one GRAPH.QUERY per tick.

One node per env: (:E {i, r0.., c0.., a0.. (alive 0/1), p<d>_<r> pending adds mod M}).
Every mechanic runs inside the query as SET clauses separated by WITH, in wforge order.

DISCLOSED DIFFERENCE: Cypher has no 64-bit xor/shift, so the stochastic-kick schedule
(a pure function of the episode seed, independent of world state) is computed client
side with the same xorshift64* stream and passed as a per-tick parameter. The client
work is inside the timed region.
"""
from __future__ import annotations

import os

import numpy as np
from falkordb import FalkorDB

from .common import M, hash_log, init_regs, stream_state
from .np_world import xs_next

HOST, PORT = "127.0.0.1", int(os.environ.get("PM_B_PORT", "6391"))


class FalkorEncounter:
    def __init__(self, mech, world_id: str, cheat: str = "", graph: str = "b1g"):
        self.m, self.world_id, self.cheat = mech, world_id, cheat
        self.db = FalkorDB(host=HOST, port=PORT)
        self.gname = graph
        self._qcache: dict = {}

    def prepare(self, seeds: np.ndarray):
        m, n = self.m, len(seeds)
        self.n_envs = n
        try:
            self.db.select_graph(self.gname).delete()
        except Exception:
            pass
        self.g = self.db.select_graph(self.gname)
        regs = init_regs(m, self.world_id, seeds)
        R, S, D1 = m.n_regs, m.n_slots, m.delay + 1
        props = [f"r{r}" for r in range(R)] + [f"c{s}" for s in range(S)] + [f"a{s}" for s in range(S)] \
            + [f"p{d}_{r}" for d in range(D1) for r in range(R)]
        rows = [[e] + regs[e].tolist() + [m.start_charge] * S + [1] * S + [0] * (D1 * R) for e in range(n)]
        body = ", ".join(f"{p}: row[{j + 1}]" for j, p in enumerate(props))
        for c in range(0, n, 4096):
            self.g.query(f"UNWIND $rows AS row CREATE (:E {{i: row[0], {body}}})", {"rows": rows[c:c + 4096]})
        self.st = np.array([stream_state("stoch", self.world_id, int(s)) for s in seeds], dtype=np.uint64)
        self.tick = 0

    def _kicks(self):
        """[[idx, val] per env] or None when no env kicks this tick (same draws as wforge)."""
        m = self.m
        if not m.stoch_rate:
            return None
        st, out = xs_next(self.st)
        hit = (out % np.uint64(m.stoch_rate)) == 0
        if not hit.any():
            self.st = st
            return None
        st2, o2 = xs_next(st)
        st3, o3 = xs_next(st2)
        self.st = np.where(hit, st3, st)
        val = (o2 % np.uint64(M)).astype(np.int64)
        idx = np.where(hit, (o3 % np.uint64(m.n_regs)).astype(np.int64), -1)
        return np.stack([idx, val], 1).tolist()

    def _query(self, t: int, kick: bool, record: bool) -> str:
        m = self.m
        D1 = m.delay + 1
        ws, ls = (t + m.delay) % D1, t % D1
        flip = bool(m.regime_period) and (t // m.regime_period) % 2 == 1
        key = (ws, ls, flip, kick, record)
        if key in self._qcache:
            return self._qcache[key]
        R, S, W = m.n_regs, m.n_slots, m.act_width
        q = ["MATCH (e:E) WITH e, $A[e.i] AS a"]
        if kick:
            q[-1] += ", $K[e.i] AS k"
        carry = "e, a" + (", k" if kick else "")
        # phase 1: intake (alive read BEFORE any change; pending writes land regardless of affordability)
        sets = []
        for s in range(S):
            mag = " + ".join(f"(a[{s * W + i}] % 8)" for i in range(W))
            sets.append(f"e.c{s} = CASE WHEN e.a{s} = 1 AND ({mag}) * {m.act_cost} <= e.c{s} "
                        f"THEN e.c{s} - ({mag}) * {m.act_cost} ELSE e.c{s} END")
        for tg in sorted(set(m.act_targets)):
            terms = [f"(a[{s * W + i}] % 8) * 251 * e.a{s}" for s in range(S) for i in range(W)
                     if m.act_targets[i] == tg]
            sets.append(f"e.p{ws}_{tg} = (e.p{ws}_{tg} + {' + '.join(terms)}) % {M}")
        q.append("SET " + ", ".join(sets))
        # phase 2: landing, then clear the landed ring slot
        q.append(f"WITH {carry} SET " + ", ".join(f"e.r{r} = (e.r{r} + e.p{ls}_{r}) % {M}" for r in range(R)))
        q.append(f"WITH {carry} SET " + ", ".join(f"e.p{ls}_{r} = 0" for r in range(R)))
        if self.cheat != "skip_lin":
            for dst, a, s1, b, s2, c in m.lin_ops:
                aa = (M - a) % M if flip else a
                q.append(f"WITH {carry} SET e.r{dst} = ({aa} * e.r{s1} + {b} * e.r{s2} + {c}) % {M}")
        if kick:
            q.append(f"WITH {carry} SET " + ", ".join(
                f"e.r{r} = CASE WHEN k[0] = {r} THEN k[1] ELSE e.r{r} END" for r in range(R)))
        # phase 3: economy
        v = f"e.r{m.yield_reg}"
        if m.yield_lo < m.yield_hi:
            inw = f"({v} >= {m.yield_lo} AND {v} < {m.yield_hi})"
        else:
            inw = f"({v} >= {m.yield_lo} OR {v} < {m.yield_hi})"
        nl = " + ".join(f"e.a{s}" for s in range(S))
        # FalkorDB evaluates the division even when the CASE guard is false: guard the divisor itself
        q.append(f"WITH e, CASE WHEN {inw} THEN {m.yield_amt} / (CASE WHEN ({nl}) > 0 THEN ({nl}) ELSE 1 END) "
                 f"ELSE 0 END AS share")
        q.append("SET " + ", ".join(f"e.c{s} = CASE WHEN e.a{s} = 1 THEN e.c{s} - {m.step_cost} + share "
                                    f"ELSE e.c{s} END" for s in range(S)))
        q.append("WITH e SET " + ", ".join(f"e.a{s} = CASE WHEN e.a{s} = 1 AND e.c{s} <= 0 THEN 0 "
                                           f"ELSE e.a{s} END" for s in range(S)))
        if record:
            cols = [f"e.r{r}" for r in range(R)] + [f"e.c{s}" for s in range(S)] + [f"e.a{s}" for s in range(S)]
            q.append("WITH e RETURN e.i, " + ", ".join(cols) + " ORDER BY e.i")
        else:
            q.append("WITH e RETURN count(e)")
        text = " ".join(q)
        self._qcache[key] = text
        return text

    def run(self, acts: np.ndarray, record: bool = False, ticks: int | None = None):
        m = self.m
        T = ticks or m.horizon
        n, S, W = self.n_envs, m.n_slots, m.act_width
        logs = []
        for _ in range(T):
            t = self.tick
            kicks = self._kicks()
            params = {"A": acts[t].reshape(n, S * W).tolist()}
            if kicks is not None:
                params["K"] = kicks
            res = self.g.query(self._query(t, kicks is not None, record), params)
            if record:
                logs.append(np.asarray(res.result_set, dtype=np.int64)[:, 1:])
            self.tick = t + 1
        return logs

    def trace_hashes(self, logs) -> list[bytes]:
        m = self.m
        R, S = m.n_regs, m.n_slots
        full = np.stack(logs, 0)                      # [T, n, R+2S]
        out = []
        for e in range(self.n_envs):
            regs, charge, alive = full[:, e, :R], full[:, e, R:R + S], full[:, e, R + S:] == 1
            dead = np.nonzero(~alive.any(1))[0]
            T = int(dead[0]) + 1 if len(dead) else m.horizon
            out.append(hash_log(regs, charge, alive, T).encode())
        return out
