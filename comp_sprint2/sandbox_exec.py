"""Strict AST-validated Python sandbox for offline executable algorithm artifacts (`AlgoArtifact`).

Every evolved offline algorithm pass (`AlgoPass`) is:
  1. Statically AST-validated BEFORE compilation (forbids imports, dunder attribute traversal,
     file/OS/network access, eval/exec/open/getattr/setattr/globals/locals).
  2. Content-addressed by SHA-256 (`AlgoArtifact.sha256()`) and re-validated on load.
  3. Executed 100% OFFLINE (LLM unplugged) inside a clean whitelisted namespace under a
     strict wall-clock deadline (`deadline`), returning candidate solutions that MUST pass
     the track's independent exact verifier (`verify_fn`) and strictly reduce primitive cost
     (`cost_fn(cand) < cost_fn(best)`) before acceptance (strictly monotonic, zero regressions!).
"""
from __future__ import annotations

import ast
import collections
import hashlib
import heapq
import itertools
import json
import math
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


_FORBIDDEN_CALL_NAMES = frozenset({
    "eval", "exec", "compile", "open", "__import__", "input",
    "getattr", "setattr", "delattr", "hasattr", "vars", "dir",
    "globals", "locals", "breakpoint", "memoryview", "type", "object",
    "super", "classmethod", "staticmethod", "property",
})

_SAFE_BUILTINS: Dict[str, Any] = {
    "abs": abs,
    "all": all,
    "any": any,
    "bin": bin,
    "bool": bool,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "frozenset": frozenset,
    "hex": hex,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
    "ValueError": ValueError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "StopIteration": StopIteration,
    "RuntimeError": RuntimeError,
    "ZeroDivisionError": ZeroDivisionError,
}

_SAFE_STDLIB: Dict[str, Any] = {
    "math": math,
    "itertools": itertools,
    "collections": collections,
    "Counter": collections.Counter,
    "defaultdict": collections.defaultdict,
    "deque": collections.deque,
    "heapq": heapq,
    "random": random,
    "time": time,
}


