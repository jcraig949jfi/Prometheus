"""Law 4b Deterministic Word-Width + Container + Call Metering (`OpBudget v3`).

Extends Law 4 (`OpBudget v2`) to close the final Q3 metering gap (Python container/dict/sort
allocation overhead observed in S5-Q):
  1. Every loop iteration (`for`, `while`, comprehension): 1 unit.
  2. Every big-int `BinOp` / `UnaryOp(~)` / `AugAssign` > 64 bits: `(bits - 1) // 64` units.
  3. Every user function entry (`ast.FunctionDef`): 3 units (`_op_call()`).
  4. Every container construction (`dict`, `set`, `list`, `tuple`, comprehensions, literals)
     and `sorted(...)` call charges CPU-proportional allocation/sort units:
       - `dict` / `set`: `4 + 2 * len(x)`
       - `list` / `tuple`: `2 + len(x)`
       - `sorted`: `4 + n * max(1, n.bit_length())`
Preserves exact Law 1 determinism (`0.000` variance) while keeping wall-clock parity tight
across bitmask loops, hash-table beam searches, and mutable-netlist walks.
"""
from __future__ import annotations

import ast
import copy
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from comp_sprint.circuit import XAGCircuit, full_mask, verify_truth_tables
from comp_sprint2.s2a_engine import davio_base_6to8
from comp_sprint3.sandbox_s3 import (
    BudgetExhausted,
    CompositionalAlgoArtifact,
    LibNamespace,
    OpBudget,
    SubBudgetExhausted,
    _SAFE_BUILTINS_BASE,
    _SAFE_STDLIB,
    _make_safe_range,
    validate_module_source,
)
from comp_sprint4.law4_meter import _BINOP_NAMES, _make_word_helpers
from comp_sprint4.s4b_xag_engine import make_s4b_xag_api_factory


DEFAULT_S6_V3_BUDGET = 2_400_000


class _Law4bInstrumenter(ast.NodeTransformer):
    """Instrument loops, big-int word ops, function entries, and container literals/comprehensions."""

    def _tick_stmt(self) -> ast.Expr:
        return ast.Expr(value=ast.Call(func=ast.Name(id="_op_tick", ctx=ast.Load()), args=[], keywords=[]))

    def _call_stmt(self) -> ast.Expr:
        return ast.Expr(value=ast.Call(func=ast.Name(id="_op_call", ctx=ast.Load()), args=[], keywords=[]))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        node.body.insert(0, self._call_stmt())
        return node

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
        node.iter = ast.Call(func=ast.Name(id="_op_iter", ctx=ast.Load()), args=[node.iter], keywords=[])
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        fn_name = _BINOP_NAMES.get(type(node.op))
        if fn_name is None:
            return node
        return ast.Call(func=ast.Name(id=fn_name, ctx=ast.Load()), args=[node.left, node.right], keywords=[])

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.op, ast.Invert):
            return ast.Call(func=ast.Name(id="_w_inv", ctx=ast.Load()), args=[node.operand], keywords=[])
        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            chk = ast.Expr(value=ast.Call(func=ast.Name(id="_wchk", ctx=ast.Load()), args=[ast.Name(id=node.target.id, ctx=ast.Load())], keywords=[]))
            return [node, chk]
        return node

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        self.generic_visit(node)
        return ast.Call(func=ast.Name(id="_w_alloc_map", ctx=ast.Load()), args=[node], keywords=[])

    def visit_Set(self, node: ast.Set) -> ast.AST:
        self.generic_visit(node)
        return ast.Call(func=ast.Name(id="_w_alloc_map", ctx=ast.Load()), args=[node], keywords=[])

    def visit_DictComp(self, node: ast.DictComp) -> ast.AST:
        self.generic_visit(node)
        return ast.Call(func=ast.Name(id="_w_alloc_map", ctx=ast.Load()), args=[node], keywords=[])

    def visit_SetComp(self, node: ast.SetComp) -> ast.AST:
        self.generic_visit(node)
        return ast.Call(func=ast.Name(id="_w_alloc_map", ctx=ast.Load()), args=[node], keywords=[])

    def visit_ListComp(self, node: ast.ListComp) -> ast.AST:
        self.generic_visit(node)
        return ast.Call(func=ast.Name(id="_w_alloc_seq", ctx=ast.Load()), args=[node], keywords=[])


def _compile_law4b(tree: ast.Module, filename: str) -> Any:
    inst = _Law4bInstrumenter().visit(copy.deepcopy(tree))
    ast.fix_missing_locations(inst)
    return compile(inst, filename=filename, mode="exec")


def _make_law4b_builtins(budget: OpBudget) -> Dict[str, Any]:
    charge = budget.charge
    sb = dict(_SAFE_BUILTINS_BASE)
    sb["range"] = _make_safe_range(budget)

    def m_dict(*args: Any, **kwargs: Any) -> dict:
        res = dict(*args, **kwargs)
        charge(4 + 2 * len(res))
        return res

    def m_set(*args: Any) -> set:
        res = set(*args)
        charge(4 + 2 * len(res))
        return res

    def m_list(*args: Any) -> list:
        res = list(*args)
        charge(2 + len(res))
        return res

    def m_tuple(*args: Any) -> tuple:
        res = tuple(*args)
        charge(2 + len(res))
        return res

    def m_sorted(iterable: Iterable[Any], /, *, key: Any = None, reverse: bool = False) -> list:
        res = sorted(iterable, key=key, reverse=reverse)
        n = len(res)
        charge(4 + n * max(1, n.bit_length()))
        return res

    sb["dict"] = m_dict
    sb["set"] = m_set
    sb["list"] = m_list
    sb["tuple"] = m_tuple
    sb["sorted"] = m_sorted
    return sb


