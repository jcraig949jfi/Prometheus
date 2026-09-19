"""Capability model (WORLDS_KERNEL_DESIGN v0.2 s3). A capability is a versioned string id.

Components DECLARE the capabilities they provide; an Experiment DECLARES the ones it requires;
`negotiate()` compares them and returns a result object -- never an exception -- so a missing
optional capability blocks exactly one experiment and nothing else (operator directive s3, s32).

The CORE set is tiny and immutable within a major version. Everything else is an extension id;
unknown extension ids are permitted (a component may provide something the kernel has not
catalogued) and are reported as UNCATALOGUED in the negotiation so a receipt can show them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Iterable

CORE = frozenset({
    "core.world.v1",        # reset / observe / legal_actions / step / trace_hash
    "core.player.v1",       # PlayerSpec: representation + initial_state, instantiated by a Substrate
    "core.substrate.v1",    # instantiate / act / cost / fingerprint
    "core.experiment.v1",   # the Experiment IR schema
    "core.receipt.v1",      # the Receipt schema
})

# Catalogued extensions. The catalogue is documentation and a spelling check; it is NOT a gate.
EXTENSIONS = {
    "ext.snapshot.v1":            "world.snapshot() / world.restore(snapshot)",
    "ext.events.v1":              "world.events() drains compact (tick, kind, player, key, value) tuples",
    "ext.legal_actions.v1":       "world.legal_actions(player_id) describes the action space",
    "ext.multiplayer.v1":         "n_players > 1 sharing one world state",
    "ext.continuous_actions.v1":  "float-valued actions (Physics2D); canonical interchange is fixed-point",
    "ext.intervention.observation_delay.v1": "kernel-applied observation delay wrapper",
    "ext.intervention.observation_permute.v1": "kernel-applied seeded channel permutation",
    "ext.intervention.world_params.v1": "world accepts parameter overrides at construction",
    "ext.workspace.kv.v1":        "substrate exposes workspace.read/write to the player",
    "ext.workspace.stream.v1":    "substrate exposes append/read on a stream",
    "ext.workspace.graph.v1":     "substrate exposes link/neighbours",
    "ext.workspace.tensor.v1":    "substrate exposes dense/sparse tensor ops (cost-accounted)",
    "ext.workspace.executable.v1": "substrate exposes artifact create/invoke",
    "ext.state.ttl.v1":           "state device supports ttl-bound and scoped keys",
    "ext.state.stream.v1":        "state device supports append-only streams",
    "ext.physics2d.v1":           "rigid bodies, collisions, joints, sensors, contact events, headless step",
    "ext.message_bus.v1":         "inter-player channels",
    "ext.cost.v1":                "component reports raw accounting per run",
    "ext.replay.bit.v1":          "two runs with equal seeds produce equal trace hashes",
    "ext.replay.semantic.v1":     "agreement under a tolerance declared before execution",
    "ext.reference.v1":           "component is the reference implementation of its kind",
}

STATUS_OK = "OK"
STATUS_BLOCKED = "BLOCKED_MISSING_CAPABILITY"


def is_core(cap: str) -> bool:
    return cap in CORE


def well_formed(cap: str) -> bool:
    parts = cap.split(".")
    return len(parts) >= 3 and parts[0] in ("core", "ext") and parts[-1].startswith("v") and parts[-1][1:].isdigit()


@dataclass(frozen=True)
class Negotiation:
    status: str
    required: FrozenSet[str]
    provided: FrozenSet[str]
    missing: FrozenSet[str]
    uncatalogued: FrozenSet[str]
    malformed: FrozenSet[str] = field(default_factory=frozenset)

    @property
    def ok(self) -> bool:
        return self.status == STATUS_OK

    def as_dict(self) -> dict:
        return {"status": self.status, "required": sorted(self.required), "provided": sorted(self.provided),
                "missing": sorted(self.missing), "uncatalogued": sorted(self.uncatalogued), "malformed": sorted(self.malformed)}


def negotiate(required: Iterable[str], provided: Iterable[str]) -> Negotiation:
    req = frozenset(required); prov = frozenset(provided)
    malformed = frozenset(c for c in req | prov if not well_formed(c))
    missing = frozenset(c for c in req if c not in prov)
    uncat = frozenset(c for c in req | prov if c not in CORE and c not in EXTENSIONS)
    status = STATUS_OK if not missing and not malformed else STATUS_BLOCKED
    return Negotiation(status, req, prov, missing, uncat, malformed)


def union(*sets: Iterable[str]) -> FrozenSet[str]:
    out = set()
    for s in sets:
        out |= set(s)
    return frozenset(out)
