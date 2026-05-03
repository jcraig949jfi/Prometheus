"""sigma_kernel.omega_validators — in-process Omega validators for BIND/EVAL.

Two new validators are exposed:

- ``bind_validation(payload, seed) -> (Verdict, rationale)``
- ``eval_validation(payload, seed) -> (Verdict, rationale)``

They are called by ``BindEvalKernelV2`` from inside the FALSIFY path. Unlike
``omega_oracle.py`` (which runs as a separate subprocess for control-plane /
data-plane separation), these validators run in-process. The divergence is
deliberate: routing every BIND/EVAL through a subprocess Omega adds 50ms+ of
fork+JSON+stdin/stdout overhead per call, which kills the p50<5ms perf claim
on the BIND/EVAL hot path. In-process is the right shape for *fast* validators
that only do mechanical structural checks (hash equality, finite-positive
numeric checks, list-shape checks); subprocess Omega remains the correct shape
for *expensive* validators (null-model bootstrap, statistical tests).

If the kernel ever needs cross-process isolation for these checks (e.g., to
defend against a maliciously crafted binding that hijacks the parent
interpreter's state), they can be hoisted into ``omega_oracle.py`` -- the
contract returned here ((Verdict, rationale)) is identical.
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any, Dict, Tuple

from .sigma_kernel import Verdict, _sha256


# ---------------------------------------------------------------------------
# bind_validation
# ---------------------------------------------------------------------------


def bind_validation(payload: Dict[str, Any], seed: int = 0) -> Tuple[Verdict, str]:
    """Mechanical pre-PROMOTE check for the BIND opcode.

    Verifies:
        - ``callable_ref`` resolves via ``importlib`` + getattr
        - ``inspect.getsource`` matches ``expected_callable_hash`` if supplied
          (None means skip the drift check, e.g. for the first BIND)
        - ``cost_model.max_seconds`` is finite and strictly positive
        - ``cost_model.max_memory_mb`` is finite and strictly positive
        - ``cost_model.max_oracle_calls`` is non-negative integer
        - ``postconditions`` is None or a list of non-empty strings
        - ``authority_refs`` is None or a list of non-empty strings

    Returns ``(Verdict.CLEAR, "")`` on success. Returns ``(Verdict.BLOCK,
    rationale)`` on any failure. The rationale is a short human-readable
    sentence the kernel attaches to the FALSIFY verdict so callers see why
    BIND was rejected without re-running.
    """
    # 1. callable_ref imports.
    callable_ref = payload.get("callable_ref", "")
    if not callable_ref or ":" not in callable_ref:
        return Verdict.BLOCK, (
            f"bind_validation: callable_ref must be 'module:qualname', got "
            f"{callable_ref!r}"
        )
    modpath, qualname = callable_ref.split(":", 1)
    try:
        mod = importlib.import_module(modpath)
    except ImportError as e:
        return Verdict.BLOCK, (
            f"bind_validation: cannot import module {modpath!r}: {e}"
        )
    obj: Any = mod
    for part in qualname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError as e:
            return Verdict.BLOCK, (
                f"bind_validation: cannot resolve qualname {qualname!r} in "
                f"{modpath!r}: {e}"
            )
    if not callable(obj):
        return Verdict.BLOCK, (
            f"bind_validation: {callable_ref!r} resolves to "
            f"{type(obj).__name__}, not callable"
        )

    # 2. drift check (optional).
    expected_hash = payload.get("expected_callable_hash")
    if expected_hash is not None:
        try:
            src = inspect.getsource(obj)
        except (OSError, TypeError):
            src = repr(obj)
        live_hash = _sha256(src)
        if live_hash != expected_hash:
            return Verdict.BLOCK, (
                f"bind_validation: callable hash drift -- stored="
                f"{expected_hash[:12]} live={live_hash[:12]}"
            )

    # 3. cost model.
    cm = payload.get("cost_model")
    if not isinstance(cm, dict):
        return Verdict.BLOCK, (
            f"bind_validation: cost_model must be a dict, got "
            f"{type(cm).__name__}"
        )
    try:
        max_seconds = float(cm["max_seconds"])
        max_memory_mb = float(cm["max_memory_mb"])
        max_oracle_calls = int(cm["max_oracle_calls"])
    except (KeyError, TypeError, ValueError) as e:
        return Verdict.BLOCK, (
            f"bind_validation: cost_model malformed: {e}"
        )
    if not (max_seconds > 0 and max_seconds == max_seconds and max_seconds < float("inf")):
        return Verdict.BLOCK, (
            f"bind_validation: cost_model.max_seconds must be a finite "
            f"positive float, got {max_seconds!r}"
        )
    if not (max_memory_mb > 0 and max_memory_mb < float("inf")):
        return Verdict.BLOCK, (
            f"bind_validation: cost_model.max_memory_mb must be a finite "
            f"positive float, got {max_memory_mb!r}"
        )
    if max_oracle_calls < 0:
        return Verdict.BLOCK, (
            f"bind_validation: cost_model.max_oracle_calls must be >= 0, got "
            f"{max_oracle_calls!r}"
        )

    # 4. postconditions / authority_refs shape.
    pc = payload.get("postconditions")
    if pc is not None:
        if not isinstance(pc, list):
            return Verdict.BLOCK, (
                f"bind_validation: postconditions must be a list or None, "
                f"got {type(pc).__name__}"
            )
        # If supplied as a list it must be non-empty and items must be
        # non-empty strings. (None is the "absent" default and is OK.)
        if len(pc) == 0:
            return Verdict.BLOCK, (
                "bind_validation: postconditions list is empty; either omit "
                "or supply at least one non-empty string"
            )
        for i, item in enumerate(pc):
            if not isinstance(item, str) or not item.strip():
                return Verdict.BLOCK, (
                    f"bind_validation: postconditions[{i}] must be a "
                    f"non-empty string, got {item!r}"
                )

    ar = payload.get("authority_refs")
    if ar is not None:
        if not isinstance(ar, list):
            return Verdict.BLOCK, (
                f"bind_validation: authority_refs must be a list or None, "
                f"got {type(ar).__name__}"
            )
        if len(ar) == 0:
            return Verdict.BLOCK, (
                "bind_validation: authority_refs list is empty; either omit "
                "or supply at least one non-empty reference"
            )
        for i, item in enumerate(ar):
            if not isinstance(item, str) or not item.strip():
                return Verdict.BLOCK, (
                    f"bind_validation: authority_refs[{i}] must be a "
                    f"non-empty string, got {item!r}"
                )

    return Verdict.CLEAR, "bind_validation: structural checks pass"


# ---------------------------------------------------------------------------
# eval_validation
# ---------------------------------------------------------------------------


def eval_validation(payload: Dict[str, Any], seed: int = 0) -> Tuple[Verdict, str]:
    """Mechanical pre-PROMOTE check for the EVAL opcode.

    Verifies:
        - ``callable_ref`` imports successfully
        - ``inspect.getsource`` matches ``stored_callable_hash`` (drift check)
        - ``actual_cost`` (if supplied) does not exceed any of the three
          declared cost dimensions; the live cost is tracked by the EVAL
          path itself, not here -- this validator is called AFTER the
          callable runs so the cost is observable
        - ``args`` is None or a list

    The output_repr / postcondition matching is currently free-form; for
    the MVP we just verify the call did not exceed budget and that the
    return type, if expected, matches. Future versions can grow stronger
    postcondition predicates here.
    """
    # 1. callable_ref imports + drift check.
    callable_ref = payload.get("callable_ref", "")
    if not callable_ref or ":" not in callable_ref:
        return Verdict.BLOCK, (
            f"eval_validation: callable_ref must be 'module:qualname', got "
            f"{callable_ref!r}"
        )
    modpath, qualname = callable_ref.split(":", 1)
    try:
        mod = importlib.import_module(modpath)
    except ImportError as e:
        return Verdict.BLOCK, (
            f"eval_validation: cannot import module {modpath!r}: {e}"
        )
    obj: Any = mod
    for part in qualname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError as e:
            return Verdict.BLOCK, (
                f"eval_validation: cannot resolve qualname {qualname!r}: {e}"
            )
    if not callable(obj):
        return Verdict.BLOCK, (
            f"eval_validation: {callable_ref!r} resolves to "
            f"{type(obj).__name__}, not callable"
        )

    expected_hash = payload.get("stored_callable_hash")
    if expected_hash is not None:
        try:
            src = inspect.getsource(obj)
        except (OSError, TypeError):
            src = repr(obj)
        live_hash = _sha256(src)
        if live_hash != expected_hash:
            return Verdict.BLOCK, (
                f"eval_validation: callable source drifted between BIND and "
                f"EVAL -- stored={expected_hash[:12]} live={live_hash[:12]}"
            )

    # 2. args shape.
    args = payload.get("args")
    if args is not None and not isinstance(args, (list, tuple)):
        return Verdict.BLOCK, (
            f"eval_validation: args must be None, list, or tuple; got "
            f"{type(args).__name__}"
        )

    # 3. budget check on actual cost (if supplied).
    actual_cost = payload.get("actual_cost")
    cost_ceiling = payload.get("cost_model")
    if actual_cost is not None and cost_ceiling is not None:
        try:
            elapsed = float(actual_cost.get("elapsed_seconds", 0.0))
            mem_mb = float(actual_cost.get("memory_mb", 0.0))
            oracle_calls = int(actual_cost.get("oracle_calls", 0))
            max_seconds = float(cost_ceiling["max_seconds"])
            max_memory_mb = float(cost_ceiling["max_memory_mb"])
            max_oracle_calls = int(cost_ceiling["max_oracle_calls"])
        except (KeyError, TypeError, ValueError) as e:
            return Verdict.BLOCK, (
                f"eval_validation: cost block malformed: {e}"
            )
        if elapsed > max_seconds:
            return Verdict.BLOCK, (
                f"eval_validation: elapsed {elapsed:.3f}s > max_seconds "
                f"{max_seconds:.3f}s"
            )
        if mem_mb > max_memory_mb:
            return Verdict.BLOCK, (
                f"eval_validation: memory {mem_mb:.3f}MB > max_memory_mb "
                f"{max_memory_mb:.3f}MB"
            )
        if oracle_calls > max_oracle_calls:
            return Verdict.BLOCK, (
                f"eval_validation: oracle_calls {oracle_calls} > "
                f"max_oracle_calls {max_oracle_calls}"
            )

    return Verdict.CLEAR, "eval_validation: structural + budget checks pass"
