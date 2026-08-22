"""DEGENERATE-INPUT AUDIT — seven of how many? (Cycle 040.)

Seven instances of one bug class turned up in three weeks, all in my own modules. From inside I
could not tell whether that is a habit of mine or simply where all bugs live, and an intuition
either way is worth nothing. This gets the denominator.

**Method, and its limits stated first.** A function is counted MEASURE-LIKE by a mechanical
criterion — it takes at least one argument and reduces to a scalar verdict (bool / int / float /
str / Optional thereof) — so the denominator is auditable rather than curated. Each is then
called with a DEGENERATE argument (empty collection) and with a MINIMAL LEGITIMATE one, and
classified by comparing the two answers:

    REFUSES        raised on the degenerate input — the honest response
    CONFLATES      returned the SAME answer for "nothing to measure" as for a real no-signal case
    DISTINGUISHES  returned something different for the two
    UNPROBED       arguments could not be constructed generically

`UNPROBED` is reported, never silently dropped. A rate computed over only the probeable functions
would flatter the result exactly the way cycle 038's hand-written fixtures did.
"""
from __future__ import annotations

import inspect
import typing
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

__all__ = ["MEASURE_MODULES", "AuditRow", "is_measure_like", "classify", "audit_modules",
           "REFUSES", "CONFLATES", "DISTINGUISHES", "UNPROBED"]

REFUSES = "REFUSES"
CONFLATES = "CONFLATES"
DISTINGUISHES = "DISTINGUISHES"
UNPROBED = "UNPROBED"

MEASURE_MODULES = (
    "prometheus_math.partition", "prometheus_math.battery", "prometheus_math.calibration",
    "prometheus_math.relative_claim", "prometheus_math.function_field",
    "techne.ladder_circuits.aliasing", "techne.ladder_circuits.sweep",
    "techne.ladder_circuits.stage_taxonomy", "techne.ladder_circuits.preprocessing_audit",
    "techne.ladder_circuits.composition", "techne.ladder_circuits.battery_chain",
)

_SCALAR = {"bool", "int", "float", "str"}


def is_measure_like(fn: Callable) -> bool:
    """Mechanical: takes at least one argument and reduces to a scalar verdict.

    Deliberately not curated. A criterion I choose per function is a criterion I can bend, which
    is the cycle-038 lesson; this one is applied uniformly and can be disagreed with in one place.
    """
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    params = [p for p in sig.parameters.values()
              if p.kind not in (p.VAR_KEYWORD,) and p.name != "self"]
    if not params:
        return False
    ann = sig.return_annotation
    if ann is inspect.Signature.empty:
        return False
    text = ann if isinstance(ann, str) else getattr(ann, "__name__", str(ann))
    text = str(text)
    if "Measurement" in text:
        # **A migrated measure is still a measure.** Without this line the cycle-041 migration
        # made functions vanish from this audit's population: the return annotation stops being
        # `int` and no longer matches, so the site leaves the denominator instead of leaving the
        # CONFLATES bucket. The rate would then improve because the population shrank, which is
        # the shape of confound that flatters a gate rather than passing it. Found by converting
        # one function and watching `test_THE_DENOMINATOR_IS_FORTY` fail.
        return True
    if any(s in text for s in _SCALAR):
        return True
    return "Optional" in text


def _degenerate_and_minimal(fn: Callable) -> Optional[Tuple[tuple, tuple]]:
    """Build (degenerate_args, minimal_args) generically, or None if it cannot be done.

    Degenerate = every positional gets an empty collection / zero. Minimal = a smallest
    legitimate value of the same shape. Crude on purpose: a bespoke pair per function would be
    the author choosing the test again.
    """
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return None
    deg: List[Any] = []
    minimal: List[Any] = []
    for p in sig.parameters.values():
        if p.name == "self" or p.kind is p.VAR_KEYWORD:
            continue
        if p.default is not inspect.Parameter.empty:
            continue                       # optional: leave to the default
        ann = str(p.annotation)
        if "Callable" in ann:
            deg.append(lambda *a, **k: 0)
            minimal.append(lambda *a, **k: 0)
        elif "int" in ann and "Sequence" not in ann and "List" not in ann:
            deg.append(0)
            minimal.append(2)
        elif "float" in ann:
            deg.append(0.0)
            minimal.append(0.5)
        elif "str" in ann:
            deg.append("")
            minimal.append("x")
        else:
            deg.append(())
            minimal.append((frozenset([0]),))
    if not deg:
        return None
    return tuple(deg), tuple(minimal)


@dataclass(frozen=True)
class AuditRow:
    module: str
    name: str
    verdict: str
    detail: str = ""


def classify(fn: Callable, name: str, module: str) -> AuditRow:
    """Call with a degenerate input and a minimal legitimate one, and compare."""
    pair = _degenerate_and_minimal(fn)
    if pair is None:
        return AuditRow(module, name, UNPROBED, "no generic arguments")
    deg_args, min_args = pair

    try:
        deg = fn(*deg_args)
    except Exception as exc:
        return AuditRow(module, name, REFUSES, type(exc).__name__)

    # A migrated measure refuses by RETURNING `OUT_OF_DOMAIN`, not by raising. Reading that as an
    # answer would score the repaired form worse than the broken one it replaced.
    if getattr(deg, "status", None) == "OUT_OF_DOMAIN":
        return AuditRow(module, name, REFUSES, f"Measurement({deg.reason[:60]})")

    try:
        mini = fn(*min_args)
    except Exception:
        return AuditRow(module, name, UNPROBED,
                        "answered on degenerate input but the minimal case could not be built")

    try:
        same = bool(deg == mini)
    except Exception:
        return AuditRow(module, name, UNPROBED, "results not comparable")
    return AuditRow(module, name, CONFLATES if same else DISTINGUISHES,
                    f"degenerate={deg!r} minimal={mini!r}"[:120])


def audit_modules(modules: Tuple[str, ...] = MEASURE_MODULES) -> List[AuditRow]:
    import importlib

    rows: List[AuditRow] = []
    for mn in modules:
        m = importlib.import_module(mn)
        names = getattr(m, "__all__", None) or [n for n in dir(m) if not n.startswith("_")]
        for n in names:
            o = getattr(m, n, None)
            if inspect.isfunction(o) and o.__module__ == mn and is_measure_like(o):
                rows.append(classify(o, n, mn.split(".")[-1]))
    return rows
