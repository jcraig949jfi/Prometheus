"""world.grid.v1 (overnight C41, WRITE route): a second home-written world, Ludus-shaped (directive s30) --
multiple players on a ring of L nodes, persistent OBJECTS (cells at nodes that hold an integer and pay when
read by someone who did not write them), RESOURCES (pools that regenerate, deplete when harvested, and are
contested), PARTIAL OBSERVABILITY (a player sees only its node: pool amount, cell value, neighbours present,
its own charge), CONSTRUCTION (a WRITE action changes a cell; a cell is a tool for whoever reads it later),
CONTACT (two players on one node), and lifetime state (ext.world.lifetime_state.v1: cells and pools carry
across episodes). Integer only, BIT replay, events, snapshot, runtime-mutable economics.

Action word: [move, verb, value]  move in {0 stay, 1 clockwise, 2 anticlockwise}; verb in {0 none, 1 HARVEST,
2 WRITE cell := value, 3 READ cell (pays if written by another player)}; value in [0, act_range).
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List

from prometheus.toolbox.contracts import ActionSpace, EVENT_ID, Event
from prometheus.toolbox.ref.worlds import stream, M

DEFAULTS = dict(n_nodes=8, n_players=2, horizon=64, act_range=8, start_charge=40, step_cost=1, move_cost=1, harvest_gain=6,
                pool_max=3, regen_every=4, write_cost=2, read_gain=5, world_seed=0, _cheat_skip_dynamics=False)


class GridWorld:
    kind = "world.grid.v1"
    capabilities = frozenset({"core.world.v1", "ext.events.v1", "ext.snapshot.v1", "ext.legal_actions.v1", "ext.multiplayer.v1",
                              "ext.intervention.world_params.v1", "ext.cost.v1", "ext.replay.bit.v1", "ext.world.mutable_params.v1",
                              "ext.world.lifetime_state.v1"})
    replay_class = "BIT"
    MUTABLE = ("step_cost", "move_cost", "harvest_gain", "regen_every", "write_cost", "read_gain")

    def __init__(self, **params):
        unknown = sorted(set(params) - set(DEFAULTS))
        if unknown:
            raise ValueError("world.grid.v1: unknown params %s" % unknown)
        self.p = dict(DEFAULTS, **params); self.n_players = self.p["n_players"]
        self._state = None; self._events: List[Event] = []; self._steps = 0

    def manifest(self) -> dict:
        return {"kind": self.kind, "params": self.p}

    def set_params(self, **changes) -> None:
        bad = sorted(set(changes) - set(self.MUTABLE))
        if bad:
            raise ValueError("world.grid.v1: params %s are not runtime-mutable (mutable: %s)" % (bad, list(self.MUTABLE)))
        t = self._state["tick"] if self._state else 0
        for k, v in changes.items():
            self.p[k] = v; self._events.append((t, EVENT_ID["TASK_CHANGE"], -1, self.MUTABLE.index(k), int(v)))

    def reset(self, seed: int, keep: bool = False) -> None:
        p = self.p; s = stream("grid.init", p["world_seed"], seed); L = p["n_nodes"]
        if keep and self._state is not None:
            prev = self._state; pools = list(prev["pools"]); cells = list(prev["cells"]); owner = list(prev["owner"])
        else:
            pools = [s.below(p["pool_max"] + 1) for _ in range(L)]; cells = [0] * L; owner = [-1] * L
        self._state = {"tick": 0, "pos": [s.below(L) for _ in range(self.n_players)], "charge": [p["start_charge"]] * self.n_players,
                       "alive": [True] * self.n_players, "pools": pools, "cells": cells, "owner": owner, "seed": seed}
        self._trace = hashlib.sha256(); self._events = []

    def observe(self, pid: int) -> List[int]:
        st = self._state; n = st["pos"][pid]
        others = sum(1 for q in range(self.n_players) if q != pid and st["alive"][q] and st["pos"][q] == n)
        return [n, st["pools"][n], st["cells"][n], 1 if st["owner"][n] not in (-1, pid) else 0, others, min(15, max(0, st["charge"][pid]) // 4)]

    def legal_actions(self, pid: int) -> ActionSpace:
        return ActionSpace(3, self.p["act_range"])

    def step(self, actions: Dict[int, List[int]]) -> bool:
        p = self.p; st = self._state; t = st["tick"]; ev = self._events; L = p["n_nodes"]
        moves: Dict[int, int] = {}; verbs: Dict[int, tuple] = {}
        for pid in range(self.n_players):
            if not st["alive"][pid]:
                continue
            a = [x % p["act_range"] for x in list(actions.get(pid, []))[:3]] + [0, 0, 0]
            moves[pid] = a[0] % 3; verbs[pid] = (a[1] % 4, a[2])
            ev.append((t, EVENT_ID["ACTION"], pid, a[0] % 3, a[1] % 4))
        # movement (simultaneous)
        for pid, mv in moves.items():
            if mv and st["charge"][pid] > p["move_cost"]:
                st["pos"][pid] = (st["pos"][pid] + (1 if mv == 1 else -1)) % L; st["charge"][pid] -= p["move_cost"]
                ev.append((t, EVENT_ID["RESOURCE_CHANGE"], pid, 0, -p["move_cost"]))
        # verbs, in player order (a deterministic contention rule)
        if not p["_cheat_skip_dynamics"]:
            for pid in sorted(verbs):
                verb, val = verbs[pid]; n = st["pos"][pid]
                if verb == 1 and st["pools"][n] > 0:
                    st["pools"][n] -= 1; st["charge"][pid] += p["harvest_gain"]; ev.append((t, EVENT_ID["YIELD"], pid, n, p["harvest_gain"]))
                elif verb == 2 and st["charge"][pid] > p["write_cost"]:
                    st["cells"][n] = val; st["owner"][n] = pid; st["charge"][pid] -= p["write_cost"]
                    ev.append((t, EVENT_ID["ARTIFACT_CREATE"], pid, n, val))
                elif verb == 3 and st["owner"][n] not in (-1, pid) and st["cells"][n] != 0:
                    st["charge"][pid] += p["read_gain"]; ev.append((t, EVENT_ID["ARTIFACT_INVOKE"], pid, n, st["cells"][n]))
                    st["cells"][n] = 0; st["owner"][n] = -1                    # a tool is consumed by its use
            if p["regen_every"] and t % p["regen_every"] == 0:
                for n in range(L):
                    if st["pools"][n] < p["pool_max"]:
                        st["pools"][n] += 1
        # contact + metabolism
        for pid in range(self.n_players):
            if not st["alive"][pid]:
                continue
            here = [q for q in range(self.n_players) if q != pid and st["alive"][q] and st["pos"][q] == st["pos"][pid]]
            if here:
                ev.append((t, EVENT_ID["CONTACT"], pid, st["pos"][pid], len(here)))
            st["charge"][pid] -= p["step_cost"]
            if st["charge"][pid] <= 0:
                st["alive"][pid] = False; ev.append((t, EVENT_ID["ABSORBED"], pid, st["pos"][pid], st["charge"][pid]))
        self._trace.update(json.dumps([t, st["pos"], st["charge"], st["alive"], st["pools"], st["cells"], st["owner"]]).encode())
        st["tick"] = t + 1; self._steps += 1
        return st["tick"] >= p["horizon"] or not any(st["alive"])

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
        return {"ticks": st["tick"], "charge": list(st["charge"]), "alive": list(st["alive"]), "cells_nonzero": sum(1 for c in st["cells"] if c), "pools": list(st["pools"])}