def run_compositional_law4b(
    initial_solution: Any,
    artifact: CompositionalAlgoArtifact,
    domain_api_factory: Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]],
    call_args_fn: Callable[[Any, Dict[str, Any], LibNamespace, OpBudget], Tuple[Any, ...]],
    verify_fn: Callable[[Any], bool],
    cost_fn: Callable[[Any], int],
    v3_budget: int,
    fallback_artifact: Optional[CompositionalAlgoArtifact] = None,
) -> Tuple[Any, Dict[str, Any]]:
    """Execute `CompositionalAlgoArtifact` under Law 4b (`OpBudget v3`: word + container + call metering)."""
    budget = OpBudget(limit=v3_budget)
    gen_stack: List[Tuple[str, int]] = [("orchestrator", artifact.generation)]
    lib = LibNamespace(budget, gen_stack)

    best_box: List[Any] = [initial_solution]
    best_cost_box: List[int] = [cost_fn(initial_solution)]
    gen_gate_drops: Dict[str, int] = {}
    mod_gate_drops: Dict[str, int] = {}
    unsound_rejects = 0

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

    charge = budget.charge

    def _op_tick() -> None:
        charge(1)

    def _op_call() -> None:
        charge(3)

    def _op_iter(it: Iterable[Any]) -> Iterable[Any]:
        for x in it:
            charge(1)
            yield x

    def _w_alloc_map(obj: Any) -> Any:
        charge(4 + 2 * len(obj))
        return obj

    def _w_alloc_seq(obj: Any) -> Any:
        charge(2 + len(obj))
        return obj

    safe_builtins = _make_law4b_builtins(budget)
    word_helpers = _make_word_helpers(budget)

    def _make_ns() -> Dict[str, Any]:
        ns: Dict[str, Any] = {
            "__builtins__": safe_builtins,
            "_op_tick": _op_tick,
            "_op_call": _op_call,
            "_op_iter": _op_iter,
            "_w_alloc_map": _w_alloc_map,
            "_w_alloc_seq": _w_alloc_seq,
            "lib": lib,
            "budget": budget,
        }
        ns.update(word_helpers)
        ns.update(_SAFE_STDLIB)
        ns.update(api_dict)
        return ns

    status = "ok"
    err_msg = ""
    for m in artifact.modules:
        try:
            tree, exported = validate_module_source(m.source)
            code = _compile_law4b(tree, filename=f"<lib_v3:{m.name}>")
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

    if status == "ok":
        try:
            orch_tree, _ = validate_module_source(artifact.orchestrator.source, required_fn="solve")
            orch_code = _compile_law4b(orch_tree, filename=f"<orch_v3:{artifact.orchestrator.name}>")
            orch_ns = _make_ns()
            exec(orch_code, orch_ns, orch_ns)
            solve_fn = orch_ns.get("solve")
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

    meta = {
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

    if fallback_artifact is not None:
        rem = v3_budget - int(meta["ops_spent"])
        if rem >= 10_000:
            best2, meta2 = run_compositional_law4b(
                initial_solution=best_box[0],
                artifact=fallback_artifact,
                domain_api_factory=domain_api_factory,
                call_args_fn=call_args_fn,
                verify_fn=verify_fn,
                cost_fn=cost_fn,
                v3_budget=rem,
                fallback_artifact=None,
            )
            if cost_fn(best2) < best_cost_box[0] and verify_fn(best2):
                best_box[0] = best2
                best_cost_box[0] = cost_fn(best2)
            meta["ops_spent"] = min(v3_budget, int(meta["ops_spent"]) + int(meta2["ops_spent"]))
            meta["final_cost"] = best_cost_box[0]
            for k, v in meta2["cross_gen_calls"].items():
                meta["cross_gen_calls"][k] = meta["cross_gen_calls"].get(k, 0) + v

    return best_box[0], meta


def synthesize_s6_xag(
    n_inputs: int,
    targets: Sequence[int],
    artifact: Optional[CompositionalAlgoArtifact],
    seed: int = 0,
    v3_budget: int = DEFAULT_S6_V3_BUDGET,
    fallback_artifact: Optional[CompositionalAlgoArtifact] = None,
) -> Tuple[XAGCircuit, Dict[str, Any]]:
    """Unified 100%-deterministic Law 4b (`OpBudget v3`) 8-10in XAG evaluator."""
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)
    base = davio_base_6to8(n_inputs, clean_targets, seed=seed)
    if artifact is None:
        return base, {
            "final_cost": base.gate_count(), "ops_spent": 0, "ops_limit": v3_budget,
            "status": "base_only", "module_calls": {}, "cross_gen_calls": {},
            "gen_gate_drops": {}, "mod_gate_drops": {}, "fn_errors": {}, "fn_error_msgs": {},
        }
    api_factory = make_s4b_xag_api_factory(n_inputs, clean_targets)
    best, meta = run_compositional_law4b(
        initial_solution=base,
        artifact=artifact,
        domain_api_factory=api_factory,
        call_args_fn=lambda cur, api, lib, bud: (cur, n_inputs, clean_targets, seed, api, lib, bud),
        verify_fn=lambda c: isinstance(c, XAGCircuit) and c.n_inputs == n_inputs and verify_truth_tables(c, clean_targets),
        cost_fn=lambda c: int(c.gate_count()),
        v3_budget=v3_budget,
        fallback_artifact=fallback_artifact,
    )
    assert verify_truth_tables(best, clean_targets)
    return best, meta
