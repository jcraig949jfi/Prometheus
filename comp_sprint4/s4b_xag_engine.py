"""Track S4-B Metered Deterministic 9-to-11 Input XAG Engine + Matched-Op Causal Knockouts."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from comp_sprint.circuit import XAGCircuit, full_mask, input_masks, verify_truth_tables
from comp_sprint2.s2a_engine import davio_base_6to8
from comp_sprint3.s3_engine import (
    build_s3_a3_artifact,
    build_s3_a5_sham_artifact,
    make_metered_xag_api_factory,
)
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, OpBudget, run_compositional_artifact
from comp_sprint4.ko_matched import run_matched_op_knockout


DEFAULT_S4B_OP_BUDGET = 160_000


def make_s4b_xag_api_factory(
    n_inputs: int,
    clean_targets: Tuple[int, ...],
) -> Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]]:
    base_factory = make_metered_xag_api_factory(n_inputs, clean_targets)
    mask = full_mask(n_inputs)
    in_ms = input_masks(n_inputs)

    def factory(budget: OpBudget, report_best: Callable[[Any], bool]) -> Dict[str, Any]:
        api = base_factory(budget, report_best)

        def m_cofactor(tt: int, var: int, val: int) -> int:
            budget.charge(1)
            m1 = in_ms[var]
            sh = 1 << var
            if val == 0:
                lo = tt & (mask ^ m1)
                return lo | (lo << sh)
            hi = tt & m1
            return hi | (hi >> sh)

        api["cofactor"] = m_cofactor
        return api

    return factory


def build_s4b_a3_artifact() -> CompositionalAlgoArtifact:
    a3 = build_s3_a3_artifact()
    return CompositionalAlgoArtifact("A3_ZERO_LLM", "S4B_XAG_4GEN", 0, a3.modules, a3.orchestrator)


def build_s4b_a5_sham_artifact() -> CompositionalAlgoArtifact:
    a5 = build_s3_a5_sham_artifact()
    return CompositionalAlgoArtifact("A5_SHAM", "S4B_XAG_4GEN", 0, a5.modules, a5.orchestrator)


def synthesize_s4b_with_artifact(
    n_inputs: int,
    targets: Sequence[int],
    artifact: Optional[CompositionalAlgoArtifact],
    seed: int = 0,
    op_budget: int = DEFAULT_S4B_OP_BUDGET,
    fallback_artifact: Optional[CompositionalAlgoArtifact] = None,
) -> Tuple[XAGCircuit, Dict[str, Any]]:
    """Unified 100%-deterministic Track S4-B evaluator with matched-op knockout support."""
    mask = full_mask(n_inputs)
    clean_targets = tuple(t & mask for t in targets)
    base = davio_base_6to8(n_inputs, clean_targets, seed=seed)
    if artifact is None:
        return base, {
            "final_cost": base.gate_count(),
            "ops_spent": 0,
            "ops_limit": op_budget,
            "status": "base_only",
            "module_calls": {},
            "cross_gen_calls": {},
            "gen_gate_drops": {},
            "mod_gate_drops": {},
            "fn_errors": {},
            "fn_error_msgs": {},
        }

    api_factory = make_s4b_xag_api_factory(n_inputs, clean_targets)
    verify_fn = lambda c: isinstance(c, XAGCircuit) and c.n_inputs == n_inputs and verify_truth_tables(c, clean_targets)
    cost_fn = lambda c: int(c.gate_count())
    call_args_fn = lambda cur, api, lib, bud: (cur, n_inputs, clean_targets, seed, api, lib, bud)

    if fallback_artifact is not None:
        best, meta = run_matched_op_knockout(
            initial_solution=base,
            knocked_artifact=artifact,
            fallback_artifact=fallback_artifact,
            domain_api_factory=api_factory,
            call_args_fn=call_args_fn,
            verify_fn=verify_fn,
            cost_fn=cost_fn,
            op_budget=op_budget,
        )
    else:
        best, meta = run_compositional_artifact(
            initial_solution=base,
            artifact=artifact,
            domain_api_factory=api_factory,
            call_args_fn=call_args_fn,
            verify_fn=verify_fn,
            cost_fn=cost_fn,
            op_budget=op_budget,
        )
    assert verify_truth_tables(best, clean_targets)
    return best, meta
