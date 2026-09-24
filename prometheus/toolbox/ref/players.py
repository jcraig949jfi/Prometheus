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

from prometheus.toolbox.contracts import ActionSpace, PlayerSpec, flatten
from prometheus.toolbox.ref.worlds import stream


def fold(obs) -> int:
    h = 0
    for i, v in enumerate(flatten(obs)):                              # C100: structured observations fold through the canonical vector
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


# ------------------------------------------------------------------------------------------ sequence.v1 (atlas-bee S1)
def random_sequence(seed: int, length: int = 16, width: int = 2, act_range: int = 8, meta: dict | None = None) -> PlayerSpec:
    """An OPEN-LOOP player: one action vector per tick, replayed cyclically, blind to the observation (the open-loop
    action tensor of NPE lane E's E4b/E10; the control for every closed-vs-open-loop question)."""
    s = stream("sequence", seed)
    actions = [[s.below(act_range) for _ in range(width)] for _ in range(length)]
    return PlayerSpec("sequence.v1", {"actions": actions, "length": length, "width": width, "act_range": act_range}, {}, frozenset(),
                      dict(meta or {}, seed=seed, generator="random_sequence"))


class SequenceInstance:
    def __init__(self, spec: PlayerSpec):
        self.actions = [list(a) for a in spec.payload["actions"]]; self.t = 0
        self._c = {"transitions": 0, "reads": 0, "writes": 0, "ops": 0}

    def act(self, obs, legal: ActionSpace) -> List[int]:
        a = self.actions[self.t % len(self.actions)] if self.actions else []
        self.t += 1; self._c["transitions"] += 1
        return [x % legal.range for x in a[:legal.width]] + [0] * max(0, legal.width - len(a))

    def adapt(self, signal) -> None:
        return None

    def cost(self) -> Dict[str, int]:
        return dict(self._c, params=sum(len(a) for a in self.actions), state_bytes=4)

    def fingerprint(self) -> str:
        return fingerprint_by_probe(self)

    def snapshot(self) -> bytes:
        return json.dumps({"t": self.t, "c": self._c}).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self.t = d["t"]; self._c = d["c"]


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
        outs, status = self.player.run_tick(self.state, [flatten(obs)], 1, self.rng, meter=self.meter)
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
        nxt, acts, mw = self.table[self.state][fold(flatten(obs) + [0 if mem is None else int(mem)]) % self.n_buckets]
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


# ------------------------------------------------------------------------------------------ rewrite.v1 (C33)
def random_rewrite_system(seed: int, n_rules: int = 6, alphabet: int = 8, tape_len: int = 12, meta: dict | None = None) -> PlayerSpec:
    """A token REWRITE SYSTEM as a player (not an agent): rules [a, b] -> [c, d] over an integer alphabet, applied
    left-to-right once per tick to the player's own tape after the observation's first tokens are injected at
    the tape head; the action is the tape's last `width` tokens. Structure = rules + tape; cost = rewrites."""
    s = stream("rewrite", seed)
    rules = [[[s.below(alphabet), s.below(alphabet)], [s.below(alphabet), s.below(alphabet)]] for _ in range(n_rules)]
    tape = [s.below(alphabet) for _ in range(tape_len)]
    return PlayerSpec("rewrite.v1", {"alphabet": alphabet, "rules": rules, "tape": tape, "inject": 2},
                      {}, frozenset(), dict(meta or {}, seed=seed, generator="random_rewrite_system"))


class RewriteInstance:
    def __init__(self, spec: PlayerSpec):
        p = spec.payload
        self.alphabet = p["alphabet"]; self.rules = [(tuple(l), tuple(r)) for l, r in p["rules"]]; self.tape = list(p["tape"]); self.inject = p["inject"]
        self._c = {"transitions": 0, "reads": 0, "writes": 0, "ops": 0, "rewrites": 0}

    def act(self, obs: List[int], legal: ActionSpace) -> List[int]:
        obs = flatten(obs)                                                # C100
        self._c["reads"] += len(obs)
        for i, v in enumerate(obs[:self.inject]):
            self.tape[i] = v % self.alphabet
        t = self.tape; i = 0
        while i < len(t) - 1:
            for lhs, rhs in self.rules:
                if (t[i], t[i + 1]) == lhs:
                    t[i], t[i + 1] = rhs; self._c["rewrites"] += 1; self._c["writes"] += 2
                    break
            i += 1
            self._c["ops"] += 1
        self._c["transitions"] += 1
        acts = t[-legal.width:]
        self.tape = t[1:] + t[:1]                      # the tape is a shift register: injected tokens flow toward the action end
        return [a % legal.range for a in acts] + [0] * max(0, legal.width - len(acts))

    def adapt(self, signal: List[int]) -> None:
        return None

    def cost(self) -> Dict[str, int]:
        return dict(self._c, params=4 * len(self.rules) + len(self.tape), state_bytes=len(self.tape))

    def fingerprint(self) -> str:
        return fingerprint_by_probe(self)

    def snapshot(self) -> bytes:
        return json.dumps({"tape": self.tape, "c": self._c}).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self.tape = d["tape"]; self._c = d["c"]


# ------------------------------------------------------------------------------------------ statemachine.v3 (C65)
def random_statemachine_v3(seed: int, n_states: int = 4, n_buckets: int = 8, width: int = 2, act_range: int = 8, mem_range: int = 16,
                           meta: dict | None = None) -> PlayerSpec:
    """v2 plus EXECUTABLE ARTIFACTS: a cell is [next_state, [acts], op, arg] with op in {0 none, 1 write mem := arg,
    2 create artifact [mem, arg, mem_range] (an affine program), 3 invoke artifact arg -> mem := program(fold(obs))}.
    Prefers ext.workspace.executable.v1 (and kv); requires nothing: elsewhere the ops are refused and counted."""
    s = stream("statemachine.v3", seed)
    table = [[[s.below(n_states), [s.below(act_range) for _ in range(width)], s.below(4), s.below(mem_range)] for _ in range(n_buckets)] for _ in range(n_states)]
    return PlayerSpec("statemachine.v3", {"n_states": n_states, "n_buckets": n_buckets, "width": width, "act_range": act_range, "mem_range": mem_range, "table": table},
                      {"state": 0}, frozenset(), dict(meta or {}, seed=seed, generator="random_statemachine_v3"))


class StateMachineV3Instance(StateMachineV2Instance):
    def __init__(self, spec: PlayerSpec, workspace):
        super().__init__(spec, workspace); self.mem_range = spec.payload["mem_range"]

    def act(self, obs: List[int], legal: ActionSpace) -> List[int]:
        self._c["reads"] += len(obs)
        mem = self.ws.read(); m = 0 if mem is None else int(mem)
        nxt, acts, op, arg = self.table[self.state][fold(flatten(obs) + [m]) % self.n_buckets]     # C100
        self.state = nxt
        if op == 1:
            self.ws.write(int(arg))
        elif op == 2:
            self.ws.create([m % self.mem_range, int(arg), self.mem_range])
        elif op == 3:
            out = self.ws.invoke(int(arg), fold(obs) % self.mem_range)
            if out is not None:
                self.ws.write(int(out) % self.mem_range)
        self._c["transitions"] += 1; self._c["ops"] += 1
        return [a % legal.range for a in acts[:legal.width]] + [0] * max(0, legal.width - len(acts))

    def cost(self) -> Dict[str, int]:
        return dict(self._c, params=sum(len(b[1]) + 3 for row in self.table for b in row), state_bytes=4, **self.ws.cost())
