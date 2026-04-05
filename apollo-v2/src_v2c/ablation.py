"""
ablation.py — The bypass killer.

For each primitive in an organism, remove it, recompile, rerun on reference tasks,
measure how many outputs change. If ANY primitive changes < 20% of outputs,
that primitive is decorative (not load-bearing) and the organism is penalized.

The ablation delta fitness = min(change_fraction) across all primitives.
"""

from dataclasses import dataclass
from genome import Organism, PrimitiveCall


@dataclass
class AblationResult:
    primitive_name: str
    node_id: str
    output_change_fraction: float  # Fraction of tasks where top candidate changed
    passes: bool                   # True if change_fraction >= ABLATION_THRESHOLD


ABLATION_THRESHOLD = 0.20


def ablation_test(organism: Organism, compiled_source: str,
                  reference_tasks: list[dict],
                  timeout: float = 0.5) -> list[AblationResult]:
    """Test each primitive for load-bearing status.

    Args:
        organism: The organism to test
        compiled_source: Pre-compiled source (for baseline run)
        reference_tasks: Tasks to evaluate on
        timeout: Per-task timeout

    Returns:
        List of AblationResult, one per primitive node.
    """
    from compiler import compile_organism
    from sandbox import safe_evaluate

    # Step 1: Get baseline outputs (top candidate per task)
    baseline_outputs = _get_outputs(compiled_source, reference_tasks, timeout)
    if not baseline_outputs:
        return []

    results = []

    # Step 2: For each primitive, ablate and compare
    for pc in organism.primitive_sequence:
        ablated_org = _ablate_node(organism, pc.node_id)

        if ablated_org.primitive_count == 0:
            # Removing this node empties the organism — it's critical
            results.append(AblationResult(
                primitive_name=pc.primitive_name,
                node_id=pc.node_id,
                output_change_fraction=1.0,
                passes=True,
            ))
            continue

        # Compile ablated organism
        cr = compile_organism(ablated_org)
        if not cr.success:
            # Can't compile without this primitive — it's critical
            results.append(AblationResult(
                primitive_name=pc.primitive_name,
                node_id=pc.node_id,
                output_change_fraction=1.0,
                passes=True,
            ))
            continue

        # Run ablated organism
        ablated_outputs = _get_outputs(cr.source_code, reference_tasks, timeout)

        # Compare outputs
        if not ablated_outputs or len(ablated_outputs) != len(baseline_outputs):
            # Runtime failure = primitive was needed
            results.append(AblationResult(
                primitive_name=pc.primitive_name,
                node_id=pc.node_id,
                output_change_fraction=1.0,
                passes=True,
            ))
            continue

        n_changed = sum(
            1 for b, a in zip(baseline_outputs, ablated_outputs)
            if b != a
        )
        change_fraction = n_changed / len(baseline_outputs)

        results.append(AblationResult(
            primitive_name=pc.primitive_name,
            node_id=pc.node_id,
            output_change_fraction=change_fraction,
            passes=change_fraction >= ABLATION_THRESHOLD,
        ))

    return results


def compute_ablation_fitness(results: list[AblationResult]) -> float:
    """Compute the ablation fitness dimension.

    Returns the MINIMUM change fraction across all primitives.
    An organism is only as strong as its weakest primitive.
    """
    if not results:
        return 0.0
    return min(r.output_change_fraction for r in results)


def _get_outputs(source_code: str, tasks: list[dict],
                 timeout: float) -> list[str]:
    """Run organism on tasks, return list of top-candidate strings."""
    from sandbox import safe_evaluate

    outputs = []
    for task in tasks:
        r = safe_evaluate(source_code, task['prompt'], task['candidates'], timeout)
        results = r.get('results', [])
        if results:
            outputs.append(results[0]['candidate'])
        else:
            outputs.append("")
    return outputs


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
