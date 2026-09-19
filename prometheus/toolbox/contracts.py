"""The immutable core contracts (WORLDS_KERNEL_DESIGN v0.2 s2, s10, s12). Protocols only; no behaviour.

Hot-path rule (inherited from NPE's contract.py): observations, actions, events and state are
integers, integer lists or bytes. Strings live in manifests and receipts.

    World       core.world.v1      reset(seed) / observe(pid) / legal_actions(pid) / step(actions) / trace_hash()
                                   + ext.events.v1: events();  ext.snapshot.v1: snapshot()/restore()
    PlayerSpec  core.player.v1     data: representation id + payload + initial_state; never executes itself
    Substrate   core.substrate.v1  instantiate(spec) -> PlayerInstance; declares the affordances a player sees
    PlayerInstance                 act(obs, legal) -> actions; adapt(signal); cost(); fingerprint(); snapshot/restore
    Observer                       begin(ctx) / on_tick(tick, world, actions) / on_events(events) / measure() / describe()
    Intervention                   data: world parameter overrides + kernel wrappers; applied by the kernel, never by a player
    Objective                      evaluate(receipt_like) -> {"value": number, "components": {...}}; reads, never writes
    Control                        arm(experiment) -> experiment (a variant) + expectation(primary_receipt, arm_receipt) -> outcome
    Transform                      accepts(kind) / apply(obj, rng) -> obj  (declares the object kinds it accepts)
    Selector                       propose(archive_rows, rng) -> [PlayerSpec]; ingest(receipts) -> rows  (archive is rows)

Every component also carries:  kind (registry id), manifest() -> dict (content identity), capabilities (frozenset).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Protocol, Tuple, runtime_checkable

# --- events (ext.events.v1) ---------------------------------------------------------------------------
# A compact event is a 5-tuple: (tick:int, kind:int, player:int, key:int, value:int). Kinds are small ints so
# an event stream is an int array on every device; names exist for receipts and observers.
EVENT_KINDS: Tuple[str, ...] = (
    "STATE_READ", "STATE_WRITE", "ACTION", "MESSAGE", "TRANSFER", "RESOURCE_CHANGE", "CONTACT",
    "ARTIFACT_CREATE", "ARTIFACT_INVOKE", "SNAPSHOT", "BRANCH", "TASK_CHANGE", "ABSORBED", "YIELD",
)
EVENT_ID: Dict[str, int] = {k: i for i, k in enumerate(EVENT_KINDS)}
Event = Tuple[int, int, int, int, int]

REPLAY_CLASSES = ("BIT", "SEMANTIC", "PARTIAL", "NONDETERMINISTIC")


@dataclass(frozen=True)
class ActionSpace:
    """What a player may emit this tick: `width` integers each in [0, `range`)."""
    width: int
    range: int


@dataclass(frozen=True)
class PlayerSpec:
    """core.player.v1: the executable candidate SPECIFICATION. It never runs itself."""
    representation: str                 # registry id of the representation, e.g. "statemachine.v1"
    payload: Dict[str, Any]             # the program / table / manifest, JSON-serialisable
    initial_state: Dict[str, Any] = field(default_factory=dict)
    requires: FrozenSet[str] = frozenset()   # substrate capabilities this representation needs
    meta: Dict[str, Any] = field(default_factory=dict)   # provenance: parent, seed, generator

    def manifest(self) -> dict:
        return {"representation": self.representation, "payload": self.payload,
                "initial_state": self.initial_state, "requires": sorted(self.requires), "meta": self.meta}


@dataclass(frozen=True)
class Intervention:
    """Changes experimental CONDITIONS (never evaluates anything). Two parts, both data:
    `world_params` are overrides the world accepts at construction (ext.intervention.world_params.v1);
    `wrappers` are kernel-applied observation/action wrappers keyed by capability id."""
    name: str
    world_params: Dict[str, Any] = field(default_factory=dict)
    wrappers: Dict[str, Any] = field(default_factory=dict)   # e.g. {"observation_delay": 3, "observation_permute": 1}

    def manifest(self) -> dict:
        return {"name": self.name, "world_params": self.world_params, "wrappers": self.wrappers}

    def requires(self) -> FrozenSet[str]:
        out = set()
        if self.world_params:
            out.add("ext.intervention.world_params.v1")
        for k in self.wrappers:
            out.add("ext.intervention.%s.v1" % k)
        return frozenset(out)


@runtime_checkable
class World(Protocol):
    kind: str
    capabilities: FrozenSet[str]
    n_players: int

    def manifest(self) -> dict: ...
    def reset(self, seed: int) -> None: ...
    def observe(self, player_id: int) -> List[int]: ...
    def legal_actions(self, player_id: int) -> ActionSpace: ...
    def step(self, actions: Dict[int, List[int]]) -> bool: ...
    def trace_hash(self) -> str: ...
    # ext.events.v1
    def events(self) -> List[Event]: ...
    # ext.snapshot.v1
    def snapshot(self) -> bytes: ...
    def restore(self, snapshot: bytes) -> None: ...


@runtime_checkable
class PlayerInstance(Protocol):
    def act(self, obs: List[int], legal: ActionSpace) -> List[int]: ...
    def adapt(self, signal: List[int]) -> None: ...
    def cost(self) -> Dict[str, int]: ...
    def fingerprint(self) -> str: ...
    def snapshot(self) -> bytes: ...
    def restore(self, snapshot: bytes) -> None: ...


@runtime_checkable
class Substrate(Protocol):
    kind: str
    capabilities: FrozenSet[str]          # what THIS machine offers to players (workspace.*, tensor.*)
    representations: FrozenSet[str]       # PlayerSpec.representation ids it can instantiate

    def manifest(self) -> dict: ...
    def instantiate(self, spec: PlayerSpec, seed: int) -> PlayerInstance: ...
    def accounting(self) -> Dict[str, int]: ...


@runtime_checkable
class Observer(Protocol):
    kind: str
    version: str

    def manifest(self) -> dict: ...
    def begin(self, ctx: dict) -> None: ...
    def on_tick(self, tick: int, observations: Dict[int, List[int]], actions: Dict[int, List[int]]) -> None: ...
    def on_events(self, events: List[Event]) -> None: ...
    def measure(self) -> Dict[str, Any]: ...
    def describe(self) -> List[int]: ...


@runtime_checkable
class Objective(Protocol):
    kind: str
    version: str

    def manifest(self) -> dict: ...
    def evaluate(self, receipt: dict) -> Dict[str, Any]: ...   # {"value": number, "components": {...}}


@runtime_checkable
class Control(Protocol):
    kind: str                     # positive | negative | sham | scratch | permutation | compute_matched | storage_matched | replay | ablation | transplant | cheat

    def manifest(self) -> dict: ...
    def arm(self, experiment: Any, rng_seed: int) -> Any: ...
    def expectation(self, primary: dict, arm: dict) -> dict: ...   # {"outcome": "MET"|"NOT_MET"|"INDETERMINATE", "detail": ...}


@runtime_checkable
class Transform(Protocol):
    kind: str
    accepts: FrozenSet[str]       # object kinds: "player.<representation>" | "world.<kind>" | "experiment"

    def manifest(self) -> dict: ...
    def apply(self, obj: Any, rng_seed: int) -> Any: ...


@runtime_checkable
class Selector(Protocol):
    kind: str

    def manifest(self) -> dict: ...
    def propose(self, archive_rows: List[dict], rng_seed: int, n: int) -> List[PlayerSpec]: ...
    def ingest(self, receipts: List[dict]) -> List[dict]: ...


def component_manifest_hash(manifest: dict) -> str:
    import hashlib, json
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]
