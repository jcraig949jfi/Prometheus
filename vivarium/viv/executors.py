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


class WalkState:
    """The state a stateful kind carries between repeats. Reset creates a new
    one per repeat; persist reuses it. Nothing else in Vivarium is stateful."""

    __slots__ = ("position", "repeats")

    def __init__(self):
        self.position = 0.0
        self.repeats = 0

    def snapshot(self) -> dict:
        return {"position": self.position, "repeats": self.repeats}


def _random_walk_v0(spec: dict, *, seed: int, state) -> dict:
    """A deterministic 1-D walk. `steps` increments from the derived seed.

    Under repeat.state='reset' each repeat starts from position 0 and the
    repeats are independent draws. Under 'persist' the position carries, and
    the repeats are one trajectory -- which is the difference a lag-1
    within-world autocorrelation reads. That is the whole reason this kind
    exists; it makes no claim about anything."""
    import random as _random
    p = _params("random_walk_v0", spec)
    steps, scale = p["steps"], p["step_scale"]
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ExecutorUnavailable("steps must be a positive integer, got %r"
                                  % (steps,))
    if not isinstance(scale, (int, float)) or isinstance(scale, bool):
        raise ExecutorUnavailable("step_scale must be a number, got %r"
                                  % (scale,))
    if state is None:
        state = WalkState()
    start = state.position
    rng = _random.Random(seed)
    for _ in range(steps):
        state.position += scale * (rng.random() * 2.0 - 1.0)
    state.repeats += 1
    return {"position": state.position, "start_position": start,
            "displacement": state.position - start, "steps": steps,
            "step_scale": scale, "seed": seed,
            "executor": "random_walk_v0",
            "reproducibility": "BIT_DETERMINISTIC"}


def _noop_v0(spec: dict) -> dict:
    """Exercises the loop with no science in it. Takes no parameters, so there
    is nothing it could default."""
    _params("noop_v0", spec)
    return {"executed": True, "executor": "noop_v0",
            "reproducibility": "BIT_DETERMINISTIC"}


def _evaluate_bitstring(spec: dict, *, seed: int) -> dict:
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
    seed_root = seed          # the REPEAT's derived seed, not the world's
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


def new_state(kind_name: str):
    """A fresh state object for a stateful kind, or None."""
    kind = _kinds.get(kind_name)
    if kind is not None and kind.stateful:
        return WalkState() if kind_name == "random_walk_v0" else None
    return None


def run(spec: dict, *, seed: int = None, state=None) -> dict:
    """Execute the spec's declared kind against its declared parameters.

    Takes the SPEC, not a queue row and not an engine payload: everything an
    executor is entitled to see is in the sealed spec by construction.

    `seed` is the REPEAT's derived seed. It is passed rather than read from
    the spec because which seed this repeat gets is a declared derivation
    (repeat.seed_derivation) that the runner resolves -- an executor must not
    reinvent it, and must not silently fall back to the world seed.
    `state` is the carried state for a stateful kind under repeat.state.
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
    if seed is None:
        seed = spec["world"]["seed_root"]
    if kind_name == "noop_v0":
        return _noop_v0(spec)
    if kind_name == "evaluate_bitstring":
        return _evaluate_bitstring(spec, seed=seed)
    if kind_name == "random_walk_v0":
        return _random_walk_v0(spec, seed=seed, state=state)
    raise ExecutorUnavailable("no executor bound for kind %r" % (kind_name,))
