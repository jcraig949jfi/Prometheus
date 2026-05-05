"""ergon.learner.tools.inspect_archive_elites — per-cell elite inspection harness.

Per Iter 7 / Task #80 (originally #63). The archive holds the BEST genome
seen for each (canonicalizer_subclass, dag_entropy, output_type, magnitude,
canonical_form_distance) cell. The promotion ledger persists EVERY substrate-
PASS event; this harness inspects the WINNERS.

Usage (programmatic):
    from ergon.learner.tools.inspect_archive_elites import (
        render_archive_markdown,
    )
    md = render_archive_markdown(archive, evaluator=optional_evaluator)

The harness can also re-run a trial in-line and inspect the resulting
archive — see __main__ block.

Output: a markdown table grouped by canonicalizer_subclass, with one row
per cell elite showing: cell coordinate, fitness, content_hash prefix,
operator class that won the cell, and (for predicate domain) the
predicate the genome encodes.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ergon.learner.archive import MAPElitesArchive
from ergon.learner.descriptor import (
    CANONICALIZER_SUBCLASSES,
    OUTPUT_TYPE_SIGNATURES,
)
from ergon.learner.genome import Genome


def render_archive_markdown(
    archive: MAPElitesArchive,
    title: str = "Archive elite inspection",
    predicate_fn: Optional[Callable[[Genome], Dict[str, Any]]] = None,
) -> str:
    """Render the archive's cell elites as a grouped markdown report.

    predicate_fn (optional): for the predicate domain, pass
    `genome_to_predicate` to display each elite's predicate.
    """
    grouped: Dict[int, List[Any]] = defaultdict(list)
    for entry in archive.all_elites():
        grouped[entry.cell_coordinate.canonicalizer_subclass].append(entry)

    lines = [
        f"# {title}",
        "",
        f"- Total cells filled: **{archive.n_cells_filled()}**",
    ]
    if archive.cells:
        op_counts = archive.operator_fill_count()
        lines.append("- Cells by winning operator class:")
        for op, n in sorted(op_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  - {op}: {n}")
    lines.append("")

    for cs_idx in sorted(grouped.keys()):
        if cs_idx < 0 or cs_idx >= len(CANONICALIZER_SUBCLASSES):
            cs_label = f"out-of-band ({cs_idx})"
        else:
            cs_label = CANONICALIZER_SUBCLASSES[cs_idx]
        cells = grouped[cs_idx]
        lines.append(f"## {cs_label} ({len(cells)} cells)")
        lines.append("")
        # Header
        if predicate_fn is not None:
            lines.append(
                "| dag_h | type | mag | dist | fitness "
                "| op | n_evals | hash | predicate |"
            )
            lines.append("|---|---|---|---|---|---|---|---|---|")
        else:
            lines.append(
                "| dag_h | type | mag | dist | fitness | op | n_evals | hash |"
            )
            lines.append("|---|---|---|---|---|---|---|---|")
        # Sort by fitness tuple desc, so top-fitness cells first
        cells.sort(
            key=lambda e: e.fitness.to_tuple(),
            reverse=True,
        )
        for entry in cells:
            cc = entry.cell_coordinate
            type_label = (
                OUTPUT_TYPE_SIGNATURES[cc.output_type_signature]
                if 0 <= cc.output_type_signature < len(OUTPUT_TYPE_SIGNATURES)
                else f"oob({cc.output_type_signature})"
            )
            fit = entry.fitness
            fit_str = (
                f"({fit.battery_survival_count},{fit.band_concentration_tier},"
                f"{fit.continuous_signal_score:.2f},{fit.cost_amortized_score:.2f})"
            )
            row_prefix = (
                f"| {cc.dag_entropy_bucket} "
                f"| {type_label} "
                f"| {cc.magnitude_bucket} "
                f"| {cc.canonical_form_distance_bucket} "
                f"| {fit_str} "
                f"| {entry.operator_class} "
                f"| {entry.n_evaluations} "
                f"| `{entry.content_hash[:8]}` "
            )
            if predicate_fn is not None:
                genome = archive.get_genome(entry.content_hash)
                pred = predicate_fn(genome) if genome is not None else {}
                lines.append(row_prefix + f"| `{pred}` |")
            else:
                lines.append(row_prefix + "|")
        lines.append("")
    return "\n".join(lines)


def render_archive_summary(archive: MAPElitesArchive) -> str:
    """One-line summary."""
    n = archive.n_cells_filled()
    op_counts = archive.operator_fill_count()
    op_str = ", ".join(
        f"{op}={c}" for op, c in sorted(op_counts.items(), key=lambda x: -x[1])
    )
    return f"archive: {n} cells filled (by op: {op_str})"


def run_inspection_on_obstruction_trial(
    seed: int = 42, n_episodes: int = 1000
) -> str:
    """Run a fresh predicate trial and inspect the resulting archive.

    Reproduces the iter15 setup but with a single seed and produces an
    inspection report at the end.
    """
    import math
    import random

    from ergon.learner.archive import FitnessTuple
    from ergon.learner.descriptor import (
        EvaluationResult,
        compute_cell_coordinate,
    )
    from ergon.learner.genome_evaluator import ObstructionBindEvalEvaluator
    from ergon.learner.operators.anti_prior import AntiPriorOperator
    from ergon.learner.operators.predicate_symbolic import (
        PredicateSymbolicOperator,
    )
    from ergon.learner.operators.structural import StructuralOperator
    from ergon.learner.operators.uniform import UniformOperator
    from ergon.learner.scheduler import OperatorScheduler
    from ergon.learner.trials.trial_3_obstruction_smoke import (
        genome_to_predicate,
        make_obstruction_atom_pool,
    )

    atom_pool = make_obstruction_atom_pool()
    evaluator = ObstructionBindEvalEvaluator(promote_rate=0.001)
    archive = MAPElitesArchive()
    rng = random.Random(seed)

    custom_weights = {
        "structural": 0.65,
        "symbolic": 0.15,
        "uniform": 0.05,
        "structured_null": 0.05,
        "anti_prior": 0.10,
    }
    scheduler = OperatorScheduler(operator_weights=custom_weights, seed=seed)
    operators = {
        "structural": StructuralOperator(),
        "symbolic": PredicateSymbolicOperator(),
        "uniform": UniformOperator(n_atoms_distribution=(1, 4)),
        "structured_null": UniformOperator(n_atoms_distribution=(2, 4)),
        "anti_prior": AntiPriorOperator(),
    }

    for ep in range(n_episodes):
        op_class = scheduler.next_operator_class(ep)
        op_name = op_class if op_class in operators else "uniform"
        operator = operators[op_name]

        parent = None
        if op_name in ("structural", "symbolic") and archive.n_cells_filled() > 0:
            parent_entry = archive.sample_parent(
                rng, substrate_pass_bias=5.0, exploration_rate=0.0
            )
            if parent_entry is not None:
                parent = archive.get_genome(parent_entry.content_hash)

        child = operator.mutate(parent, rng, atom_pool)
        child = Genome(
            nodes=child.nodes,
            target_predicate=child.target_predicate,
            mutation_operator_class=op_name,  # type: ignore[arg-type]
            parent_hash=child.parent_hash,
            metadata=dict(child.metadata),
        )

        kernel_result = evaluator._get_or_evaluate(child)
        obs_data = evaluator.evaluate_obstruction(child)
        lift = obs_data.get("obstruction_lift", 0.0)
        passes = obs_data.get("substrate_pass", False)

        cell = compute_cell_coordinate(child, evaluation=EvaluationResult(
            output_canonicalizer_subclass=kernel_result.output_canonicalizer_subclass,
            output_magnitude=kernel_result.output_magnitude,
            canonical_form_distance_to_catalog=kernel_result.output_canonical_form_distance,
        ))
        cont_score = math.log10(1 + lift)
        fitness = FitnessTuple(
            battery_survival_count=int(passes),
            band_concentration_tier=2 if cell.magnitude_bucket in (1, 2) else 1,
            continuous_signal_score=cont_score,
            cost_amortized_score=1.0,
        )
        archive.submit(child, cell, fitness)

    return render_archive_markdown(
        archive,
        title=f"Iter 17 archive inspection (seed={seed}, n_eps={n_episodes})",
        predicate_fn=genome_to_predicate,
    )


if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    n_episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    md = run_inspection_on_obstruction_trial(seed=seed, n_episodes=n_episodes)
    out = (
        Path(__file__).parent.parent
        / "trials" / f"ARCHIVE_INSPECTION_seed{seed}_n{n_episodes}.md"
    )
    out.write_text(md, encoding="utf-8")
    print(f"Inspection written to: {out}")
    print()
    print(md)
