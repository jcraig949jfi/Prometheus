"""Sprint 3 Deterministic AST-Sandboxed Compositional Library Runtime (Laws 1 & 3).

Fixes Law 1 (Zero Wall-Clock Jitter) and Law 3 (Compositional Module Library):
  1. ZERO wall-clock access: `time` is completely removed from the sandbox. Every loop
     iteration (`for`, `while`, comprehensions) and every domain API call charges an
     exact integer cost to `OpBudget`. Identical artifact + task + seed = 0.000 variance.
  2. Un-swallowable global cap: `BudgetExhausted` inherits from `BaseException` so
     user `except Exception:` blocks cannot bypass the deterministic operation cap.
  3. Soft sub-budgets: `lib.run(fn_name, *args, op_cap=N, **kwargs)` allows the
     orchestrator or any module to allocate a deterministic sub-budget to a helper
     without starving later modules.
  4. True Compositional Library (`CompositionalAlgoArtifact`):
       - `modules`: ordered tuple of verified `LibModule`s tagged with `generation` (0..3).
       - `orchestrator`: `LibModule` defining `def solve(circ, n_inputs, targets, seed, api, lib, budget)`.
       - Modules in Gen k can directly call helpers crystallized in Gen 0..k-1 via `lib.<fn>(...)`.
       - Call-graph & cross-generation telemetry (`cross_gen_calls`, `gen_gate_drops`) is
         recorded automatically.
  5. Causal Knockouts: `knockout_generations(artifact, knocked_gens)` stubs out all
     functions from `knocked_gens` while preserving the orchestrator and other generations.
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
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple


class BudgetExhausted(BaseException):
    """Hard deterministic op-budget cap (BaseException so user `except Exception:` cannot swallow it)."""


class SubBudgetExhausted(Exception):
    """Soft sub-budget cap raised inside `lib.run(..., op_cap=...)`."""


class OpBudget:
    """Deterministic integer operation counter with stackable soft sub-limits."""

    def __init__(self, limit: int) -> None:
        self.limit: int = max(1, int(limit))
        self.spent: int = 0
        self._sub_limits: List[int] = []

    def remaining(self) -> int:
        rem = self.limit - self.spent
        if self._sub_limits:
            rem = min(rem, self._sub_limits[-1] - self.spent)
        return max(0, rem)

    def global_remaining(self) -> int:
        return max(0, self.limit - self.spent)

    def fraction_remaining(self) -> float:
        return self.remaining() / float(self.limit)

    def charge(self, ops: int = 1) -> None:
        if ops <= 0:
            return
        self.spent += ops
        if self.spent > self.limit:
            raise BudgetExhausted(f"Global op budget {self.limit} exhausted")
        if self._sub_limits and self.spent > self._sub_limits[-1]:
            raise SubBudgetExhausted(f"Sub-budget limit reached at spent={self.spent}")

    def push_sub_cap(self, op_cap: int) -> None:
        cap = max(1, int(op_cap))
        target = min(self.limit, self.spent + cap)
        if self._sub_limits:
            target = min(target, self._sub_limits[-1])
        self._sub_limits.append(target)

    def pop_sub_cap(self) -> None:
        if self._sub_limits:
            self._sub_limits.pop()


_FORBIDDEN_CALL_NAMES = frozenset({
    "eval", "exec", "compile", "open", "__import__", "input",
    "getattr", "setattr", "delattr", "hasattr", "vars", "dir",
    "globals", "locals", "breakpoint", "memoryview", "type", "object",
    "super", "classmethod", "staticmethod", "property",
    "BaseException", "BudgetExhausted", "_op_tick", "_op_iter",
})


def _make_safe_range(budget: OpBudget) -> Callable[..., range]:
    def _safe_range(*args: int) -> range:
        r = range(*args)
        if len(r) > 250_000:
            budget.charge(budget.limit + 1)
        return r
    return _safe_range


_SAFE_BUILTINS_BASE: Dict[str, Any] = {
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
    "Exception": Exception,
    "ValueError": ValueError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "StopIteration": StopIteration,
    "RuntimeError": RuntimeError,
    "ZeroDivisionError": ZeroDivisionError,
    "SubBudgetExhausted": SubBudgetExhausted,
}

# NOTE: `time` is intentionally EXCLUDED (Law 1: 100% deterministic op-budget execution!)
_SAFE_STDLIB: Dict[str, Any] = {
    "math": math,
    "itertools": itertools,
    "collections": collections,
    "Counter": collections.Counter,
    "defaultdict": collections.defaultdict,
    "deque": collections.deque,
    "heapq": heapq,
    "random": random,
}


def validate_module_source(
    source: str,
    required_fn: Optional[str] = None,
    max_chars: int = 18000,
) -> Tuple[ast.Module, List[str]]:
    """Strictly AST-validate a library module or orchestrator; return (tree, exported_fn_names)."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Module source must be a non-empty string")
    if len(source) > max_chars:
        raise ValueError(f"Module source length {len(source)} exceeds max {max_chars}")

    try:
        tree = ast.parse(source, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"SyntaxError in module source: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("Imports are forbidden in sandboxed modules (use injected api/lib/stdlib)")
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_"):
                raise ValueError(f"Access to private/dunder attribute {node.attr!r} is forbidden")
        if isinstance(node, ast.Name):
            if node.id.startswith("__"):
                raise ValueError(f"Access to dunder name {node.id!r} is forbidden")
            if node.id in _FORBIDDEN_CALL_NAMES:
                raise ValueError(f"Use of forbidden name {node.id!r} is disallowed")
        if isinstance(node, ast.ExceptHandler):
            # Disallow bare `except:` so `BudgetExhausted(BaseException)` can NEVER be caught!
            if node.type is None:
                raise ValueError("Bare `except:` is forbidden; use `except Exception:` instead")

    exported: List[str] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef) and not stmt.name.startswith("_"):
            exported.append(stmt.name)

    if required_fn is not None and required_fn not in exported:
        raise ValueError(f"Module must define top-level function `def {required_fn}(...)`")
    if not exported:
        raise ValueError("Module must define at least one public top-level function")
    return tree, exported


