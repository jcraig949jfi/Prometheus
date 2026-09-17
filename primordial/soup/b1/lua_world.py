"""Form (d): driver for encounter.lua on a private substrate (default port 6391).

State lives in five packed string keys; one EVALSHA advances every env by k ticks.
k=1 is 'one EVALSHA per tick'; k=horizon runs the whole episode server-side.
"""
from __future__ import annotations

import os
import pathlib

import numpy as np
import redis

from .common import hash_log, init_regs, stream_state

URL = os.environ.get("PM_B_SUBSTRATE", "redis://127.0.0.1:6391/0")
_SRC = (pathlib.Path(__file__).with_name("encounter.lua")).read_text(encoding="ascii")


class LuaEncounter:
    def __init__(self, mech, world_id: str, cheat: str = "", r: redis.Redis | None = None, ns: str = "b1"):
        self.m, self.world_id, self.cheat = mech, world_id, cheat
        self.r = r or redis.Redis.from_url(URL)
        self.sha = self.r.script_load(_SRC)
        self.keys = [f"{ns}:{k}" for k in ("regs", "charge", "alive", "pend", "stoch")]

    def prepare(self, seeds: np.ndarray):
        m, n = self.m, len(seeds)
        self.n_envs = n
        regs = init_regs(m, self.world_id, seeds).astype("<u2")
        charge = (np.full((n, m.n_slots), m.start_charge, dtype=np.int64) + (1 << 31)).astype("<u4")
        alive = np.ones((n, m.n_slots), dtype=np.uint8)
        pend = np.zeros((n, m.delay + 1, m.n_regs), dtype="<u2")
        st = np.array([stream_state("stoch", self.world_id, int(s)) for s in seeds], dtype=np.uint64)
        stoch = np.stack([(st & np.uint64(0xFFFFFFFF)).astype("<u4"), (st >> np.uint64(32)).astype("<u4")], 1)
        p = self.r.pipeline(transaction=False)
        for key, arr in zip(self.keys, (regs, charge, alive, pend, stoch)):
            p.set(key, np.ascontiguousarray(arr).tobytes())
        p.execute()
        m = self.m
        self.argv_head = [n, m.n_regs, m.n_slots, m.act_width]
        self.argv_mid = [m.delay, m.regime_period, m.stoch_rate, m.act_cost, m.step_cost,
                         m.yield_reg, m.yield_lo, m.yield_hi, m.yield_amt,
                         1 if self.cheat == "skip_lin" else 0]
        self.lin_csv = ",".join(str(int(v)) for op in m.lin_ops for v in op)
        self.tgt_csv = ",".join(str(int(v)) for v in m.act_targets)

    def run(self, acts: np.ndarray, k: int, record: bool = False, ticks: int | None = None):
        """acts [T,n,S,W]; advance `ticks` (default horizon) in calls of k ticks."""
        T = ticks or self.m.horizon
        a8 = acts.astype(np.uint8)
        logs = []
        t = 0
        while t < T:
            kk = min(k, T - t)
            out = self.r.evalsha(self.sha, len(self.keys), *self.keys,
                                 *self.argv_head, t, kk, *self.argv_mid, 1 if record else 0,
                                 self.lin_csv, self.tgt_csv, a8[t:t + kk].tobytes())
            if record:
                logs.append(np.asarray(out, dtype=np.int64))
            t += kk
        return logs

    def trace_hashes(self, logs) -> list[bytes]:
        m, n = self.m, self.n_envs
        R, S = m.n_regs, m.n_slots
        width = R + 2 * S
        per_call = []
        for chunk in logs:                       # each chunk: env-outer, tick-inner
            per_call.append(chunk.reshape(n, -1, width))
        full = np.concatenate(per_call, axis=1)  # [n, T, width]
        out = []
        for e in range(n):
            regs, charge, alive = full[e, :, :R], full[e, :, R:R + S], full[e, :, R + S:] == 1
            dead = np.nonzero(~alive.any(1))[0]
            T = int(dead[0]) + 1 if len(dead) else m.horizon
            out.append(hash_log(regs, charge, alive, T).encode())
        return out
