"""Component registry (WORLDS_KERNEL_DESIGN v0.2 s5, s19). A registry ROW is data; a component is
UNAVAILABLE until its row exists and its admission predicate has passed (admission.py). The IR
refers to components by `kind`; the registry turns a kind + params into an object at lowering time.

Rows are also emitted into every receipt so the evidence names the exact implementations used.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, FrozenSet, Optional

SLOTS = ("world", "substrate", "representation", "observer", "objective", "control", "transform", "selector", "state_device", "compute_device")
STATES = ("ADMITTED", "PROVISIONAL", "UNAVAILABLE", "RETIRED")


@dataclass
class ComponentRecord:
    kind: str
    slot: str
    factory: Callable[..., Any]
    capabilities: FrozenSet[str] = frozenset()      # provided
    requires: FrozenSet[str] = frozenset()          # needed from other slots (e.g. a representation needs workspace.kv)
    reference_of: Optional[str] = None              # this is the reference implementation of <kind family>
    route: str = "write"                            # write | wrap | bind | chop
    provenance: Dict[str, Any] = field(default_factory=dict)   # author seat, fossil/organ id, source path
    license: str = "UNSPECIFIED"
    native_deps: tuple = ()
    state: str = "PROVISIONAL"
    admission: Dict[str, Any] = field(default_factory=dict)    # last admission result, by host

    def row(self) -> dict:
        return {"kind": self.kind, "slot": self.slot, "capabilities": sorted(self.capabilities), "requires": sorted(self.requires),
                "reference_of": self.reference_of, "route": self.route, "provenance": self.provenance, "license": self.license,
                "native_deps": list(self.native_deps), "state": self.state}


class Registry:
    def __init__(self):
        self._rows: Dict[str, ComponentRecord] = {}

    def register(self, rec: ComponentRecord) -> ComponentRecord:
        if rec.slot not in SLOTS:
            raise ValueError("unknown slot %r" % rec.slot)
        self._rows[rec.kind] = rec
        return rec

    def get(self, kind: str) -> ComponentRecord:
        try:
            return self._rows[kind]
        except KeyError:
            raise KeyError("no component registered as %r" % kind)

    def has(self, kind: str) -> bool:
        return kind in self._rows

    def make(self, kind: str, **params) -> Any:
        rec = self.get(kind)
        if rec.state == "UNAVAILABLE":
            raise UnavailableComponent(kind, rec.admission)
        return rec.factory(**params)

    def rows(self, slot: Optional[str] = None) -> list:
        return [r.row() for r in self._rows.values() if slot is None or r.slot == slot]

    def kinds(self, slot: str) -> list:
        return sorted(k for k, r in self._rows.items() if r.slot == slot)

    def fork(self) -> "Registry":
        """An independent copy (C62): tests and experiments that register their own components must never mutate the
        process-global default registry -- a test-only UNAVAILABLE row leaked into the admission census by ordering."""
        import copy
        r = Registry(); r._rows = {k: copy.copy(v) for k, v in self._rows.items()}
        return r

    def provided_capabilities(self, *kinds: str) -> FrozenSet[str]:
        out = set()
        for k in kinds:
            out |= set(self.get(k).capabilities)
        return frozenset(out)


class UnavailableComponent(RuntimeError):
    def __init__(self, kind: str, admission: dict):
        super().__init__("component %s is UNAVAILABLE: %s" % (kind, admission.get("failed", "no admission record")))
        self.kind = kind
        self.admission = admission


_DEFAULT: Optional[Registry] = None


def default_registry() -> Registry:
    """The kernel's registry with the reference implementations loaded. Built once per process."""
    global _DEFAULT
    if _DEFAULT is None:
        from prometheus.toolbox.ref import install
        _DEFAULT = Registry()
        install(_DEFAULT)
    return _DEFAULT
