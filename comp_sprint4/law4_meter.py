"""Law 4 Deterministic Word-Width & Z3-Decision Metering (`OpBudget v2`).

Closes the Q3 Sprint 4 metering loophole while preserving Law 1 (`0.000` jitter):
  1. Big-Int Word-Width Metering: Every integer `BinOp` (`&`, `|`, `^`, `+`, `-`, `*`, `<<`, `>>`),
     `UnaryOp` (`~`), and `AugAssign` charges `(bits - 1) // 64` word-ops whenever operand/result
     bit-length exceeds 64 bits. Thus a 50,000-bit packed Python int is charged ~781x a 64-bit op,
     matching real CPU word cycles with 0.000 wall-clock jitter.
  2. Z3-rlimit-Proportional Metering: `verify_bv_equiv_z3_det_v2` returns exact deterministic
     `rlimit_count` from an isolated `z3.Context()`, charging `max(50, rlimit_count // 25)` ops
     per SMT query instead of a flat constant.
"""
from __future__ import annotations

import ast
import copy
import operator
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import z3

from comp_sprint.circuit import XAGCircuit, full_mask, verify_truth_tables
from comp_sprint2.s2a_engine import davio_base_6to8
from comp_sprint2.s2b_bv import BVProgram, default_test_vectors
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
from comp_sprint4.s4a_bv_engine import _prog_to_z3_ctx, bv_base_simplify_det, make_metered_bv_api_factory
from comp_sprint4.s4b_xag_engine import make_s4b_xag_api_factory


_BINOP_NAMES = {
    ast.BitAnd: "_w_and",
    ast.BitOr: "_w_or",
    ast.BitXor: "_w_xor",
    ast.LShift: "_w_lsh",
    ast.RShift: "_w_rsh",
    ast.Add: "_w_add",
    ast.Sub: "_w_sub",
    ast.Mult: "_w_mul",
}


class _WordOpInstrumenter(ast.NodeTransformer):
    """Instrument loops (`_op_tick`, `_op_iter`) AND big-int word operations (`_w_*`, `_wchk`)."""

    def _tick_stmt(self) -> ast.Expr:
        return ast.Expr(value=ast.Call(func=ast.Name(id="_op_tick", ctx=ast.Load()), args=[], keywords=[]))

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
        return ast.Call(
            func=ast.Name(id=fn_name, ctx=ast.Load()),
            args=[node.left, node.right],
            keywords=[],
        )

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.op, ast.Invert):
            return ast.Call(func=ast.Name(id="_w_inv", ctx=ast.Load()), args=[node.operand], keywords=[])
        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        self.generic_visit(node)
        # Preserve exact in-place mutation semantics (e.g. set |=) and charge big-int result width after!
        if isinstance(node.target, ast.Name):
            chk = ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="_wchk", ctx=ast.Load()),
                    args=[ast.Name(id=node.target.id, ctx=ast.Load())],
                    keywords=[],
                )
            )
            return [node, chk]
        return node


def _compile_word_instrumented(tree: ast.Module, filename: str) -> Any:
    inst = _WordOpInstrumenter().visit(copy.deepcopy(tree))
    ast.fix_missing_locations(inst)
    return compile(inst, filename=filename, mode="exec")


