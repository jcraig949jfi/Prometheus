"""Local executors. Deliberately tiny, and deliberately without defaults.

An executor is a pure function of its declared parameters. It MEASURES; it does
not hypothesize, does not choose the next experiment, and does not decide
whether its own number is interesting -- SFE's section 26 boundary, inherited
unchanged.

NO DEFAULTS. Not one `.get(key, fallback)` for anything a result depends on.
`_evaluate_bitstring` used to default `length` to 24, and since the engine
derives the hidden target from sha256("target:<seed_root>:<length>"), an
under-specified spec was silently scored against a Vivarium-chosen landscape.
Every parameter now comes from the spec or the run does not happen. The
contract is re-checked here as well as at validation, because an executor that
trusts its caller is one refactor away from defaulting again.
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import kinds as _kinds

REPO = Path(__file__).resolve().parent.parent.parent
_ENGINE = REPO / "SerendipityFoundry" / "SerendipityFoundryEngine"


class ExecutorUnavailable(RuntimeError):
    """The requested kind cannot be run faithfully on this host."""


class ExecutorNotImplemented(RuntimeError):
    """A registered kind whose executor does not live here.

    Not an error in the request: such a kind is admissible to the register on
    purpose. It is an error to have reached execution."""


def _params(kind_name: str, spec: dict) -> dict:
    """The declared parameters, contract-checked. Never widened, never filled."""
    work = spec.get("work") or {}
    payload = work.get("payload")
    kind = _kinds.get(kind_name)
    if kind is None:
        raise ExecutorUnavailable("no contract for kind %r" % kind_name)
    reasons = kind.check(payload)
    if reasons:
        raise ExecutorUnavailable("; ".join(reasons))
    return payload


def _noop_v0(spec: dict) -> dict:
    """Exercises the loop with no science in it. Takes no parameters, so there
    is nothing it could default."""
    _params("noop_v0", spec)
    return {"executed": True, "executor": "noop_v0",
            "reproducibility": "BIT_DETERMINISTIC"}


def _evaluate_bitstring(spec: dict) -> dict:
    if str(_ENGINE) not in sys.path:
        sys.path.insert(0, str(_ENGINE))
    try:
        from sfe.executors import BitStringExecutor, WorkPackage  # type: ignore
    except Exception as exc:              # noqa: BLE001
        raise ExecutorUnavailable(
            "evaluate_bitstring needs the engine reference executor "
            "(sfe.executors); refusing to score against a look-alike "
            "reimplementation: %s" % exc) from exc
    p = _params("evaluate_bitstring", spec)
    seed_root = spec["world"]["seed_root"]
    length = p["length"]
    if not isinstance(length, int) or isinstance(length, bool) or length <= 0:
        raise ExecutorUnavailable("length must be a positive integer, got %r"
                                  % (length,))
    ex = BitStringExecutor(length=length)
    wp = WorkPackage(work_id="viv", world_id="viv", kind=ex.kind,
                     payload={"bits": p["bits"]}, seed_root=seed_root)
    r = ex.execute(wp)
    if r.status != "COMPLETED":
        raise RuntimeError("executor failed: %s" % (r.error or "unspecified"))
    return {**r.result, "executor": ex.kind,
            "reproducibility": r.reproducibility}


_IMPL = {"noop_v0": _noop_v0, "evaluate_bitstring": _evaluate_bitstring}


def run(spec: dict) -> dict:
    """Execute the spec's declared kind against its declared parameters.

    Takes the SPEC, not a queue row and not an engine payload: everything an
    executor is entitled to see is in the sealed spec by construction.
    """
    kind_name = (spec.get("work") or {}).get("kind")
    kind = _kinds.get(kind_name)
    if kind is None:
        raise ExecutorUnavailable("no executor contract for kind %r"
                                  % (kind_name,))
    if not kind.implemented:
        raise ExecutorNotImplemented(
            "EXECUTOR_NOT_IMPLEMENTED: kind %r is registered (owner=%s) so it "
            "may be REGISTERED in the queue, but no executor for it lives "
            "here. This row was admitted as a candidate, not as a runnable "
            "experiment." % (kind_name, kind.owner))
    return _IMPL[kind_name](spec)
