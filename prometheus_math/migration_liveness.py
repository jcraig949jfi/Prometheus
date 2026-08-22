"""MIGRATION LIVENESS — which refusals are actually reached, measured rather than judged.

Cycle 040 established the bug class at ten sites among forty measure-like functions. All ten now
refuse by RAISING. Converting them to return `Measurement` is the repair the type was built for,
but converting all ten at once would be the same mistake in a new coat: doing the work I can
imagine needing rather than the work something demonstrably needs.

So the slice gets picked by measurement. **A refusal is LIVE iff some code path actually reaches
it during a real run** — not iff I can construct an input that would. The operational test is
uniform across all ten, deliberately, because a criterion chosen per site is a criterion I can
bend (the cycle-038 lesson, restated in cycle 040):

    LIVE      the refusal fired at least once during a full run of the suite
    UNREACHED the refusal never fired

and each firing is attributed to its nearest caller frame, split into

    FROM_TEST  a test constructed the degenerate input on purpose
    FROM_PROD  a non-test caller reached it without meaning to

**The limit of this measurement, stated before its result.** The test suite is not the production
workload. A refusal marked UNREACHED is unreached *by the suite*, which is a lower bound on
liveness and not a proof of deadness — and FROM_TEST firings say only that I wrote the test, not
that the case occurs. This measures reachability under one workload; it does not measure need.
"""
from __future__ import annotations

import collections
import inspect
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

__all__ = ["TARGETS", "LivenessRecord", "install_probes", "REFUSAL_TYPES", "summarise"]

# The ten sites of the answering-outside-your-domain class, by (module, attribute, cycle found).
TARGETS: Tuple[Tuple[str, str, int], ...] = (
    ("prometheus_math.battery", "structural_constancy", 29),
    ("techne.ladder_circuits.aliasing", "find_aliasing_witness", 37),
    ("techne.ladder_circuits.aliasing", "fiber_search", 37),
    ("prometheus_math.partition", "refinement_multiplicity", 38),
    ("prometheus_math.calibration", "skill", 39),
    ("techne.ladder_circuits.aliasing", "verify_factorization", 39),
    ("techne.ladder_circuits.sweep", "uniform_adversary", 39),
    ("prometheus_math.partition", "is_refinement_chain", 40),
    ("prometheus_math.partition", "chain_direction", 40),
    ("techne.ladder_circuits.sweep", "find_splitting_witness", 40),
)

_HERE = str(pathlib.Path(__file__).resolve())


def _refusal_types() -> tuple:
    """The exception types the ten refuse with. Named, not caught-broadly: a bare `except
    Exception` would count ordinary bugs as refusals and inflate liveness."""
    types: List[type] = []
    try:
        from prometheus_math.partition import PartitionError
        types.append(PartitionError)
    except Exception:  # pragma: no cover
        pass
    try:
        from techne.ladder_circuits.aliasing import OutOfDomain
        types.append(OutOfDomain)
    except Exception:  # pragma: no cover
        pass
    try:
        from prometheus_math.measurement import MeasurementError
        types.append(MeasurementError)
    except Exception:  # pragma: no cover
        pass
    return tuple(types)


REFUSAL_TYPES = _refusal_types()


@dataclass
class LivenessRecord:
    calls: int = 0
    refusals: int = 0
    from_test: int = 0
    from_prod: int = 0
    frames: collections.Counter = field(default_factory=collections.Counter)

    @property
    def live(self) -> bool:
        return self.refusals > 0


def _nearest_caller() -> str:
    """First frame outside this module — the code that actually made the degenerate call.

    Walks `sys._getframe` rather than `inspect.stack()`. That is not a style preference: the
    first version of this probe used `inspect.stack()`, which reads and caches source context for
    every frame, and it turned a two-minute suite into something that had not finished in fifteen.
    A probe whose cost changes what it can observe is not a probe.
    """
    depth = 2
    while True:
        try:
            fr = sys._getframe(depth)
        except ValueError:
            return "<unknown>"
        name = fr.f_code.co_filename
        if name != _HERE:
            return f"{pathlib.Path(name).name}:{fr.f_lineno}"
        depth += 1


def install_probes(records: Dict[str, LivenessRecord]) -> None:
    """Wrap each target so calls and refusals are counted, re-raising so behaviour is unchanged.

    **`functools.wraps` here is load-bearing, and I know that because the first version omitted
    it and I claimed non-invasiveness anyway.** The bare wrapper carried
    `__module__ == "prometheus_math.migration_liveness"`, so cycle 040's `audit_modules` — which
    filters on `o.__module__ == mn` — silently dropped every probed function from its own
    denominator. Four tests failed, measured against a probe-off control on identical scope:

        PROBE-OFF   376 passed
        PROBE-ON    372 passed, 4 failed   (all four in test_degenerate_audit)

    The probe was perturbing the instrument that measures the thing the probe exists to measure.
    `wraps` copies `__module__`, `__name__` and `__wrapped__`, which restores the delta to zero.
    The docstring claim came first and the evidence second; that ordering is the mistake, and the
    control is what caught it.
    """
    import functools
    import importlib

    for mod_name, attr, _cycle in TARGETS:
        try:
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, attr)
        except Exception:  # pragma: no cover
            continue
        records.setdefault(attr, LivenessRecord())

        def make(fn: Callable, attr: str) -> Callable:
            @functools.wraps(fn)
            def probe(*a: Any, **k: Any) -> Any:
                rec = records[attr]
                rec.calls += 1
                try:
                    return fn(*a, **k)
                except REFUSAL_TYPES:
                    where = _nearest_caller()
                    rec.refusals += 1
                    rec.frames[where] += 1
                    if "test" in where:
                        rec.from_test += 1
                    else:
                        rec.from_prod += 1
                    raise
            return probe

        setattr(mod, attr, make(fn, attr))


def summarise(records: Dict[str, LivenessRecord]) -> List[str]:  # pragma: no cover - reporting
    out = []
    for _m, attr, cycle in TARGETS:
        r = records.get(attr, LivenessRecord())
        state = "LIVE" if r.live else "UNREACHED"
        out.append(f"{attr:26} c{cycle:03d}  calls={r.calls:5d}  refusals={r.refusals:3d}  "
                   f"test={r.from_test:3d} prod={r.from_prod:3d}  {state}")
    return out
