"""world.pendulum.v1 (overnight C63): the reference SEMANTIC world.

A damped, driven pendulum per player with FLOAT state through math.sin / math.cos (libm-dependent across
platforms), and an integer charge economy. The trace hashes the state QUANTISED at the declared `quantum`
-- a condition of the experiment, in the manifest before any run -- so two runs agree iff every quantised
state agrees; the quantum is never widened after a result. Actions are fixed-point (ext.continuous_actions.v1):
[torque, brake] integers in [0, act_range) scaled by act_scale inside. Upright within `upright_band` pays.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Dict, List

from prometheus.toolbox.contracts import ActionSpace, EVENT_ID, Event
from prometheus.toolbox.ref.worlds import stream

DEFAULTS = dict(n_players=1, horizon=64, act_range=8, act_scale=0.05, dt=0.05, damping=0.02, gravity=9.81, length=1.0,
                start_charge=64, step_cost=1, torque_cost=1, upright_gain=4, upright_band=0.3, quantum=1e-6, world_seed=0,
                _cheat_skip_dynamics=False)


class PendulumWorld:
    kind = "world.pendulum.v1"
    capabilities = frozenset({"core.world.v1", "ext.events.v1", "ext.snapshot.v1", "ext.legal_actions.v1", "ext.multiplayer.v1",
                              "ext.intervention.world_params.v1", "ext.cost.v1", "ext.replay.semantic.v1", "ext.continuous_actions.v1",
                              "ext.reference.v1"})
    replay_class = "SEMANTIC"

    def __init__(self, **params):
        unknown = sorted(set(params) - set(DEFAULTS))
        if unknown:
            raise ValueError("world.pendulum.v1: unknown params %s" % unknown)
        self.p = dict(DEFAULTS, **params); self.n_players = self.p["n_players"]
        if not (0 < float(self.p["quantum"]) <= 1):
            raise ValueError("quantum must be in (0, 1]")
        self._state = None; self._events: List[Event] = []; self._steps = 0

    def manifest(self) -> dict:
        return {"kind": self.kind, "params": self.p, "quantum": self.p["quantum"], "float_state": True, "libm": True}

    def _q(self, x: float) -> int:
        return int(round(x / self.p["quantum"]))

    def reset(self, seed: int) -> None:
        s = stream("pendulum", self.p["world_seed"], seed)
        self._state = {"tick": 0, "theta": [(s.below(2000) - 1000) / 1000.0 * math.pi for _ in range(self.n_players)],
                       "omega": [0.0] * self.n_players, "charge": [self.p["start_charge"]] * self.n_players, "alive": [True] * self.n_players}
        self._trace = hashlib.sha256(); self._events = []

    def observe(self, pid: int) -> List[int]:
        st = self._state
        return [self._q(math.sin(st["theta"][pid])) & 0xFFFFFFFF, self._q(math.cos(st["theta"][pid])) & 0xFFFFFFFF,
                self._q(st["omega"][pid]) & 0xFFFFFFFF, min(15, max(0, st["charge"][pid]) // 4)]

    def legal_actions(self, pid: int) -> ActionSpace:
        return ActionSpace(2, self.p["act_range"])

    def step(self, actions: Dict[int, List[int]]) -> bool:
        p = self.p; st = self._state; t = st["tick"]; ev = self._events
        for pid in range(self.n_players):
            if not st["alive"][pid]:
                continue
            a = [x % p["act_range"] for x in list(actions.get(pid, []))[:2]] + [0, 0]
            torque = (a[0] - p["act_range"] // 2) * p["act_scale"]; brake = a[1] * p["act_scale"]
            cost = (abs(a[0] - p["act_range"] // 2) + a[1]) * p["torque_cost"]
            if cost > st["charge"][pid]:
                torque = 0.0; brake = 0.0; cost = 0
            st["charge"][pid] -= cost
            ev.append((t, EVENT_ID["ACTION"], pid, 0, cost))
            if not p["_cheat_skip_dynamics"]:
                th, om = st["theta"][pid], st["omega"][pid]
                acc = -(p["gravity"] / p["length"]) * math.sin(th) - (p["damping"] + brake) * om + torque
                om = om + acc * p["dt"]; th = th + om * p["dt"]
                th = (th + math.pi) % (2 * math.pi) - math.pi
                st["theta"][pid], st["omega"][pid] = th, om
            if abs(abs(st["theta"][pid]) - math.pi) < p["upright_band"]:
                st["charge"][pid] += p["upright_gain"]; ev.append((t, EVENT_ID["YIELD"], pid, 0, p["upright_gain"]))
            st["charge"][pid] -= p["step_cost"]
            if st["charge"][pid] <= 0:
                st["alive"][pid] = False; ev.append((t, EVENT_ID["ABSORBED"], pid, 0, st["charge"][pid]))
        q = [t, [self._q(x) for x in st["theta"]], [self._q(x) for x in st["omega"]], st["charge"], st["alive"]]
        self._trace.update(json.dumps(q).encode())
        st["tick"] = t + 1; self._steps += 1
        return st["tick"] >= p["horizon"] or (self.n_players > 0 and not any(st["alive"]))   # C85

    def trace_hash(self) -> str:
        return self._trace.hexdigest()

    def events(self) -> List[Event]:
        out, self._events = self._events, []
        return out

    def snapshot(self) -> bytes:
        return json.dumps({"state": self._state, "trace": self._trace.hexdigest()}, sort_keys=True).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self._state = d["state"]; self._trace = hashlib.sha256(("restored:" + d["trace"]).encode()); self._events = []

    def accounting(self) -> Dict[str, int]:
        return {"world_steps": self._steps}

    def summary(self) -> dict:
        st = self._state
        return {"ticks": st["tick"], "charge": list(st["charge"]), "alive": list(st["alive"]), "theta_q": [self._q(x) for x in st["theta"]]}