def validate_algo_source(source: str, expected_fn: str = "optimize", max_chars: int = 16000) -> ast.Module:
    """Strictly validate an evolved Python algorithm pass before compilation."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Algorithm source must be a non-empty string")
    if len(source) > max_chars:
        raise ValueError(f"Algorithm source length {len(source)} exceeds max {max_chars}")

    try:
        tree = ast.parse(source, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"SyntaxError in algorithm source: {exc}") from exc

    found_fn = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("Imports are forbidden in sandboxed algorithm passes (use injected API/stdlib)")
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_"):
                raise ValueError(f"Access to private/dunder attribute {node.attr!r} is forbidden")
        if isinstance(node, ast.Name):
            if node.id.startswith("__"):
                raise ValueError(f"Access to dunder name {node.id!r} is forbidden")
            if node.id in _FORBIDDEN_CALL_NAMES:
                raise ValueError(f"Use of forbidden builtin {node.id!r} is disallowed")
        if isinstance(node, ast.FunctionDef) and node.name == expected_fn:
            found_fn = True

    if not found_fn:
        raise ValueError(f"Algorithm source must define top-level function `def {expected_fn}(...)`")
    return tree


@dataclass(frozen=True)
class AlgoPass:
    """One verified, AST-sandboxed executable offline optimization pass."""
    name: str
    track: str          # "S2A_XAG" | "S2B_BV"
    source: str         # Python source defining `def optimize(...)`
    sha256: str
    origin: str = "unknown"
    rationale: str = ""

    @classmethod
    def from_source(
        cls,
        name: str,
        track: str,
        source: str,
        origin: str = "unknown",
        rationale: str = "",
    ) -> "AlgoPass":
        clean = source.strip() + "\n"
        validate_algo_source(clean, expected_fn="optimize")
        payload = {"track": track, "source": clean}
        sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return cls(
            name=str(name),
            track=str(track),
            source=clean,
            sha256=sha,
            origin=str(origin),
            rationale=str(rationale)[:300],
        )

    def compile_fn(self, domain_api: Dict[str, Any]) -> Callable[..., Any]:
        tree = validate_algo_source(self.source, expected_fn="optimize")
        ns: Dict[str, Any] = {"__builtins__": dict(_SAFE_BUILTINS)}
        ns.update(_SAFE_STDLIB)
        ns.update(domain_api)
        code = compile(tree, filename=f"<algo_pass:{self.name}>", mode="exec")
        exec(code, ns, ns)
        fn = ns.get("optimize")
        if not callable(fn):
            raise ValueError(f"Pass {self.name!r} did not bind callable `optimize`")
        return fn


@dataclass(frozen=True)
class AlgoArtifact:
    """Content-addressed frozen offline executable algorithm artifact `S_mg`."""
    arm: str
    track: str
    generation: int
    passes: Tuple[AlgoPass, ...]
    parent_sha256: Optional[str] = None

    def sha256(self) -> str:
        payload = {
            "arm": self.arm,
            "track": self.track,
            "generation": self.generation,
            "parent_sha256": self.parent_sha256,
            "pass_shas": [p.sha256 for p in self.passes],
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        return hashlib.sha256(raw).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arm": self.arm,
            "track": self.track,
            "generation": self.generation,
            "parent_sha256": self.parent_sha256,
            "artifact_sha256": self.sha256(),
            "passes": [
                {
                    "name": p.name,
                    "track": p.track,
                    "source": p.source,
                    "sha256": p.sha256,
                    "origin": p.origin,
                    "rationale": p.rationale,
                }
                for p in self.passes
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlgoArtifact":
        passes: List[AlgoPass] = []
        for pd in data["passes"]:
            p = AlgoPass.from_source(
                name=str(pd["name"]),
                track=str(pd["track"]),
                source=str(pd["source"]),
                origin=str(pd.get("origin", "loaded")),
                rationale=str(pd.get("rationale", "")),
            )
            if "sha256" in pd and pd["sha256"] and p.sha256 != pd["sha256"]:
                raise ValueError(f"AlgoPass {p.name!r} SHA mismatch on load!")
            passes.append(p)
        art = cls(
            arm=str(data["arm"]),
            track=str(data["track"]),
            generation=int(data["generation"]),
            passes=tuple(passes),
            parent_sha256=data.get("parent_sha256"),
        )
        if "artifact_sha256" in data and art.sha256() != data["artifact_sha256"]:
            raise ValueError("AlgoArtifact SHA mismatch on load!")
        return art


def run_monotonic_pipeline(
    initial_solution: Any,
    passes: Sequence[AlgoPass],
    domain_api: Dict[str, Any],
    call_args_fn: Callable[[Any, float], Tuple[Any, ...]],
    verify_fn: Callable[[Any], bool],
    cost_fn: Callable[[Any], int],
    time_budget_sec: float,
) -> Tuple[Any, Dict[str, Any]]:
    """Run compiled `passes` monotonically over `initial_solution` within `time_budget_sec`.

    Guarantees:
      - Strictly monotonic: only accepts a pass output if `verify_fn(cand)` is True AND
        `cost_fn(cand) < cost_fn(best)`.
      - Isolates pass errors: exceptions/invalid outputs are logged and ignored (never corrupt `best`).
      - Respects shared `time_budget_sec` across all passes.
    """
    best = initial_solution
    best_cost = cost_fn(best)
    t_start = time.perf_counter()
    global_deadline = t_start + time_budget_sec
    n_passes = len(passes)
    pass_stats: List[Dict[str, Any]] = []

    for idx, p in enumerate(passes):
        now = time.perf_counter()
        if now >= global_deadline:
            break
        # Fair time slice: give remaining passes equal slice, allowing unused time to roll forward
        rem_passes = max(1, n_passes - idx)
        slice_deadline = min(global_deadline, now + (global_deadline - now) / rem_passes * 1.35)
        p_t0 = now
        status = "no_improve"
        err_msg = ""
        gain = 0
        try:
            fn = p.compile_fn(domain_api)
            args = call_args_fn(best, slice_deadline)
            cand = fn(*args)
            if cand is not None:
                c_cost = cost_fn(cand)
                if c_cost < best_cost:
                    if verify_fn(cand):
                        gain = best_cost - c_cost
                        best = cand
                        best_cost = c_cost
                        status = "improved"
                    else:
                        status = "rejected_unsound"
        except Exception as exc:
            status = "error"
            err_msg = f"{type(exc).__name__}: {str(exc)[:140]}"
        pass_stats.append({
            "name": p.name,
            "status": status,
            "gain": gain,
            "elapsed_ms": round((time.perf_counter() - p_t0) * 1000.0, 2),
            "error": err_msg,
        })

    return best, {
        "final_cost": best_cost,
        "elapsed_sec": round(time.perf_counter() - t_start, 4),
        "pass_stats": pass_stats,
    }
