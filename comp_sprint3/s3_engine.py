"""Sprint 3 Metered Deterministic XAG Engine (Law 1: 0.000 Wall-Clock Variance).

Every domain API call AND every loop iteration is deterministically charged to `OpBudget`.
All arms (`A2_PRIOR_ONLY`, `G1`, `G2`, `G3`, `G3_KO_*`, `A3_ZERO_LLM`, `A5_SHAM`) receive
the EXACT same integer `op_budget` per task.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from comp_sprint.circuit import (
    Gate,
    StrashBuilder,
    XAGCircuit,
    full_mask,
    input_masks,
    verify_truth_tables,
)
from comp_sprint.npn import npn4_canonical
from comp_sprint.synth_base import _enumerate_cuts, _eval_cut_tt
from comp_sprint2.s2a_engine import (
    _safe_cone_size,
    _safe_davio,
    _safe_node_tts,
    _safe_sat_exact_4in,
    _safe_sat_exact_multi,
    _safe_splice_cut,
    _safe_splice_npn4,
    davio_base_6to8,
)
from comp_sprint3.sandbox_s3 import (
    CompositionalAlgoArtifact,
    LibModule,
    OpBudget,
    run_compositional_artifact,
)


DEFAULT_S3_OP_BUDGET = 120_000


def make_metered_xag_api_factory(
    n_inputs: int,
    clean_targets: Tuple[int, ...],
) -> Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]]:
    """Build a deterministic, op-metered domain API factory bound to `OpBudget`."""

    def factory(budget: OpBudget, _report_best: Callable[[Any], bool]) -> Dict[str, Any]:
        class MeteredStrashBuilder(StrashBuilder):
            def add_gate(self, op: str, left: int, left_inv: bool, right: int, right_inv: bool) -> Tuple[int, bool]:
                budget.charge(2)
                return super().add_gate(op, left, left_inv, right, right_inv)

            def build(self, outputs: Sequence[Tuple[int, bool]], prune_dead: bool = True) -> XAGCircuit:
                budget.charge(max(5, len(self.gates)))
                return super().build(outputs, prune_dead=prune_dead)

        def m_sat_4in(tt4: int, max_gates: int = 6) -> Optional[XAGCircuit]:
            budget.charge(400)
            return _safe_sat_exact_4in(tt4, max_gates=max_gates)

        def m_sat_multi(n_in: int, targets: Sequence[int], max_gates: int = 5) -> Optional[XAGCircuit]:
            budget.charge(500)
            return _safe_sat_exact_multi(n_in, targets, max_gates=max_gates)

        def m_davio(n_in: int, targets: Sequence[int], var_order: Sequence[int], greedy: bool = False) -> XAGCircuit:
            budget.charge(180)
            return _safe_davio(n_in, targets, var_order, greedy=greedy)

        def m_enum_cuts(circ: XAGCircuit, max_k: int = 4, max_cuts_per_node: int = 16) -> Dict[int, List[Tuple[int, ...]]]:
            budget.charge(max(15, circ.gate_count() * 2))
            return _enumerate_cuts(circ, max_k=max_k, max_cuts_per_node=max_cuts_per_node)

        def m_eval_cut(circ: XAGCircuit, nid: int, leaves: Sequence[int]) -> Optional[int]:
            budget.charge(5)
            return _eval_cut_tt(circ, nid, tuple(leaves))

        def m_splice_cut(circ: XAGCircuit, target_nid: int, leaves: Sequence[int], repl_circ: XAGCircuit) -> Optional[XAGCircuit]:
            budget.charge(max(10, circ.gate_count()))
            return _safe_splice_cut(circ, target_nid, leaves, repl_circ)

        def m_splice_npn4(circ: XAGCircuit, target_nid: int, leaves: Tuple[int, ...], canon_circ: XAGCircuit, cut_tt4: int) -> Optional[XAGCircuit]:
            budget.charge(max(10, circ.gate_count()))
            return _safe_splice_npn4(circ, target_nid, leaves, canon_circ, cut_tt4)

        def m_cone_size(circ: XAGCircuit, root_nid: int, leaves: Sequence[int]) -> int:
            budget.charge(4)
            return _safe_cone_size(circ, root_nid, leaves)

        def m_node_tts(circ: XAGCircuit) -> Dict[int, int]:
            budget.charge(max(5, circ.gate_count()))
            return _safe_node_tts(circ)

        def m_verify(circ: XAGCircuit, targets: Sequence[int]) -> bool:
            budget.charge(max(5, circ.gate_count()))
            return verify_truth_tables(circ, targets)

        def m_npn4(tt4: int) -> int:
            budget.charge(3)
            return npn4_canonical(tt4)

        def m_circuit_features(circ: XAGCircuit) -> Dict[str, Any]:
            budget.charge(max(5, circ.gate_count()))
            and_c = sum(1 for g in circ.gates if g.op == "AND")
            xor_c = len(circ.gates) - and_c
            return {
                "n_inputs": circ.n_inputs,
                "n_outputs": len(circ.outputs),
                "gate_count": len(circ.gates),
                "and_count": and_c,
                "xor_count": xor_c,
                "xor_ratio": xor_c / max(1, len(circ.gates)),
            }

        return {
            "Gate": Gate,
            "StrashBuilder": MeteredStrashBuilder,
            "XAGCircuit": XAGCircuit,
            "full_mask": full_mask,
            "input_masks": input_masks,
            "npn4_canonical": m_npn4,
            "sat_exact_4in": m_sat_4in,
            "sat_exact_multi": m_sat_multi,
            "davio_synth": m_davio,
            "enumerate_cuts": m_enum_cuts,
            "eval_cut_tt": m_eval_cut,
            "splice_cut": m_splice_cut,
            "splice_npn4": m_splice_npn4,
            "cone_size": m_cone_size,
            "node_tts": m_node_tts,
            "verify_truth_tables": m_verify,
            "circuit_features": m_circuit_features,
        }

    return factory


# ---------------- Deterministic Op-Budget Baselines: A3_ZERO_LLM & A5_SHAM ----------------

_A3_S3_MOD = """
def det_sat_cut_rewrite(circ, n_inputs, targets, seed):
    best = circ
    npn_cache = {}
    for _round in range(6):
        if budget.remaining() < 500:
            break
        improved = False
        cuts = enumerate_cuts(best, max_k=4, max_cuts_per_node=16)
        n_in = best.n_inputs
        cands = []
        for gi in range(best.gate_count() - 1, -1, -1):
            nid = n_in + gi
            for lf in cuts.get(nid, ()):
                if len(lf) < 3:
                    continue
                cs = cone_size(best, nid, lf)
                if cs >= 4:
                    cands.append((cs, nid, lf))
        cands.sort(key=lambda x: x[0], reverse=True)
        for cs, nid, lf in cands[:48]:
            if budget.remaining() < 500:
                break
            tt4 = eval_cut_tt(best, nid, lf)
            if tt4 is None:
                continue
            c = npn4_canonical(tt4)
            if c in (0x0000, 0x00FF, 0x000F, 0x0FF0):
                continue
            if c not in npn_cache:
                npn_cache[c] = sat_exact_4in(c, max_gates=min(cs - 1, 5))
            opt = npn_cache[c]
            if opt is None or opt.gate_count() >= cs:
                continue
            cand = splice_npn4(best, nid, lf, opt, tt4)
            if cand is not None and cand.gate_count() < best.gate_count():
                if report_best(cand):
                    best = cand
                    improved = True
                    break
        if not improved:
            break
    return best
