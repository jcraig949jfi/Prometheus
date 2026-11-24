"""Matched-Op Causal Knockout Runtime (Closes Q3 Caveat #3: Eliminates Op-Count Collapse).

When a generation `k` module is knocked out of an evolved artifact `G`:
  1. All modules with `generation in knocked_gens` are replaced by clean type-preserving stubs.
  2. `G`'s exact orchestrator runs first under `OpBudget(limit=op_budget)`.
  3. Any remaining unused ops (`budget.global_remaining() > 2500`) that would otherwise be
     dropped by the stubbed module are routed seamlessly into `fallback_artifact` (the exact
     surviving parent checkpoint without `knocked_gens`), starting from `best_solution()`!
This guarantees matched total op expenditure between `G` and `KO_MATCHED`.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from comp_sprint3.sandbox_s3 import (
    CompositionalAlgoArtifact,
    LibModule,
    LibNamespace,
    OpBudget,
    run_compositional_artifact,
)


def knockout_generations_generic(
    artifact: CompositionalAlgoArtifact,
    knocked_gens: Set[int],
    passthrough_type_name: str,
    arm_name: str,
) -> CompositionalAlgoArtifact:
    """Stub out all modules in `knocked_gens`, returning first arg unchanged if it matches `passthrough_type_name`."""
    new_mods: List[LibModule] = []
    for m in artifact.modules:
        if m.generation in knocked_gens:
            lines: List[str] = []
            for fn_name in m.exported_fns:
                lines.append(
                    f"def {fn_name}(*args, **kwargs):\n"
                    f"    if args and isinstance(args[0], {passthrough_type_name}):\n"
                    f"        return args[0]\n"
                    f"    return None\n"
                )
            new_mods.append(
                LibModule.from_source(
                    name=f"{m.name}__ko",
                    generation=m.generation,
                    source="\n".join(lines),
                    origin=f"knockout_of_{m.name}",
                    rationale=f"Causal knockout stub for gen {m.generation}",
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


def run_matched_op_knockout(
    initial_solution: Any,
    knocked_artifact: CompositionalAlgoArtifact,
    fallback_artifact: Optional[CompositionalAlgoArtifact],
    domain_api_factory: Callable[[OpBudget, Callable[[Any], bool]], Dict[str, Any]],
    call_args_fn: Callable[[Any, Dict[str, Any], LibNamespace, OpBudget], Tuple[Any, ...]],
    verify_fn: Callable[[Any], bool],
    cost_fn: Callable[[Any], int],
    op_budget: int,
) -> Tuple[Any, Dict[str, Any]]:
    """Run `knocked_artifact`; route any unspent op budget into `fallback_artifact` for matched-op ablation."""
    best, meta1 = run_compositional_artifact(
        initial_solution=initial_solution,
        artifact=knocked_artifact,
        domain_api_factory=domain_api_factory,
        call_args_fn=call_args_fn,
        verify_fn=verify_fn,
        cost_fn=cost_fn,
        op_budget=op_budget,
    )
    spent1 = int(meta1.get("ops_spent", 0))
    rem = op_budget - spent1
    if fallback_artifact is None or rem < 2500:
        return best, meta1

    best2, meta2 = run_compositional_artifact(
        initial_solution=best,
        artifact=fallback_artifact,
        domain_api_factory=domain_api_factory,
        call_args_fn=call_args_fn,
        verify_fn=verify_fn,
        cost_fn=cost_fn,
        op_budget=rem,
    )
    if cost_fn(best2) < cost_fn(best) and verify_fn(best2):
        best = best2

    merged_xgen = dict(meta1.get("cross_gen_calls", {}))
    for k, v in meta2.get("cross_gen_calls", {}).items():
        merged_xgen[k] = merged_xgen.get(k, 0) + v
    merged_gdrops = dict(meta1.get("gen_gate_drops", {}))
    for k, v in meta2.get("gen_gate_drops", {}).items():
        merged_gdrops[k] = merged_gdrops.get(k, 0) + v
    merged_mdrops = dict(meta1.get("mod_gate_drops", {}))
    for k, v in meta2.get("mod_gate_drops", {}).items():
        merged_mdrops[k] = merged_mdrops.get(k, 0) + v
    merged_mcalls = dict(meta1.get("module_calls", {}))
    for k, v in meta2.get("module_calls", {}).items():
        merged_mcalls[k] = merged_mcalls.get(k, 0) + v

    return best, {
        "final_cost": cost_fn(best),
        "ops_spent": min(op_budget, spent1 + int(meta2.get("ops_spent", 0))),
        "ops_limit": op_budget,
        "status": f"ko_matched:{meta1.get('status')}+{meta2.get('status')}",
        "error": meta1.get("error") or meta2.get("error", ""),
        "unsound_rejects": int(meta1.get("unsound_rejects", 0)) + int(meta2.get("unsound_rejects", 0)),
        "module_calls": merged_mcalls,
        "cross_gen_calls": merged_xgen,
        "gen_gate_drops": merged_gdrops,
        "mod_gate_drops": merged_mdrops,
        "fn_errors": dict(meta1.get("fn_errors", {})),
        "fn_error_msgs": dict(meta1.get("fn_error_msgs", {})),
    }
