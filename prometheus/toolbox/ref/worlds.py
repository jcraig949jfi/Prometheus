"""Reference worlds.

  world.integer.v1     WRITE  the kernel's own integer register world: n_regs registers mod 2^16, seeded linear
                              transitions, per-player charge economy with a hidden yield window, action landing
                              delay, optional regime switch and stochastic kick. Pure stdlib, BIT replay,
                              events, snapshot/restore. Deliberately close in spirit to wforge Encounter so the
                              two can be compared, but NOT a copy: wforge stays frozen as its own reference.
  world.wforge.encounter.v0  WRAP  wforge Encounter (SerendipityFoundry/worldfoundry/wforge) behind the same
                              contract; registered only if importable. Trace hash is wforge's own.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List

from prometheus.toolbox.contracts import ActionSpace, EVENT_ID, Event

M = 1 << 16
MASK64 = (1 << 64) - 1


class XS64:
    """xorshift64 -- integer only; the same family wforge uses, seeded by a tag so streams are independent."""

    def __init__(self, seed: int):
        self.s = (seed & MASK64) or 0x9E3779B97F4A7C15

    def next(self) -> int:
        x = self.s
        x ^= (x << 13) & MASK64; x ^= x >> 7; x ^= (x << 17) & MASK64
        self.s = x & MASK64
        return self.s

    def below(self, n: int) -> int:
        return self.next() % n


def stream(*tags) -> XS64:
    h = hashlib.sha256(json.dumps(tags, default=str).encode()).digest()
    return XS64(int.from_bytes(h[:8], "big"))


DEFAULTS = dict(n_regs=6, n_players=1, horizon=64, act_width=2, act_range=8, n_ops=4, obs_regs=4,
                act_cost=1, step_cost=1, start_charge=64, yield_amt=8, yield_width=8192,
                regime_period=0, action_delay=0, stoch_rate=0, world_seed=0, _cheat_skip_dynamics=False)


class IntegerWorld:
    kind = "world.integer.v1"
    capabilities = frozenset({"core.world.v1", "ext.events.v1", "ext.snapshot.v1", "ext.legal_actions.v1",
                              "ext.multiplayer.v1", "ext.intervention.world_params.v1", "ext.cost.v1",
                              "ext.replay.bit.v1", "ext.reference.v1", "ext.world.mutable_params.v1", "ext.world.lifetime_state.v1"})
    replay_class = "BIT"
    MUTABLE = ("regime_period", "stoch_rate", "act_cost", "step_cost", "yield_amt", "action_delay")   # changeable at a tick boundary

    def set_params(self, **changes) -> None:
        """ext.world.mutable_params.v1: apply at a tick boundary; the trace covers the change through its effects and
        the TASK_CHANGE event names each changed parameter index."""
        bad = sorted(set(changes) - set(self.MUTABLE))
        if bad:
            raise ValueError("world.integer.v1: params %s are not runtime-mutable (mutable: %s)" % (bad, list(self.MUTABLE)))
        t = self._state["tick"] if self._state else 0
        for k, v in changes.items():
            self.p[k] = v
            self._events.append((t, EVENT_ID["TASK_CHANGE"], -1, self.MUTABLE.index(k), int(v)))

    def __init__(self, **params):
        unknown = sorted(set(params) - set(DEFAULTS))
        if unknown:
            raise ValueError("world.integer.v1: unknown params %s" % unknown)
        self.p = dict(DEFAULTS, **params)
        p = self.p
        self.n_players = p["n_players"]
        s = stream("structure", p["world_seed"])
        R = p["n_regs"]
        self.lin_ops = [(s.below(R), s.below(7) + 1, s.below(R), s.below(7) + 1, s.below(R), s.below(M)) for _ in range(p["n_ops"])]
        self.act_targets = [s.below(R) for _ in range(p["act_width"])]
        self.yield_reg = s.below(R)
        self.yield_lo = s.below(M)
        self.yield_hi = (self.yield_lo + p["yield_width"]) % M
        self.obs_regs = list(range(min(p["obs_regs"], R)))
        self._state = None
        self._events: List[Event] = []
        self._steps = 0

    # ------------------------------------------------------------ identity
    def manifest(self) -> dict:
        return {"kind": self.kind, "params": self.p, "lin_ops": self.lin_ops, "act_targets": self.act_targets,
                "yield": [self.yield_reg, self.yield_lo, self.yield_hi], "obs_regs": self.obs_regs}

    # ------------------------------------------------------------ core.world.v1
    def reset(self, seed: int, keep: bool = False) -> None:
        """keep=True (ext.world.lifetime_state.v1): registers, pending actions and the stochastic stream carry over
        from the previous episode; charge, survival and the tick restart. The trace restarts per episode."""
        p = self.p
        s = stream("init", p["world_seed"], seed)
        if keep and self._state is not None:
            prev = self._state
            regs = list(prev["regs"]); pending = [(q[0] - prev["tick"], q[1], q[2], q[3]) for q in prev["pending"]]; stoch = prev["stoch"]
        else:
            regs = [s.below(M) for _ in range(p["n_regs"])]; pending = []; stoch = stream("stoch", p["world_seed"], seed).s
        self._state = {"tick": 0, "regs": regs, "charge": [p["start_charge"]] * self.n_players, "alive": [True] * self.n_players,
                       "pending": pending, "seed": seed, "stoch": stoch}
        self._trace = hashlib.sha256()
        self._events = []                     # _steps is cumulative over the world's lifetime (accounting), never reset here

    def observe(self, player_id: int) -> List[int]:
        st = self._state
        return [st["regs"][i] for i in self.obs_regs] + [min(15, max(0, st["charge"][player_id]) // 8)]

    def legal_actions(self, player_id: int) -> ActionSpace:
        return ActionSpace(self.p["act_width"], self.p["act_range"])

    def step(self, actions: Dict[int, List[int]]) -> bool:
        p = self.p; st = self._state; t = st["tick"]; ev = self._events
        # phase 1: action intake (simultaneous)
        for pid in range(self.n_players):
            if not st["alive"][pid]:
                continue
            a = list(actions.get(pid, []))[:p["act_width"]]
            a = [x % p["act_range"] for x in a] + [0] * (p["act_width"] - len(a))
            mag = sum(a); cost = mag * p["act_cost"]
            if cost > st["charge"][pid]:
                mag, cost = 0, 0
            if cost:
                st["charge"][pid] -= cost
                ev.append((t, EVENT_ID["RESOURCE_CHANGE"], pid, 0, -cost))
            ev.append((t, EVENT_ID["ACTION"], pid, 0, mag))
            if mag:
                for i, x in enumerate(a):
                    if x:
                        st["pending"].append((t + p["action_delay"], pid, self.act_targets[i], x * 97))
        # phase 2: world transition (deterministic order)
        landing = sorted((q for q in st["pending"] if q[0] == t), key=lambda q: (q[1], q[2]))
        st["pending"] = [q for q in st["pending"] if q[0] > t]
        for _, pid, tgt, amt in landing:
            st["regs"][tgt] = (st["regs"][tgt] + amt) % M
            ev.append((t, EVENT_ID["STATE_WRITE"], pid, tgt, amt))
        if not p["_cheat_skip_dynamics"]:
            flip = bool(p["regime_period"]) and (t // p["regime_period"]) % 2 == 1
            regs = st["regs"]
            for dst, a, s1, b, s2, c in self.lin_ops:
                aa = (M - a) % M if flip else a
                regs[dst] = (aa * regs[s1] + b * regs[s2] + c) % M
            if p["stoch_rate"]:
                xs = XS64(st["stoch"])
                if xs.below(p["stoch_rate"]) == 0:
                    regs[xs.below(p["n_regs"])] = xs.below(M)
                st["stoch"] = xs.s
        # phase 3: economy (simultaneous settlement)
        v = st["regs"][self.yield_reg]
        lo, hi = self.yield_lo, self.yield_hi
        in_win = (lo <= v < hi) if lo < hi else (v >= lo or v < hi)
        winners = [i for i in range(self.n_players) if st["alive"][i]] if in_win else []
        for pid in range(self.n_players):
            if not st["alive"][pid]:
                continue
            st["charge"][pid] -= p["step_cost"]
            if pid in winners:
                gain = p["yield_amt"] // len(winners)
                st["charge"][pid] += gain
                ev.append((t, EVENT_ID["YIELD"], pid, self.yield_reg, gain))
                if len(winners) > 1:
                    ev.append((t, EVENT_ID["CONTACT"], pid, len(winners), gain))
            if st["charge"][pid] <= 0:
                st["alive"][pid] = False
                ev.append((t, EVENT_ID["ABSORBED"], pid, 0, st["charge"][pid]))
        self._trace.update(json.dumps([t, st["regs"], st["charge"], st["alive"]]).encode())
        st["tick"] = t + 1
        self._steps += 1
        return st["tick"] >= p["horizon"] or (self.n_players > 0 and not any(st["alive"]))     # C84: a zero-player world runs to its horizon

    def trace_hash(self) -> str:
        return self._trace.hexdigest()

    # ------------------------------------------------------------ ext.events.v1 / ext.snapshot.v1 / ext.cost.v1
    def events(self) -> List[Event]:
        out, self._events = self._events, []
        return out

    def snapshot(self) -> bytes:
        return json.dumps({"state": self._state, "trace": self._trace.hexdigest(), "steps": self._steps}, sort_keys=True).encode()

    def restore(self, snapshot: bytes) -> None:
        # The trace object cannot be resumed from a digest, so a restored world's trace hash covers only ticks
        # after the restore and is prefixed by the snapshot's digest. Receipts mark this (replay class PARTIAL).
        d = json.loads(snapshot.decode())
        self._state = d["state"]
        self._trace = hashlib.sha256(("restored:" + d["trace"]).encode())
        self._events = []

    def accounting(self) -> Dict[str, int]:
        return {"world_steps": self._steps}

    def summary(self) -> dict:
        st = self._state
        return {"ticks": st["tick"], "charge": list(st["charge"]), "alive": list(st["alive"])}


# ---------------------------------------------------------------------------------------------- wforge (WRAP)
def _wforge():
    from SerendipityFoundry.worldfoundry.wforge import world as W, genome as G   # namespace package from the repo root
    return W, G


class WforgeEncounterWorld:
    kind = "world.wforge.encounter.v0"
    capabilities = frozenset({"core.world.v1", "ext.legal_actions.v1", "ext.multiplayer.v1", "ext.cost.v1", "ext.replay.bit.v1"})
    replay_class = "BIT"

    def __init__(self, genome_seed: int = 0, grammar_version: str = "v0", _cheat_skip_dynamics: bool = False):
        W, G = _wforge()
        self._W = W
        self.genome = G.de_novo(grammar_version, genome_seed)
        self.mech = W.expand(self.genome)
        self.n_players = self.mech.n_slots
        self._enc = None
        self._steps = 0
        self._cheat = bool(_cheat_skip_dynamics)     # C71: the WRAPPER's cheat -- the engine is never stepped

    def manifest(self) -> dict:
        return {"kind": self.kind, "world_id": self.genome.world_id, "mechanics_hash": self.mech.manifest_hash(), "wrapper_cheat": self._cheat}

    def reset(self, seed: int) -> None:
        self._enc = self._W.Encounter(self.mech, self.genome.world_id, seed); self._steps = 0

    def observe(self, player_id: int) -> List[int]:
        return list(self._enc.observe(player_id))

    def legal_actions(self, player_id: int) -> ActionSpace:
        return ActionSpace(self.mech.act_width, 8)

    def step(self, actions: Dict[int, List[int]]) -> bool:
        acts = [list(actions.get(i, [0] * self.mech.act_width)) for i in range(self.n_players)]
        self._steps += 1
        if self._cheat:
            self._enc.tick += 1                            # time passes, nothing happens: the engine is frozen
            return self._enc.tick >= self.mech.horizon
        return self._enc.step(acts)

    def trace_hash(self) -> str:
        return self._enc.outcome()["trace_hash"]

    def events(self) -> List[Event]:
        return []

    def accounting(self) -> Dict[str, int]:
        return {"world_steps": self._steps}

    def summary(self) -> dict:
        o = self._enc.outcome()
        return {"ticks": o["ticks"], "charge": [s["final_charge"] for s in o["per_slot"]], "alive": [s["alive"] for s in o["per_slot"]]}


# ---------------------------------------------------------------------------------------------- campaign-6 ComposedWorld (WRAP, C39)
def _c6():
    from archaeon.campaign6.worlds import generator as G6
    from archaeon.campaign6.worlds import runtime as R6
    return G6, R6


class C6ComposedWorld:
    """Archaeon's campaign-6 ComposedWorld behind the kernel World contract (archaeon/ untouched). One organism,
    channel observations flattened to one word list, actions = one 32-bit word per output channel, FLOAT pools
    quantised (x1e6) for the trace and the events. Python float arithmetic here is +,*,min,max on doubles and
    agreed 3/3 across Windows/Linux (C47) -- but after C63 showed a libm world differing at a fine quantum, any
    float world declares the honest class: SEMANTIC with quantum 1e-6 (C64). The claim is "agreement at the
    declared quantum", which is what the trace actually tests."""
    kind = "world.c6.composed.v1"
    capabilities = frozenset({"core.world.v1", "ext.events.v1", "ext.legal_actions.v1", "ext.cost.v1", "ext.replay.semantic.v1"})
    replay_class = "SEMANTIC"
    Q = 1_000_000

    def __init__(self, seed: int | None = None, bin: int | None = None, params: dict | None = None, ticks: int = 24, _cheat_skip_dynamics: bool = False):
        G6, R6 = _c6()
        self._cheat = bool(_cheat_skip_dynamics)     # C71: wrapper-level cheat
        if params is None:
            rec = G6.sample_world(int(seed or 0), bin_target=bin, ticks=ticks); params = rec["params"]; self.record = rec
        else:
            self.record = None
        self.w = R6.ComposedWorld(params); self.params = params
        self.n_players = 1; self._st = None; self._events: List[Event] = []; self._steps = 0; self._last_reward = 0.0; self._seed = 0

    def manifest(self) -> dict:
        return {"kind": self.kind, "world_id": self.w.world_id(), "features": list(self.w.features), "params": self.params, "float_state": True, "quantum": 1.0 / self.Q, "wrapper_cheat": self._cheat}

    def reset(self, seed: int) -> None:
        self._seed = seed; self._st = self.w.reset(seed, 0, None); self._trace = hashlib.sha256(); self._events = []; self._last_reward = 0.0

    def observe(self, player_id: int) -> List[int]:
        return [int(x) & 0xFFFFFFFF for ch in self.w.observe(self._st) for x in ch]

    def legal_actions(self, player_id: int) -> ActionSpace:
        return ActionSpace(self.w.K, 1 << 32)

    def step(self, actions: Dict[int, List[int]]) -> bool:
        st = self._st; t = st["tick"]; a = list(actions.get(0, []))
        outputs = [[int(x) & 0xFFFFFFFF] for x in a[:self.w.K]]
        self._events.append((t, EVENT_ID["ACTION"], 0, 0, sum(1 for x in a if x)))
        before_cells = list(st["cells"]); was_alive = st["alive"]
        if self._cheat:
            st["tick"] += 1                                # frozen engine: only the clock moves
        else:
            self.w.act(st, outputs)
        gain = st["reward"] - self._last_reward
        if gain > 0:
            self._events.append((t, EVENT_ID["YIELD"], 0, 0, int(gain * self.Q)))
        elif gain < 0:
            self._events.append((t, EVENT_ID["RESOURCE_CHANGE"], 0, 0, int(gain * self.Q)))
        self._last_reward = st["reward"]
        for j, (b, c) in enumerate(zip(before_cells, st["cells"])):
            if b != c:
                self._events.append((t, EVENT_ID["STATE_WRITE"], 0, j, c))
        if was_alive and not st["alive"]:
            self._events.append((t, EVENT_ID["ABSORBED"], 0, 0, 0))
        q = [t, st["pos"], int(st["reward"] * self.Q), [int(p * self.Q) for p in st["pools"]], list(st["cells"]), st["alive"], st["signal"][0]]
        self._trace.update(json.dumps(q).encode())
        self._steps += 1
        return self.w.done(st)

    def trace_hash(self) -> str:
        return self._trace.hexdigest()

    def events(self) -> List[Event]:
        out, self._events = self._events, []
        return out

    def accounting(self) -> Dict[str, int]:
        return {"world_steps": self._steps}

    def summary(self) -> dict:
        st = self._st
        return {"ticks": st["tick"], "charge": [int(st["reward"] * self.Q)], "alive": [bool(st["alive"])], "features": list(self.w.features)}