"""

_A3_S3_ORCH = """
def solve(circ, n_inputs, targets, seed, api, lib, budget):
    return lib.det_sat_cut_rewrite(circ, n_inputs, targets, seed)
"""

_A5_S3_MOD = """
def sham_random_davio(circ, n_inputs, targets, seed):
    rng = random.Random(seed * 10007 + 31337)
    best = circ
    base_ord = list(range(n_inputs))
    iters = 0
    while budget.remaining() > 250:
        iters += 1
        ord_i = list(base_ord)
        rng.shuffle(ord_i)
        cand = davio_synth(n_inputs, targets, ord_i, greedy=(iters % 5 == 0))
        if cand.gate_count() < best.gate_count():
            if report_best(cand):
                best = cand
    return best
"""

_A5_S3_ORCH = """
def solve(circ, n_inputs, targets, seed, api, lib, budget):
    return lib.sham_random_davio(circ, n_inputs, targets, seed)
"""


def build_s3_a3_artifact() -> CompositionalAlgoArtifact:
    mod = LibModule.from_source("a3_det_sat_cut", 0, _A3_S3_MOD, origin="zero_llm_baseline")
    orch = LibModule.from_source("a3_orch", 0, _A3_S3_ORCH, required_fn="solve", origin="zero_llm_baseline")
    return CompositionalAlgoArtifact(arm="A3_ZERO_LLM", track="S3_XAG_COMP", generation=0, modules=(mod,), orchestrator=orch)


def build_s3_a5_sham_artifact() -> CompositionalAlgoArtifact:
    mod = LibModule.from_source("a5_sham_davio", 0, _A5_S3_MOD, origin="sham_matched_compute")
    orch = LibModule.from_source("a5_orch", 0, _A5_S3_ORCH, required_fn="solve", origin="sham_matched_compute")
    return CompositionalAlgoArtifact(arm="A5_SHAM", track="S3_XAG_COMP", generation=0, modules=(mod,), orchestrator=orch)


def synthesize_s3_with_artifact(
    n_inputs: int,
    targets: Sequence[int],
    artifact: Optional[CompositionalAlgoArtifact],
    seed: int = 0,
    op_budget: int = DEFAULT_S3_OP_BUDGET,
) -> Tuple[XAGCircuit, Dict[str, Any]]:
    """Unified 100%-deterministic, strictly-monotonic Sprint 3 evaluator."""
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
        }

    api_factory = make_metered_xag_api_factory(n_inputs, clean_targets)
    best, meta = run_compositional_artifact(
        initial_solution=base,
        artifact=artifact,
        domain_api_factory=api_factory,
        call_args_fn=lambda cur, api, lib, bud: (cur, n_inputs, clean_targets, seed, api, lib, bud),
        verify_fn=lambda c: isinstance(c, XAGCircuit) and c.n_inputs == n_inputs and verify_truth_tables(c, clean_targets),
        cost_fn=lambda c: int(c.gate_count()),
        op_budget=op_budget,
    )
    assert verify_truth_tables(best, clean_targets)
    return best, meta
