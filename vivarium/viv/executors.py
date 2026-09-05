"""Local executors. Deliberately tiny.

An executor is a pure function of the work payload. It MEASURES; it does not
hypothesize, does not choose the next experiment, and does not decide whether
its own number is interesting -- that boundary is SFE's section 26 and Vivarium
inherits it unchanged.

`evaluate_bitstring` delegates to the engine's own reference executor when the
engine source is importable, so the landscape a Vivarium run scores is the same
object the canary scores. On a host without the engine source, that kind is
simply unavailable and the experiment fails visibly rather than being scored
against a second, look-alike implementation.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parent.parent.parent
_ENGINE = REPO / "SerendipityFoundry" / "SerendipityFoundryEngine"


class ExecutorUnavailable(RuntimeError):
    """The requested kind cannot be run faithfully on this host."""


def _work_payload(payload: dict) -> dict:
    """The engine hands the executor `{exp_id, **spec}`; the executor's own
    arguments live at spec.work.payload."""
    work = payload.get("work") or {}
    return work.get("payload") or {}


def _noop_v0(payload: dict) -> dict:
    """Echo the declared payload with a deterministic marker. Exists so the
    whole queue -> SFE -> PEW loop is exercisable on any host, including one
    with no scientific executor installed."""
    inner = _work_payload(payload)
    return {"echo": inner, "executor": "noop_v0",
            "reproducibility": "BIT_DETERMINISTIC"}


def _evaluate_bitstring(payload: dict, *, seed_root: int) -> dict:
    if str(_ENGINE) not in sys.path:
        sys.path.insert(0, str(_ENGINE))
    try:
        from sfe.executors import BitStringExecutor, WorkPackage  # type: ignore
    except Exception as exc:              # noqa: BLE001
        raise ExecutorUnavailable(
            "evaluate_bitstring needs the engine reference executor "
            "(sfe.executors); refusing to score against a look-alike "
            "reimplementation: %s" % exc) from exc
    inner = _work_payload(payload)
    ex = BitStringExecutor(length=int(inner.get("length", 24)))
    wp = WorkPackage(work_id="viv", world_id="viv", kind=ex.kind,
                     payload=inner, seed_root=seed_root)
    r = ex.execute(wp)
    if r.status != "COMPLETED":
        raise RuntimeError("executor failed: %s" % (r.error or "unspecified"))
    return {**r.result, "executor": ex.kind,
            "reproducibility": r.reproducibility}


def run(kind: str, payload: dict, *, seed_root: int) -> dict:
    if kind == "noop_v0":
        return _noop_v0(payload)
    if kind == "evaluate_bitstring":
        return _evaluate_bitstring(payload, seed_root=seed_root)
    raise ExecutorUnavailable("no executor for kind %r" % kind)
