"""Reference substrate.

  substrate.flat.v1   WRITE  the flat in-process machine: instantiates statemachine.v1, constant.v1 and (when
                             proteus imports) proteus.tape.v0; no workspace; raw cost accounting aggregated over
                             its instances. It offers players NO extension capabilities: a player that `requires`
                             ext.workspace.* cannot be instantiated here, and the negotiation says so.

A Substrate is the boundary that decides what a player can touch (directive s6, s12). Phase 2 adds
substrates that expose a StateDevice as workspace.kv / workspace.stream to the same representations.
"""
from __future__ import annotations

from typing import Dict, List

from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox.ref import players as P
from prometheus.toolbox import state as ST


class SubstrateError(ValueError):
    pass


class FlatInProcessSubstrate:
    kind = "substrate.flat.v1"
    capabilities = frozenset({"core.substrate.v1", "ext.cost.v1", "ext.reference.v1"})

    def __init__(self):
        reps = {"statemachine.v1", "statemachine.v2", "constant.v1", "rewrite.v1"}
        if P.proteus_available():
            reps.add("proteus.tape.v0")
        self.representations = frozenset(reps)
        self._instances: List[object] = []

    def manifest(self) -> dict:
        return {"kind": self.kind, "representations": sorted(self.representations), "capabilities": sorted(self.capabilities)}

    def instantiate(self, spec: PlayerSpec, seed: int):
        if spec.representation not in self.representations:
            raise SubstrateError("%s cannot instantiate %r" % (self.kind, spec.representation))
        unmet = set(spec.requires) - self.capabilities
        if unmet:
            raise SubstrateError("player requires %s which %s does not offer" % (sorted(unmet), self.kind))
        if spec.representation == "statemachine.v1":
            inst = P.StateMachineInstance(spec)
        elif spec.representation == "statemachine.v2":
            inst = P.StateMachineV2Instance(spec, NoWorkspace())          # memoryless here: writes refused and counted
        elif spec.representation == "constant.v1":
            inst = P.ConstantInstance(spec)
        elif spec.representation == "rewrite.v1":
            inst = P.RewriteInstance(spec)
        else:
            inst = P.ProteusTapeInstance(spec, seed)
        self._instances.append(inst)
        return inst

    def accounting(self) -> Dict[str, int]:
        tot: Dict[str, int] = {}
        for inst in self._instances:
            for k, v in inst.cost().items():
                tot[k] = tot.get(k, 0) + int(v)
        tot["instances"] = len(self._instances)
        return tot


# ============================================================================================ workspaces (C6)
# A Workspace is what a Substrate hands a player instance: the ONLY door from a player to a StateDevice. The
# substrate decides scope, ttl, capacity and lag; the player sees read()/write() and pays per call.

class NoWorkspace:
    """The flat substrate's door: nothing behind it. Reads return None; writes are refused and counted."""

    def __init__(self):
        self._c = {"ws_reads": 0, "ws_writes": 0, "ws_refused": 0, "ws_appends": 0}

    def read(self):
        return None

    def write(self, value: int) -> None:
        self._c["ws_refused"] += 1

    def cost(self):
        return dict(self._c)

    def snapshot(self) -> bytes:
        import json
        return json.dumps(self._c).encode()

    def restore(self, snap: bytes) -> None:
        import json
        self._c = json.loads(snap.decode())


class KVWorkspace:
    def __init__(self, device, key: str, scope: str, ttl, player: int, on_read=None):
        self.dev = device; self.key = key; self.scope = scope; self.ttl = ttl; self.player = player; self.on_read = on_read
        self._c = {"ws_reads": 0, "ws_writes": 0, "ws_refused": 0, "ws_appends": 0}

    def read(self):
        self._c["ws_reads"] += 1
        v = self.dev.get(self.key, player=self.player)
        if self.on_read is not None:
            self.on_read(v)
        return v

    def write(self, value: int) -> None:
        before = self.dev.accounting()["refused"]
        self.dev.put(self.key, int(value), scope=self.scope, ttl=self.ttl, player=self.player)
        if self.dev.accounting()["refused"] > before:
            self._c["ws_refused"] += 1
        else:
            self._c["ws_writes"] += 1

    def cost(self):
        return dict(self._c)

    def snapshot(self) -> bytes:
        import json
        return json.dumps({"c": self._c, "dev": self.dev.snapshot().hex()}).encode()

    def restore(self, snap: bytes) -> None:
        import json
        d = json.loads(snap.decode()); self._c = d["c"]; self.dev.restore(bytes.fromhex(d["dev"]))


