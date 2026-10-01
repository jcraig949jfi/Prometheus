"""(3) State and write-authority tracing: who wrote what, and difference is not use.

Three layers, cheapest first:

1. WriteLedger: an append-only log of write events an instrumented engine emits
   (t, unit, writer, node, component, source_class, value_digest). Queries: who_wrote (last writer at or
   before t), authority_map (writer distribution per component), foreign_writes (a node written by a
   context other than its owner: the NPE hijack / FF-31 case, Nestor B5).
2. Dynamic causes from a DiffRecord (DiffRecord.component_causes): for every component that STARTS to
   differ, the input class that could have written it (SENSED / TRANSPORTED / CARRIED / HOOK).
   check_authority() compares those causes against a DECLARED authority map, so an assumption encoded only
   in code ("w is written only from the sensor") becomes a fail-closed check.
3. difference_vs_use(): a component that DIFFERS between twins is only a carrier CANDIDATE. It is USED only
   if an intervention on it reaches the readout (explib.reach REACHED); it is DIFFERENT_UNUSED if that
   intervention is ABSORBED or NOT_REACHED; it is UNTESTED otherwise, and UNTESTED is never a carrier.
   (W-Y: "readout Kp differs 78-98%" was Kp[0], never read; W-S P3; W-T copies are not causal weight.)
"""
from __future__ import annotations

import dataclasses
from typing import Iterable, Optional

import numpy as np

from .outcomes import FAIL, NOT_VERIFIED, PASS, Check
from .reach import ABSORBED, NOT_CERTIFIED, NOT_REACHED, REACHED, UNAPPLIED
from .trace import DiffRecord

USED, DIFFERENT_UNUSED, UNTESTED, NOT_DIFFERENT, NOT_DECIDABLE = (
    "USED", "DIFFERENT_UNUSED", "UNTESTED", "NOT_DIFFERENT", "NOT_DECIDABLE")


# ----------------------------------------------------------------------------- 1 write ledger
@dataclasses.dataclass(frozen=True)
class WriteEvent:
    t: int
    unit: int
    writer: str            # the executing context (site id, actor id, hook name)
    node: int
    component: str
    source: str            # SENSED / TRANSPORTED / COMPUTED / IMMEDIATE / HOOK / ...
    owner: Optional[str] = None   # who owns the written node (code owner), if the engine has owners


class WriteLedger:
    def __init__(self, events: Iterable[WriteEvent] = ()):
        self.events: list[WriteEvent] = []
        for e in events:
            self.add(e)

    def add(self, e: WriteEvent) -> None:
        if self.events and e.t < self.events[-1].t:
            raise ValueError("ledger is append-only in time order")
        self.events.append(e)

    def who_wrote(self, unit: int, node: int, component: str, t: int) -> Optional[WriteEvent]:
        last = None
        for e in self.events:
            if e.t > t:
                break
            if e.unit == unit and e.node == node and e.component == component:
                last = e
        return last

    def authority_map(self) -> dict:
        out: dict = {}
        for e in self.events:
            d = out.setdefault(e.component, {})
            d[e.source] = d.get(e.source, 0) + 1
        return out

    def foreign_writes(self) -> list[WriteEvent]:
        """Writes whose executing context differs from the written node's owner (hijack / FF-31)."""
        return [e for e in self.events if e.owner is not None and e.writer != e.owner]


# ----------------------------------------------------------------------------- 2 declared authority
def check_authority(causes: dict, declared: dict) -> Check:
    """causes: DiffRecord.component_causes()['causes'] ({comp: {class_key: count}}).
    declared: {comp: set of allowed classes}; a '+'-joined key passes if ANY of its classes is allowed;
    a component absent from `declared` must never start to differ. UNEXPLAINED always fails."""
    bad = []
    for comp, d in causes.items():
        allowed = declared.get(comp, set())
        for key, n in d.items():
            ks = set(key.split("+"))
            if key == "UNEXPLAINED" or not (ks & set(allowed)):
                bad.append({"component": comp, "class": key, "count": n})
    return Check("declared_authority", FAIL if bad else PASS, {"violations": bad})


# ----------------------------------------------------------------------------- 3 difference vs use
def component_difference(rec: DiffRecord, comp: str, ro_tick, ro_node) -> np.ndarray:
    """[U] bool: component `comp` differs at the readout node at some tick <= the readout tick."""
    if rec.comp_held is None or comp not in rec.comp_held:
        raise KeyError(comp)
    ch = np.asarray(rec.comp_held[comp], bool)
    U = ch.shape[1]
    rt = np.asarray(ro_tick).reshape(U)
    rn = np.asarray(ro_node).reshape(U)
    return np.array([bool(ch[:rt[u] + 1, u, rn[u]].any()) for u in range(U)])


def difference_vs_use(diff_frac: dict, use_tests: dict) -> dict:
    """diff_frac: {comp: fraction of units where the component differs at the readout} (e.g. from
    component_difference on a twin record). use_tests: {comp: reach_certificate dict} from an intervention on
    that component at the readout node in the readout window. Returns {comp: {differs, use, reason}}.
    A difference without a REACHED intervention is never reported as USED."""
    out = {}
    for comp, f in diff_frac.items():
        r = use_tests.get(comp)
        if f == 0:
            use, why = NOT_DIFFERENT, "no twin difference at the readout"
        elif r is None:
            use, why = UNTESTED, "differs, but no intervention on it was run: NOT a carrier claim"
        else:
            v = r["verdict"]
            if v == REACHED:
                use, why = USED, "intervention changed the readout"
            elif v in (ABSORBED, NOT_REACHED):
                use, why = DIFFERENT_UNUSED, f"intervention {v}: present but unused"
            elif v == UNAPPLIED:
                use, why = NOT_DECIDABLE, "intervention was a no-op"
            elif v == NOT_CERTIFIED:
                use, why = NOT_DECIDABLE, "tracer not closed"
            else:
                use, why = NOT_DECIDABLE, v
        out[comp] = {"differs": float(f), "use": use, "reason": why}
    return out


def carrier_claims(dvu: dict) -> list[str]:
    """The only components that may be named as carriers."""
    return [c for c, v in dvu.items() if v["use"] == USED]