def _make_word_helpers(budget: OpBudget) -> Dict[str, Any]:
    charge = budget.charge

    def _wchk(val: Any) -> Any:
        if type(val) is int:
            bl = val.bit_length()
            if bl > 64:
                charge((bl - 1) >> 6)
        return val

    def _mk_bin(op_fn: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        def _fn(a: Any, b: Any) -> Any:
            if type(a) is int and type(b) is int:
                bl = a.bit_length()
                bl2 = b.bit_length()
                if bl2 > bl:
                    bl = bl2
                if bl > 64:
                    charge((bl - 1) >> 6)
                res = op_fn(a, b)
                if type(res) is int:
                    rbl = res.bit_length()
                    if rbl > bl and rbl > 64:
                        charge((rbl - bl) >> 6)
                return res
            return op_fn(a, b)
        return _fn

    def _w_inv(a: Any) -> Any:
        if type(a) is int:
            bl = a.bit_length()
            if bl > 64:
                charge((bl - 1) >> 6)
        return ~a

    return {
        "_wchk": _wchk,
        "_w_and": _mk_bin(operator.and_),
        "_w_or": _mk_bin(operator.or_),
        "_w_xor": _mk_bin(operator.xor),
        "_w_lsh": _mk_bin(operator.lshift),
        "_w_rsh": _mk_bin(operator.rshift),
        "_w_add": _mk_bin(operator.add),
        "_w_sub": _mk_bin(operator.sub),
        "_w_mul": _mk_bin(operator.mul),
        "_w_inv": _w_inv,
    }


def verify_bv_equiv_z3_det_v2(
    spec: BVProgram,
    cand: BVProgram,
    rlimit: int = 120_000,
) -> Tuple[bool, Optional[Tuple[int, ...]], int]:
    """Isolated deterministic Z3 check returning `(is_unsat, cex, exact_rlimit_count)`."""
    if spec.width != cand.width or spec.n_inputs != cand.n_inputs:
        return False, None, 0
    if spec.sha256() == cand.sha256():
        return True, None, 0
    ctx = z3.Context()
    s = z3.Solver(ctx=ctx)
    s.set("rlimit", int(rlimit))
    s.set("random_seed", 0)
    zvars = [z3.BitVec(f"x{i}", spec.width, ctx=ctx) for i in range(spec.n_inputs)]
    s.add(_prog_to_z3_ctx(spec, zvars, ctx) != _prog_to_z3_ctx(cand, zvars, ctx))
    res = s.check()
    st = s.statistics()
    rl_used = int(st.get_key_value("rlimit count")) if "rlimit count" in st.keys() else int(rlimit)
    if res == z3.unsat:
        return True, None, rl_used
    if res == z3.sat:
        m = s.model()
        cex = tuple(int(m.evaluate(v, model_completion=True).as_long()) for v in zvars)
        return False, cex, rl_used
    return False, None, rl_used


def run_compositional_word_metered(
    initial_solution: Any,
    artifact: CompositionalAlgoArtifact,
    domain_api_factory: Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]],
    call_args_fn: Callable[[Any, Dict[str, Any], LibNamespace, OpBudget], Tuple[Any, ...]],
    verify_fn: Callable[[Any], bool],
    cost_fn: Callable[[Any], int],
    word_budget: int,
) -> Tuple[Any, Dict[str, Any]]:
    """Execute `CompositionalAlgoArtifact` under strict Law 4 `OpBudget v2` (word-width + Z3 rlimit)."""
    budget = OpBudget(limit=word_budget)
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

    def _op_tick() -> None:
        budget.charge(1)

    def _op_iter(it: Iterable[Any]) -> Iterable[Any]:
        for x in it:
            budget.charge(1)
            yield x

    safe_builtins = dict(_SAFE_BUILTINS_BASE)
    safe_builtins["range"] = _make_safe_range(budget)
    word_helpers = _make_word_helpers(budget)

    def _make_ns() -> Dict[str, Any]:
        ns: Dict[str, Any] = {
            "__builtins__": safe_builtins,
            "_op_tick": _op_tick,
            "_op_iter": _op_iter,
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
            code = _compile_word_instrumented(tree, filename=f"<lib_v2:{m.name}>")
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
            orch_code = _compile_word_instrumented(orch_tree, filename=f"<orch_v2:{artifact.orchestrator.name}>")
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


def optimize_s4a_law4(
    spec: BVProgram,
    artifact: Optional[CompositionalAlgoArtifact],
    seed: int = 0,
    word_budget: int = 180_000,
) -> Tuple[BVProgram, Dict[str, Any]]:
    """Evaluate a Track S4-A BV artifact under Law 4 (`OpBudget v2`: word-width + actual Z3 rlimit_count // 15)."""
    base = bv_base_simplify_det(spec)
    if artifact is None:
        return base, {"final_cost": base.op_count(), "ops_spent": 0, "status": "base_only"}

    base_factory = make_metered_bv_api_factory(spec)

    def api_factory_v2(budget: OpBudget, report_best: Callable[[Any], bool]) -> Dict[str, Any]:
        api = base_factory(budget, report_best)

        def m_z3_v2(p1: BVProgram, p2: BVProgram) -> Tuple[bool, Optional[Tuple[int, ...]]]:
            ok, cex, rl = verify_bv_equiv_z3_det_v2(p1, p2, rlimit=120_000)
            budget.charge(max(50, rl // 15))
            return ok, cex

        api["verify_equiv_z3"] = m_z3_v2
        return api

    tv_fast = default_test_vectors(spec.width, spec.n_inputs, seed=20261129, n_rand=24)
    spec_vec = spec.eval_vectors(tv_fast)

    def _verify(c: Any) -> bool:
        if not isinstance(c, BVProgram) or c.width != spec.width or c.n_inputs != spec.n_inputs:
            return False
        if c.eval_vectors(tv_fast) != spec_vec:
            return False
        ok, _, _ = verify_bv_equiv_z3_det_v2(spec, c, rlimit=450_000)
        return ok

    return run_compositional_word_metered(
        initial_solution=base,
        artifact=artifact,
        domain_api_factory=api_factory_v2,
        call_args_fn=lambda cur, api, lib, bud: (cur, spec, seed, api, lib, bud),
        verify_fn=_verify,
        cost_fn=lambda p: int(p.op_count()),
        word_budget=word_budget,
    )


def synthesize_s4b_law4(
    n_inputs: int,
    targets: Sequence[int],
    artifact: Optional[CompositionalAlgoArtifact],
    seed: int = 0,
    word_budget: int = 1_500_000,
) -> Tuple[XAGCircuit, Dict[str, Any]]:
    """Evaluate a Track S4-B XAG artifact under Law 4 (`OpBudget v2`: 64-bit word-width metering)."""
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)
    base = davio_base_6to8(n_inputs, clean_targets, seed=seed)
    if artifact is None:
        return base, {"final_cost": base.gate_count(), "ops_spent": 0, "status": "base_only"}

    api_factory = make_s4b_xag_api_factory(n_inputs, clean_targets)
    return run_compositional_word_metered(
        initial_solution=base,
        artifact=artifact,
        domain_api_factory=api_factory,
        call_args_fn=lambda cur, api, lib, bud: (cur, n_inputs, clean_targets, seed, api, lib, bud),
        verify_fn=lambda c: isinstance(c, XAGCircuit) and c.n_inputs == n_inputs and verify_truth_tables(c, clean_targets),
        cost_fn=lambda c: int(c.gate_count()),
        word_budget=word_budget,
    )