class StreamWorkspace(KVWorkspace):
    """Append-only door: read() returns the value appended `lag` appends ago (None until that many exist)."""

    def __init__(self, device, stream: str, scope: str, lag: int, maxlen: int, player: int, on_read=None):
        super().__init__(device, stream, scope, None, player, on_read=on_read); self.lag = max(1, int(lag)); self.maxlen = maxlen

    def read(self):
        self._c["ws_reads"] += 1
        recs = self.dev.read(self.key, since=0, player=self.player)
        v = recs[-self.lag][1][0] if len(recs) >= self.lag else None
        if self.on_read is not None:                        # C9: the hook must see stream reads too
            self.on_read(v)
        return v

    def write(self, value: int) -> None:
        rid = self.dev.append(self.key, (int(value),), scope=self.scope, maxlen=self.maxlen, player=self.player)
        if rid < 0:
            self._c["ws_refused"] += 1
        else:
            self._c["ws_appends"] += 1


class _WorkspaceSubstrate:
    """Shared machinery for substrates that grant a workspace backed by one InProcessStateDevice.
    Lifecycle hooks (ext.substrate.lifecycle.v1): episode_begin(ep, seed) ends the episode scope; tick(t)
    advances the device's logical clock (one clock across episodes so lifetime ttls are continuous)."""
    representations = frozenset({"statemachine.v2", "statemachine.v1", "constant.v1", "rewrite.v1"} | ({"proteus.tape.v0"} if P.proteus_available() else set()))

    def __init__(self, max_keys: int):
        self.dev = ST.InProcessStateDevice(max_keys=max_keys)
        self._instances: List[object] = []
        self._t = 0; self._episode = 0
        self._first_read_hits = 0                     # reads at the first tick of a later episode that found a value

    def _door(self, pid: int):
        raise NotImplementedError

    def instantiate(self, spec: PlayerSpec, seed: int):
        if spec.representation not in self.representations:
            raise SubstrateError("%s cannot instantiate %r" % (self.kind, spec.representation))
        unmet = set(spec.requires) - self.capabilities
        if unmet:
            raise SubstrateError("player requires %s which %s does not offer" % (sorted(unmet), self.kind))
        pid = len(self._instances)
        if spec.representation == "statemachine.v2":
            inst = P.StateMachineV2Instance(spec, self._door(pid))
        elif spec.representation == "statemachine.v1":
            inst = P.StateMachineInstance(spec)
        elif spec.representation == "constant.v1":
            inst = P.ConstantInstance(spec)
        elif spec.representation == "rewrite.v1":
            inst = P.RewriteInstance(spec)
        else:
            inst = P.ProteusTapeInstance(spec, seed)
        self._instances.append(inst)
        return inst

    def _on_read(self, v):
        if self._episode > 0 and self._tick_in_episode == 0 and v is not None:
            self._first_read_hits += 1

    def episode_begin(self, ep: int, seed: int) -> None:
        self._episode = ep; self._tick_in_episode = 0
        self.dev.end_scope("episode")

    def tick(self, t: int) -> None:
        self._t += 1; self._tick_in_episode = t + 1
        self.dev.advance(self._t)

    def events(self):
        return self.dev.events()

    def accounting(self) -> Dict[str, int]:
        tot: Dict[str, int] = {}
        for inst in self._instances:
            for k, v in inst.cost().items():
                tot[k] = tot.get(k, 0) + int(v)
        a = self.dev.accounting()
        tot.update({"instances": len(self._instances), "ws_expired": a["expired"], "ws_keys": a["keys"], "ws_discarded": a["discarded"]})
        return tot

    def science(self) -> dict:
        return {"carry_over": self._first_read_hits > 0, "first_tick_reads_with_value": self._first_read_hits}

    def manifest(self) -> dict:
        return {"kind": self.kind, "representations": sorted(self.representations), "capabilities": sorted(self.capabilities), "params": self.params}


class KVSubstrate(_WorkspaceSubstrate):
    kind = "substrate.kv.v1"
    capabilities = frozenset({"core.substrate.v1", "ext.workspace.kv.v1", "ext.substrate.lifecycle.v1", "ext.events.v1", "ext.cost.v1", "ext.state.ttl.v1"})

    def __init__(self, scope: str = "episode", ttl=None, max_keys: int = 4096):
        super().__init__(max_keys); self.params = {"scope": scope, "ttl": ttl, "max_keys": max_keys}
        if scope not in ST.SCOPES:
            raise SubstrateError("scope %r" % scope)

    def _door(self, pid: int):
        return KVWorkspace(self.dev, "p%d/mem" % pid, self.params["scope"], self.params["ttl"], pid, on_read=self._on_read)


class StreamSubstrate(_WorkspaceSubstrate):
    kind = "substrate.stream.v1"
    capabilities = frozenset({"core.substrate.v1", "ext.workspace.stream.v1", "ext.substrate.lifecycle.v1", "ext.events.v1", "ext.cost.v1", "ext.state.stream.v1"})

    def __init__(self, scope: str = "episode", lag: int = 1, maxlen: int = 64, max_keys: int = 4096):
        super().__init__(max_keys); self.params = {"scope": scope, "lag": lag, "maxlen": maxlen, "max_keys": max_keys}

    def _door(self, pid: int):
        return StreamWorkspace(self.dev, "p%d/log" % pid, self.params["scope"], self.params["lag"], self.params["maxlen"], pid, on_read=self._on_read)
