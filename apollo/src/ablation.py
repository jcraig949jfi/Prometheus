"""
ablation.py — The bypass killer.

2026-05-22 — STRENGTHENED. The previous metric (output_change_fraction) was
gameable: a primitive could change the output string without improving
correctness, and the gen-2960 baseline-matrix experiment confirmed Apollo had
evolved exactly that hole — decorative scaffolds where removing the "load-
bearing" first primitive often IMPROVED accuracy.

New metric: accuracy_delta = baseline_acc - ablated_acc. A primitive only
passes the gate if removing it CAUSES AN ACCURACY DROP (i.e., it was
contributing to correct answers, not just changing output strings).

Both metrics are computed and logged; `passes` and the fitness dimension
now key off accuracy_delta.
"""

from dataclasses import dataclass
from genome import Organism, PrimitiveCall


@dataclass
class AblationResult:
    primitive_name: str
    node_id: str
    output_change_fraction: float  # Fraction of tasks where top candidate changed (legacy, still logged)
    accuracy_delta: float          # baseline_acc - ablated_acc. Positive = primitive was load-bearing for correctness.
    passes: bool                   # True if accuracy_delta >= ACCURACY_DELTA_THRESHOLD


# Old gate: output_change_fraction >= 0.20 (trivial to satisfy)
# New gate: removing the primitive drops accuracy by at least 5 points
ACCURACY_DELTA_THRESHOLD = 0.05
ABLATION_THRESHOLD = ACCURACY_DELTA_THRESHOLD  # alias for downstream readers


def ablation_test(organism: Organism, compiled_source: str,
                  reference_tasks: list[dict],
                  timeout: float = 0.5) -> list[AblationResult]:
    """Test each primitive for load-bearing status by ACCURACY drop.

    Args:
        organism: The organism to test
        compiled_source: Pre-compiled source (for baseline run)
        reference_tasks: Tasks to evaluate on
        timeout: Per-task timeout

    Returns:
        List of AblationResult, one per primitive node. accuracy_delta is
        the load-bearing signal; output_change_fraction is kept for logging.
    """
    from compiler import compile_organism

    # Baseline: outputs + correctness on each task
    baseline_outputs, baseline_correct = _get_outputs_and_correct(
        compiled_source, reference_tasks, timeout)
    if not baseline_outputs:
        return []
    baseline_acc = sum(baseline_correct) / max(len(baseline_correct), 1)

    results = []

    for pc in organism.primitive_sequence:
        ablated_org = _ablate_node(organism, pc.node_id)

        if ablated_org.primitive_count == 0:
            results.append(AblationResult(
                primitive_name=pc.primitive_name, node_id=pc.node_id,
                output_change_fraction=1.0, accuracy_delta=baseline_acc,
                passes=True,
            ))
            continue

        cr = compile_organism(ablated_org)
        if not cr.success:
            results.append(AblationResult(
                primitive_name=pc.primitive_name, node_id=pc.node_id,
                output_change_fraction=1.0, accuracy_delta=baseline_acc,
                passes=True,
            ))
            continue

        ablated_outputs, ablated_correct = _get_outputs_and_correct(
            cr.source_code, reference_tasks, timeout)

        if not ablated_outputs or len(ablated_outputs) != len(baseline_outputs):
            results.append(AblationResult(
                primitive_name=pc.primitive_name, node_id=pc.node_id,
                output_change_fraction=1.0, accuracy_delta=baseline_acc,
                passes=True,
            ))
            continue

        n_changed = sum(1 for b, a in zip(baseline_outputs, ablated_outputs) if b != a)
        change_fraction = n_changed / len(baseline_outputs)

        ablated_acc = sum(ablated_correct) / max(len(ablated_correct), 1)
        accuracy_delta = baseline_acc - ablated_acc  # positive = primitive was load-bearing

        results.append(AblationResult(
            primitive_name=pc.primitive_name, node_id=pc.node_id,
            output_change_fraction=change_fraction,
            accuracy_delta=accuracy_delta,
            passes=accuracy_delta >= ACCURACY_DELTA_THRESHOLD,
        ))

    return results


def compute_ablation_fitness(results: list[AblationResult]) -> float:
    """Ablation fitness = MIN accuracy_delta across primitives.

    2026-05-22 change: was min(output_change_fraction). The gen-2960
    baseline-matrix experiment showed that gate was gameable: organisms
    had high output_change_fraction with zero accuracy contribution.
    """
    if not results:
        return 0.0
    return min(r.accuracy_delta for r in results)


def _get_outputs_and_correct(source_code: str, tasks: list[dict],
                             timeout: float):
    """Run organism on tasks; return (top_candidate_strings, correctness_bits)."""
    from sandbox import safe_evaluate

    outputs = []
    correct_bits = []
    for task in tasks:
        r = safe_evaluate(source_code, task['prompt'], task['candidates'], timeout)
        results = r.get('results', [])
        if results:
            top = results[0]['candidate']
            outputs.append(top)
            correct_bits.append(1 if top == task.get('correct') else 0)
        else:
            outputs.append("")
            correct_bits.append(0)
    return outputs, correct_bits


# Backward-compat shim for callers that still expect the old signature
def _get_outputs(source_code: str, tasks: list[dict], timeout: float):
    outs, _ = _get_outputs_and_correct(source_code, tasks, timeout)
    return outs


def _ablate_node(organism: Organism, remove_node_id: str) -> Organism:
    """Create a new organism with one node removed.

    Downstream nodes that referenced the removed node's output
    get their input replaced with a default value.
    """
    ablated = organism.clone()

    # Remove the target node
    ablated.primitive_sequence = [
        pc for pc in ablated.primitive_sequence
        if pc.node_id != remove_node_id
    ]

    # Fix dangling references in remaining nodes
    removed_ref = f"{remove_node_id}.output"
    for pc in ablated.primitive_sequence:
        for param, source in list(pc.input_mapping.items()):
            if source == removed_ref:
                # Replace with a parameter reference (fallback)
                fallback_key = f"ablation_default_{pc.node_id}_{param}"
                pc.input_mapping[param] = f"param.{fallback_key}"
                ablated.parameters[fallback_key] = 0.0

    # Clean wiring
    ablated.wiring = {
        k: v for k, v in ablated.wiring.items()
        if not k.startswith(f"{remove_node_id}.")
        and not v.startswith(f"{remove_node_id}.")
    }

    return ablated
