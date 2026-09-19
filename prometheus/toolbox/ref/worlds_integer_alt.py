"""world.integer_alt.v1 (overnight C70): a SECOND implementation of the integer world's semantics, written
differently on purpose (per-tick closure over precomputed op tables, a flat pending queue keyed by landing
tick, explicit phases as methods) so that admission's REFERENCE-AGREEMENT check has something real to compare:
its trace over the probe seeds must equal world.integer.v1's. The registry row says implements="world.integer".
Any divergence -- one constant, one ordering rule -- makes it UNAVAILABLE, never silently different.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List

from prometheus.toolbox.contracts import ActionSpace, EVENT_ID, Event
from prometheus.toolbox.ref.worlds import DEFAULTS, M, XS64, stream


class IntegerWorldAlt:
    kind = "world.integer_alt.v1"
    capabilities = frozenset({"core.world.v1", "ext.events.v1", "ext.snapshot.v1", "ext.legal_actions.v1", "ext.multiplayer.v1",
                              "ext.intervention.world_params.v1", "ext.cost.v1", "ext.replay.bit.v1"})
    replay_class = "BIT"
    ACT_MUL = 97

    def __init__(self, **params):
        unknown = sorted(set(params) - set(DEFAULTS))
        if unknown:
            raise ValueError("world.integer_alt.v1: unknown params %s" % unknown)
        self.p = dict(DEFAULTS, **params); self.n_players = self.p["n_players"]
        s = stream("structure", self.p["world_seed"]); R = self.p["n_regs"]
        # identical draw ORDER to the reference (this is the contract being reproduced), stored as tuples
        self.ops = tuple((s.below(R), s.below(7) + 1, s.below(R), s.below(7) + 1, s.below(R), s.below(M)) for _ in range(self.p["n_ops"]))
        self.targets = tuple(s.below(R) for _ in range(self.p["act_width"]))
        self.yreg = s.below(R); self.ylo = s.below(M); self.yhi = (self.ylo + self.p["yield_width"]) % M
        self.obs_regs = tuple(range(min(self.p["obs_regs"], R)))
        self.st = None; self.ev: List[Event] = []; self.steps = 0

    def manifest(self) -> dict:
        return {"kind": self.kind, "params": self.p, "implements": "world.integer"}

    def reset(self, seed: int) -> None:
        s = stream("init", self.p["world_seed"], seed)
        self.st = {"t": 0, "r": [s.below(M) for _ in range(self.p["n_regs"])], "c": [self.p["start_charge"]] * self.n_players,
                   "a": [True] * self.n_players, "q": {}, "x": stream("stoch", self.p["world_seed"], seed).s}
        self.h = hashlib.sha256(); self.ev = []

    def observe(self, pid: int) -> List[int]:
        return [self.st["r"][i] for i in self.obs_regs] + [min(15, max(0, self.st["c"][pid]) // 8)]

    def legal_actions(self, pid: int) -> ActionSpace:
        return ActionSpace(self.p["act_width"], self.p["act_range"])

    def _intake(self, actions):
        p = self.p; st = self.st; t = st["t"]
        for pid in range(self.n_players):
            if not st["a"][pid]:
                continue
            a = [x % p["act_range"] for x in list(actions.get(pid, []))[:p["act_width"]]] + [0] * p["act_width"]
            a = a[:p["act_width"]]
            mag = sum(a); cost = mag * p["act_cost"]
            if cost > st["c"][pid]:
                mag = cost = 0
            if cost:
                st["c"][pid] -= cost; self.ev.append((t, EVENT_ID["RESOURCE_CHANGE"], pid, 0, -cost))
            self.ev.append((t, EVENT_ID["ACTION"], pid, 0, mag))
            if mag:
                for i, x in enumerate(a):
                    if x:
                        st["q"].setdefault(t + p["action_delay"], []).append((pid, self.targets[i], x * self.ACT_MUL))

    def _transition(self):
        p = self.p; st = self.st; t = st["t"]
        for pid, tgt, amt in sorted(st["q"].pop(t, []), key=lambda q: (q[0], q[1])):
            st["r"][tgt] = (st["r"][tgt] + amt) % M; self.ev.append((t, EVENT_ID["STATE_WRITE"], pid, tgt, amt))
        if p["_cheat_skip_dynamics"]:
            return
        flip = bool(p["regime_period"]) and (t // p["regime_period"]) % 2 == 1
        r = st["r"]
        for dst, a, s1, b, s2, c in self.ops:
            r[dst] = (((M - a) % M if flip else a) * r[s1] + b * r[s2] + c) % M
        if p["stoch_rate"]:
            xs = XS64(st["x"])
            if xs.below(p["stoch_rate"]) == 0:
                r[xs.below(p["n_regs"])] = xs.below(M)
            st["x"] = xs.s

    def _economy(self):
        p = self.p; st = self.st; t = st["t"]; v = st["r"][self.yreg]
        win = (self.ylo <= v < self.yhi) if self.ylo < self.yhi else (v >= self.ylo or v < self.yhi)
        winners = [i for i in range(self.n_players) if st["a"][i]] if win else []
        for pid in range(self.n_players):
            if not st["a"][pid]:
                continue
            st["c"][pid] -= p["step_cost"]
            if pid in winners:
                g = p["yield_amt"] // len(winners); st["c"][pid] += g; self.ev.append((t, EVENT_ID["YIELD"], pid, self.yreg, g))
                if len(winners) > 1:
                    self.ev.append((t, EVENT_ID["CONTACT"], pid, len(winners), g))
            if st["c"][pid] <= 0:
                st["a"][pid] = False; self.ev.append((t, EVENT_ID["ABSORBED"], pid, 0, st["c"][pid]))

    def step(self, actions: Dict[int, List[int]]) -> bool:
        self._intake(actions); self._transition(); self._economy()
        st = self.st
        self.h.update(json.dumps([st["t"], st["r"], st["c"], st["a"]]).encode())
        st["t"] += 1; self.steps += 1
        return st["t"] >= self.p["horizon"] or not any(st["a"])

    def trace_hash(self) -> str:
        return self.h.hexdigest()

    def events(self) -> List[Event]:
        out, self.ev = self.ev, []
        return out

    def snapshot(self) -> bytes:
        return json.dumps({"st": {k: (v if k != "q" else {str(kk): vv for kk, vv in v.items()}) for k, v in self.st.items()}, "h": self.h.hexdigest()}, sort_keys=True).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); st = d["st"]; st["q"] = {int(k): [tuple(x) for x in v] for k, v in st["q"].items()}
        self.st = st; self.h = hashlib.sha256(("restored:" + d["h"]).encode()); self.ev = []

    def accounting(self) -> Dict[str, int]:
        return {"world_steps": self.steps}

    def summary(self) -> dict:
        return {"ticks": self.st["t"], "charge": list(self.st["c"]), "alive": list(self.st["a"])}
