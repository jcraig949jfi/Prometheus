"""Reference player REPRESENTATIONS (core.player.v1) and their instances. A representation is a registry
row of slot "representation"; a Substrate lists which representations it can instantiate. A PlayerSpec
is data; the instance below is what a substrate builds from it.

  statemachine.v1   WRITE  Mealy machine: `n_states` states, `n_buckets` observation buckets, a table
                           table[state][bucket] = [next_state, [a_0 .. a_{width-1}]]. Bucket = fold(obs) % n_buckets.
  constant.v1       WRITE  emits a fixed action vector; the negative-control player.
  proteus.tape.v0   WRAP   a Proteus v0 player manifest run one tick per world tick through proteus.foundry.vm.Player;
                           inputs = [observation words]; outputs channel 0 -> actions. Registered only if importable.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List

from prometheus.toolbox.contracts import ActionSpace, PlayerSpec
from prometheus.toolbox.ref.worlds import stream


def fold(obs: List[int]) -> int:
    h = 0
    for i, v in enumerate(obs):
        h = (h * 31 + (v + 1) * (i + 1)) & 0xFFFFFFFF
    return h


# ------------------------------------------------------------------------------------------ statemachine.v1
def random_statemachine(seed: int, n_states: int = 4, n_buckets: int = 8, width: int = 2, act_range: int = 8, meta: dict | None = None) -> PlayerSpec:
    s = stream("statemachine", seed)
    table = [[[s.below(n_states), [s.below(act_range) for _ in range(width)]] for _ in range(n_buckets)] for _ in range(n_states)]
    return PlayerSpec("statemachine.v1", {"n_states": n_states, "n_buckets": n_buckets, "width": width, "act_range": act_range, "table": table},
                      {"state": 0}, frozenset(), dict(meta or {}, seed=seed, generator="random_statemachine"))


class StateMachineInstance:
    def __init__(self, spec: PlayerSpec):
        p = spec.payload
        self.table = p["table"]; self.n_buckets = p["n_buckets"]; self.width = p["width"]
        self.state = int(spec.initial_state.get("state", 0))
        self._c = {"transitions": 0, "reads": 0, "writes": 0, "ops": 0}

    def act(self, obs: List[int], legal: ActionSpace) -> List[int]:
        self._c["reads"] += len(obs)
        nxt, acts = self.table[self.state][fold(obs) % self.n_buckets]
        self.state = nxt
        self._c["transitions"] += 1; self._c["ops"] += 1
        return [a % legal.range for a in acts[:legal.width]] + [0] * max(0, legal.width - len(acts))

    def adapt(self, signal: List[int]) -> None:
        return None

    def cost(self) -> Dict[str, int]:
        return dict(self._c, params=sum(len(b[1]) + 1 for row in self.table for b in row), state_bytes=4)

    def fingerprint(self) -> str:
        return fingerprint_by_probe(self)

    def snapshot(self) -> bytes:
        return json.dumps({"state": self.state, "c": self._c}).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self.state = d["state"]; self._c = d["c"]


# ------------------------------------------------------------------------------------------ constant.v1
def constant_player(actions: List[int], meta: dict | None = None) -> PlayerSpec:
    return PlayerSpec("constant.v1", {"actions": list(actions)}, {}, frozenset(), dict(meta or {}, generator="constant_player"))


class ConstantInstance:
    def __init__(self, spec: PlayerSpec):
        self.actions = list(spec.payload["actions"]); self._c = {"transitions": 0, "reads": 0, "writes": 0, "ops": 0}

    def act(self, obs: List[int], legal: ActionSpace) -> List[int]:
        self._c["transitions"] += 1
        return [a % legal.range for a in self.actions[:legal.width]] + [0] * max(0, legal.width - len(self.actions))

    def adapt(self, signal: List[int]) -> None:
        return None

    def cost(self) -> Dict[str, int]:
        return dict(self._c, params=len(self.actions), state_bytes=0)

    def fingerprint(self) -> str:
        return fingerprint_by_probe(self)

    def snapshot(self) -> bytes:
        return json.dumps(self._c).encode()

    def restore(self, snapshot: bytes) -> None:
        self._c = json.loads(snapshot.decode())


# ------------------------------------------------------------------------------------------ proteus.tape.v0 (WRAP)
def proteus_available() -> bool:
    try:
        from proteus.foundry.vm import Player  # noqa: F401
        return True
    except Exception:
        return False


def random_proteus_player(seed: int, meta: dict | None = None) -> PlayerSpec:
    from proteus.foundry import generate as G
    fm = dict(G.DEFAULT_FOUNDRY_MANIFEST); fm["seed"] = seed; fm["n"] = 1
    org = G.generate(fm)[0]                       # organism record: organism_id, lineage_id, generation, runtime_hash, manifest
    return PlayerSpec("proteus.tape.v0", {"manifest": org["manifest"]}, {}, frozenset(),
                      dict(meta or {}, seed=seed, generator="proteus.foundry.generate", organism_id=org["organism_id"], runtime_hash=org["runtime_hash"]))


class ProteusTapeInstance:
    def __init__(self, spec: PlayerSpec, seed: int):
        from proteus.foundry.vm import Player, Meter
        from proteus.foundry.prng import SplitMix64, seed_from
        self.player = Player(spec.payload["manifest"]); self.meter = Meter()
        self.state = self.player.fresh_state()
        self.rng = SplitMix64(seed_from("toolbox.player", seed))
        self._ticks = 0

    def act(self, obs: List[int], legal: ActionSpace) -> List[int]:
        outs, status = self.player.run_tick(self.state, [list(obs)], 1, self.rng, meter=self.meter)
        self._ticks += 1
        words = outs[0] if outs and outs[0] else []
        return [w % legal.range for w in words[:legal.width]] + [0] * max(0, legal.width - len(words))

    def adapt(self, signal: List[int]) -> None:
        return None

    def cost(self) -> Dict[str, int]:
        m = self.meter.as_dict(self.player.m)
        return {"transitions": self._ticks, "ops": int(m.get("ops", 0)), "reads": int(m.get("in_reads", 0)), "writes": int(m.get("code_writes", 0)),
                "params": self.player.genome_len, "state_bytes": 4 * (self.player.tape_words + self.player.n_regs)}

    def fingerprint(self) -> str:
        return fingerprint_by_probe(self)

    def snapshot(self) -> bytes:
        # COMPLETE state (C5c, 2026-09-19): tape/regs/ip, the tick count, the rng stream AND the meter -- a probe
        # that restores less than this disturbs the run it claims not to touch.
        m = self.meter
        meter = {k: (dict(getattr(m, k)) if k == "by_category" else getattr(m, k)) for k in m.__slots__}
        return json.dumps({"state": self.state, "ticks": self._ticks, "rng": self.rng.state, "meter": meter}).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self.state = d["state"]; self._ticks = d["ticks"]; self.rng.state = d["rng"]
        for k, v in d["meter"].items():
            setattr(self.meter, k, dict(v) if k == "by_category" else v)


# ------------------------------------------------------------------------------------------ fingerprint
PROBE = [[(i * 7919 + j * 104729) % 65536 for j in range(5)] for i in range(16)]


def fingerprint_by_probe(inst) -> str:
    """Behavioural identity on a FIXED probe set, taken from a snapshot so the probe never disturbs the run."""
    snap = inst.snapshot()
    h = hashlib.sha256()
    for obs in PROBE:
        h.update(bytes(inst.act(obs, ActionSpace(2, 8))))
    inst.restore(snap)
    return h.hexdigest()[:16]


SILENT_FINGERPRINT = hashlib.sha256(b"".join(bytes([0, 0]) for _ in PROBE)).hexdigest()[:16]


def probe_silent(inst) -> bool:
    """True when the player emitted only zero actions on the whole probe (C5b, 2026-09-19: 49/60 random Proteus
    players are silent, and every silent player shares ONE fingerprint -- silence must be visible, not a hash)."""
    return fingerprint_by_probe(inst) == SILENT_FINGERPRINT


# ------------------------------------------------------------------------------------------ statemachine.v2 (C6)
def random_statemachine_v2(seed: int, n_states: int = 4, n_buckets: int = 8, width: int = 2, act_range: int = 8, mem_range: int = 16,
                           write_every: int = 2, meta: dict | None = None) -> PlayerSpec:
    """Mealy machine with ONE memory slot that lives in the substrate's workspace: bucket = fold(obs + [mem]) % B;
    a transition cell is [next_state, [acts], mem_write] with mem_write = -1 (no write) or a value in [0, mem_range).
    The representation PREFERS a workspace and requires nothing: on a substrate without one it runs memoryless."""
    s = stream("statemachine.v2", seed)
    table = [[[s.below(n_states), [s.below(act_range) for _ in range(width)], (s.below(mem_range) if s.below(write_every) == 0 else -1)]
              for _ in range(n_buckets)] for _ in range(n_states)]
    return PlayerSpec("statemachine.v2", {"n_states": n_states, "n_buckets": n_buckets, "width": width, "act_range": act_range, "mem_range": mem_range, "table": table},
                      {"state": 0}, frozenset(), dict(meta or {}, seed=seed, generator="random_statemachine_v2"))


class StateMachineV2Instance:
    def __init__(self, spec: PlayerSpec, workspace):
        p = spec.payload
        self.table = p["table"]; self.n_buckets = p["n_buckets"]; self.width = p["width"]
        self.state = int(spec.initial_state.get("state", 0))
        self.ws = workspace
        self._c = {"transitions": 0, "reads": 0, "writes": 0, "ops": 0}

    def act(self, obs: List[int], legal: ActionSpace) -> List[int]:
        self._c["reads"] += len(obs)
        mem = self.ws.read()
        nxt, acts, mw = self.table[self.state][fold(list(obs) + [0 if mem is None else int(mem)]) % self.n_buckets]
        self.state = nxt
        if mw >= 0:
            self.ws.write(int(mw))
        self._c["transitions"] += 1; self._c["ops"] += 1
        return [a % legal.range for a in acts[:legal.width]] + [0] * max(0, legal.width - len(acts))

    def adapt(self, signal: List[int]) -> None:
        return None

    def cost(self) -> Dict[str, int]:
        return dict(self._c, params=sum(len(b[1]) + 2 for row in self.table for b in row), state_bytes=4, **self.ws.cost())

    def fingerprint(self) -> str:
        return fingerprint_by_probe(self)

    def snapshot(self) -> bytes:
        return json.dumps({"state": self.state, "c": self._c, "ws": self.ws.snapshot().hex()}).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self.state = d["state"]; self._c = d["c"]; self.ws.restore(bytes.fromhex(d["ws"]))