class _LoopBudgetInstrumenter(ast.NodeTransformer):
    """Inject `_op_tick()` into every `for`/`while` loop and wrap comprehension iterables."""

    def _tick_stmt(self) -> ast.Expr:
        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id="_op_tick", ctx=ast.Load()),
                args=[],
                keywords=[],
            )
        )

    def visit_For(self, node: ast.For) -> ast.AST:
        self.generic_visit(node)
        node.body.insert(0, self._tick_stmt())
        return node

    def visit_While(self, node: ast.While) -> ast.AST:
        self.generic_visit(node)
        node.body.insert(0, self._tick_stmt())
        return node

    def visit_comprehension(self, node: ast.comprehension) -> ast.AST:
        self.generic_visit(node)
        node.iter = ast.Call(
            func=ast.Name(id="_op_iter", ctx=ast.Load()),
            args=[node.iter],
            keywords=[],
        )
        return node


def _compile_instrumented(tree: ast.Module, filename: str) -> Any:
    inst_tree = _LoopBudgetInstrumenter().visit(tree)
    ast.fix_missing_locations(inst_tree)
    return compile(inst_tree, filename=filename, mode="exec")


@dataclass(frozen=True)
class LibModule:
    """One AST-validated, generation-tagged reusable Python module inside the library."""
    name: str
    generation: int
    source: str
    exported_fns: Tuple[str, ...]
    sha256: str
    origin: str = "unknown"
    rationale: str = ""

    @classmethod
    def from_source(
        cls,
        name: str,
        generation: int,
        source: str,
        required_fn: Optional[str] = None,
        origin: str = "unknown",
        rationale: str = "",
    ) -> "LibModule":
        clean = source.strip() + "\n"
        _, exported = validate_module_source(clean, required_fn=required_fn)
        payload = {"name": name, "generation": int(generation), "source": clean}
        sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return cls(
            name=str(name),
            generation=int(generation),
            source=clean,
            exported_fns=tuple(exported),
            sha256=sha,
            origin=str(origin),
            rationale=str(rationale)[:300],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "generation": self.generation,
            "source": self.source,
            "exported_fns": list(self.exported_fns),
            "sha256": self.sha256,
            "origin": self.origin,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], required_fn: Optional[str] = None) -> "LibModule":
        m = cls.from_source(
            name=str(data["name"]),
            generation=int(data["generation"]),
            source=str(data["source"]),
            required_fn=required_fn,
            origin=str(data.get("origin", "loaded")),
            rationale=str(data.get("rationale", "")),
        )
        if "sha256" in data and data["sha256"] and m.sha256 != data["sha256"]:
            raise ValueError(f"LibModule {m.name!r} SHA mismatch on load!")
        return m


