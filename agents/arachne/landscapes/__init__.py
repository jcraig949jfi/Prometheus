"""Landscape adapters. Each exposes:
    name: str
    available() -> bool
    seeds(rng, k) -> list[str]                       # namespaced node ids
    expand(node, rng, ruleset) -> list[(dst, op, null_p)]

Edges are operator-typed (the verb) with a null_p in [0,1] (high => a random
crawler would make this edge just as easily => cheap/generic).

ARACHNE-03 (2026-09-11): adapters fail LOUDLY. probe() returns
(available, reason) and build_landscapes() records every refusal in
LAST_REPORT instead of swallowing it. A run receipt copies LAST_REPORT so a
fabric can never again be read without knowing which landscapes answered.
"""
from __future__ import annotations

from typing import Dict, Tuple

LAST_REPORT: Dict[str, dict] = {}

ADAPTER_NAMES = ("mathlib", "lmfdb", "algolib", "oeis", "knots", "groups")


def _classes():
    from agents.arachne.landscapes.mathlib import MathlibLandscape
    from agents.arachne.landscapes.lmfdb import LmfdbLandscape
    from agents.arachne.landscapes.algolib import AlgolibLandscape
    from agents.arachne.landscapes.oeis import OeisLandscape
    from agents.arachne.landscapes.pgtable import KnotsLandscape, GroupsLandscape
    return (MathlibLandscape, LmfdbLandscape, AlgolibLandscape, OeisLandscape,
            KnotsLandscape, GroupsLandscape)


def probe(cls_or_inst) -> Tuple[object, bool, str]:
    """Instantiate (if a class) and ask available(); never raise. Returns
    (instance_or_None, available, reason). The reason is the adapter's own
    `unavailable_reason()` when it has one, else the _pg LAST_ERROR for its
    database, else the exception text."""
    from agents.arachne.landscapes import _pg
    name = getattr(cls_or_inst, "name", getattr(cls_or_inst, "__name__", "?"))
    try:
        inst = cls_or_inst() if isinstance(cls_or_inst, type) else cls_or_inst
    except Exception as e:  # noqa: BLE001
        return None, False, "construct failed: {}: {}".format(type(e).__name__, e)
    try:
        ok = bool(inst.available())
    except Exception as e:  # noqa: BLE001
        return inst, False, "available() raised: {}: {}".format(type(e).__name__, e)
    if ok:
        return inst, True, "ok"
    reason = None
    fn = getattr(inst, "unavailable_reason", None)
    if callable(fn):
        try:
            reason = fn()
        except Exception as e:  # noqa: BLE001
            reason = "unavailable_reason() raised: {}".format(e)
    if not reason:
        db = getattr(inst, "DB", None) or {"lmfdb": "lmfdb", "oeis": "prometheus_sci"}.get(name)
        reason = _pg.LAST_ERROR.get(db) if db else None
    return inst, False, reason or "available() returned False without a reason (adapter {})".format(name)


def build_landscapes_report() -> Dict[str, dict]:
    """name -> {available, reason, credential_source}. Never raises."""
    from agents.arachne.landscapes import _pg
    report: Dict[str, dict] = {}
    for cls in _classes():
        inst, ok, reason = probe(cls)
        name = getattr(cls, "name", cls.__name__)
        db = getattr(cls, "DB", None) or {"lmfdb": "lmfdb", "oeis": "prometheus_sci"}.get(name)
        report[name] = {"available": ok, "reason": reason,
                        "credential_source": _pg.RESOLUTION.get(db) if db else "n/a",
                        "_inst": inst}
    return report


def build_landscapes() -> dict:
    """Instantiate every adapter that can reach its data. Returns name->adapter
    for the available ones only; the refusals are in LAST_REPORT."""
    LAST_REPORT.clear()
    out = {}
    for name, row in build_landscapes_report().items():
        inst = row.pop("_inst")
        LAST_REPORT[name] = row
        if row["available"] and inst is not None:
            out[name] = inst
    return out