@dataclass(frozen=True)
class CompositionalAlgoArtifact:
    """Content-addressed compositional offline algorithm artifact (`lib` + `orchestrator`)."""
    arm: str
    track: str
    generation: int
    modules: Tuple[LibModule, ...]
    orchestrator: LibModule
    parent_sha256: Optional[str] = None

    def sha256(self) -> str:
        payload = {
            "arm": self.arm,
            "track": self.track,
            "generation": self.generation,
            "parent_sha256": self.parent_sha256,
            "module_shas": [m.sha256 for m in self.modules],
            "orchestrator_sha": self.orchestrator.sha256,
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
            "modules": [m.to_dict() for m in self.modules],
            "orchestrator": self.orchestrator.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompositionalAlgoArtifact":
        mods = tuple(LibModule.from_dict(md) for md in data["modules"])
        orch = LibModule.from_dict(data["orchestrator"], required_fn="solve")
        art = cls(
            arm=str(data["arm"]),
            track=str(data["track"]),
            generation=int(data["generation"]),
            modules=mods,
            orchestrator=orch,
            parent_sha256=data.get("parent_sha256"),
        )
        if "artifact_sha256" in data and art.sha256() != data["artifact_sha256"]:
            raise ValueError("CompositionalAlgoArtifact SHA mismatch on load!")
        return art


def knockout_generations(
    artifact: CompositionalAlgoArtifact,
    knocked_gens: Set[int],
    arm_name: str,
) -> CompositionalAlgoArtifact:
    """Create a causal knockout artifact by stubbing out all modules from `knocked_gens`
    while keeping the exact orchestrator and surviving generations intact."""
    new_mods: List[LibModule] = []
    for m in artifact.modules:
        if m.generation in knocked_gens:
            stub_lines: List[str] = []
            for fn_name in m.exported_fns:
                stub_lines.append(
                    f"def {fn_name}(*args, **kwargs):\n"
                    f"    if args and isinstance(args[0], XAGCircuit):\n"
                    f"        return args[0]\n"
                    f"    return None\n"
                )
            stub_src = "\n".join(stub_lines)
            new_mods.append(
                LibModule.from_source(
                    name=f"{m.name}__knocked_out",
                    generation=m.generation,
                    source=stub_src,
                    origin=f"knockout_of_{m.name}",
                    rationale=f"Causal knockout stub for generation {m.generation}",
                )
            )
        else:
            new_mods.append(m)
    return CompositionalAlgoArtifact(
        arm=arm_name,
        track=artifact.track,
        generation=artifact.generation,
        modules=tuple(new_mods),
        orchestrator=artifact.orchestrator,
        parent_sha256=artifact.sha256(),
    )


class LibNamespace:
    """Shared compositional library handle exposing all registered module functions + call telemetry."""

    def __init__(self, budget: OpBudget, gen_stack: List[Tuple[str, int]]) -> None:
        self._budget = budget
        self._gen_stack = gen_stack
        self._fns: Dict[str, Callable[..., Any]] = {}
        self._fn_meta: Dict[str, Tuple[str, int]] = {}
        self.call_counts: Dict[str, int] = {}
        self.module_calls: Dict[str, int] = {}
        self.cross_gen_calls: Dict[str, int] = {}
        self.fn_errors: Dict[str, int] = {}
        self.fn_error_msgs: Dict[str, str] = {}

    def register(self, fn_name: str, fn: Callable[..., Any], mod_name: str, gen: int) -> None:
        self._fn_meta[fn_name] = (mod_name, gen)

        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            caller_mod, caller_gen = self._gen_stack[-1] if self._gen_stack else ("orchestrator", -1)
            self.call_counts[fn_name] = self.call_counts.get(fn_name, 0) + 1
            self.module_calls[mod_name] = self.module_calls.get(mod_name, 0) + 1
            if caller_mod != "orchestrator" and caller_mod != mod_name and caller_gen != gen:
                key = f"g{caller_gen}->g{gen}:{fn_name}"
                self.cross_gen_calls[key] = self.cross_gen_calls.get(key, 0) + 1
            self._gen_stack.append((mod_name, gen))
            try:
                return fn(*args, **kwargs)
            finally:
                self._gen_stack.pop()

        self._fns[fn_name] = _wrapped
        setattr(self, fn_name, _wrapped)

    def has(self, fn_name: str) -> bool:
        return fn_name in self._fns

    def list_fns(self) -> List[str]:
        return sorted(self._fns.keys())

    def run(self, fn_name: str, *args: Any, op_cap: Optional[int] = None, **kwargs: Any) -> Any:
        """Invoke `lib.<fn_name>(*args, **kwargs)` with an optional deterministic soft `op_cap`."""
        fn = self._fns.get(fn_name)
        if fn is None:
            return None
        if op_cap is not None:
            if self._budget.remaining() <= 0:
                return None
            self._budget.push_sub_cap(int(op_cap))
        try:
            return fn(*args, **kwargs)
        except SubBudgetExhausted:
            return None
        except Exception as exc:
            self.fn_errors[fn_name] = self.fn_errors.get(fn_name, 0) + 1
            if fn_name not in self.fn_error_msgs:
                self.fn_error_msgs[fn_name] = f"{type(exc).__name__}: {str(exc)[:140]}"
            return None
        finally:
            if op_cap is not None:
                self._budget.pop_sub_cap()


def run_compositional_artifact(
    initial_solution: Any,
    artifact: CompositionalAlgoArtifact,
    domain_api_factory: Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]],
    call_args_fn: Callable[[Any, Dict[str, Any], LibNamespace, OpBudget], Tuple[Any, ...]],
    verify_fn: Callable[[Any], bool],
    cost_fn: Callable[[Any], int],
    op_budget: int,
) -> Tuple[Any, Dict[str, Any]]:
    """Execute a `CompositionalAlgoArtifact` strictly monotonically under deterministic `OpBudget`.

    Guarantees:
      - Zero wall-clock dependence (100% bit-for-bit deterministic for fixed artifact/task/seed).
      - Strictly monotonic: tracks `best` globally via `report_best` and final return value.
      - Un-bypassable `op_budget` cap (`BudgetExhausted(BaseException)`).
      - Records exact `ops_spent`, `module_calls`, `cross_gen_calls`, and `gen_gate_drops`.
    """
    budget = OpBudget(limit=op_budget)
    gen_stack: List[Tuple[str, int]] = [("orchestrator", artifact.generation)]
    lib = LibNamespace(budget, gen_stack)

    best_box: List[Any] = [initial_solution]
    best_cost_box: List[int] = [cost_fn(initial_solution)]
    gen_gate_drops: Dict[str, int] = {}
    mod_gate_drops: Dict[str, int] = {}
    unsound_rejects: int = 0

    def _report_best(cand: Any) -> bool:
        nonlocal unsound_rejects
        if cand is None:
            return False
        c_cost = cost_fn(cand)
        if c_cost < best_cost_box[0]:
            if verify_fn(cand):
                drop = best_cost_box[0] - c_cost
                best_box[0] = cand
                best_cost_box[0] = c_cost
                active_mod, active_gen = gen_stack[-1] if gen_stack else ("orchestrator", artifact.generation)
                gk = f"g{active_gen}"
                gen_gate_drops[gk] = gen_gate_drops.get(gk, 0) + drop
                mod_gate_drops[active_mod] = mod_gate_drops.get(active_mod, 0) + drop
                return True
            unsound_rejects += 1
        return False

    api_dict = domain_api_factory(budget, _report_best)
    api_dict["report_best"] = _report_best
    api_dict["best_solution"] = lambda: best_box[0]
    api_dict["best_cost"] = lambda: best_cost_box[0]

    def _op_tick() -> None:
        budget.charge(1)

    def _op_iter(it: Iterable[Any]) -> Iterable[Any]:
        for x in it:
            budget.charge(1)
            yield x

    safe_builtins = dict(_SAFE_BUILTINS_BASE)
    safe_builtins["range"] = _make_safe_range(budget)

    def _make_ns() -> Dict[str, Any]:
        ns: Dict[str, Any] = {
            "__builtins__": safe_builtins,
            "_op_tick": _op_tick,
            "_op_iter": _op_iter,
            "lib": lib,
            "budget": budget,
        }
        ns.update(_SAFE_STDLIB)
        ns.update(api_dict)
        return ns

    status = "ok"
    err_msg = ""

    # 1. Compile and register all library modules in generation order
    for m in artifact.modules:
        try:
            tree, exported = validate_module_source(m.source)
            code = _compile_instrumented(tree, filename=f"<lib:{m.name}>")
            ns = _make_ns()
            exec(code, ns, ns)
            for fn_name in exported:
                fn = ns.get(fn_name)
                if callable(fn):
                    lib.register(fn_name, fn, m.name, m.generation)
        except Exception as exc:
            status = "compile_error"
            err_msg = f"mod {m.name}: {type(exc).__name__}: {str(exc)[:140]}"
            break

    # 2. Compile and run orchestrator `solve(...)`
    if status == "ok":
        try:
            orch_tree, _ = validate_module_source(artifact.orchestrator.source, required_fn="solve")
            orch_code = _compile_instrumented(orch_tree, filename=f"<orch:{artifact.orchestrator.name}>")
            orch_ns = _make_ns()
            exec(orch_code, orch_ns, orch_ns)
            solve_fn = orch_ns.get("solve")
            if not callable(solve_fn):
                raise ValueError("Orchestrator did not bind callable `solve`")
            args = call_args_fn(best_box[0], api_dict, lib, budget)
            cand = solve_fn(*args)
            _report_best(cand)
        except BudgetExhausted:
            status = "budget_exhausted"
        except SubBudgetExhausted:
            status = "sub_budget_exhausted"
        except Exception as exc:
            status = "error"
            err_msg = f"{type(exc).__name__}: {str(exc)[:160]}"

    return best_box[0], {
        "final_cost": best_cost_box[0],
        "ops_spent": min(budget.spent, budget.limit),
        "ops_limit": budget.limit,
        "status": status,
        "error": err_msg,
        "unsound_rejects": unsound_rejects,
        "module_calls": dict(lib.module_calls),
        "cross_gen_calls": dict(lib.cross_gen_calls),
        "gen_gate_drops": dict(gen_gate_drops),
        "mod_gate_drops": dict(mod_gate_drops),
        "fn_errors": dict(lib.fn_errors),
        "fn_error_msgs": dict(lib.fn_error_msgs),
    }
