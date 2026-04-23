"""
health.py — Evolutionary health diagnostics for Apollo.

Logs a comprehensive health report every N generations to detect:
- Genetic monoculture (structural convergence)
- Task-level accuracy distribution (fake gradients)
- Mutation effectiveness (parent→child deltas)
- Dead primitives (never contribute)
- Population fitness distribution (is there a gradient?)
"""

import numpy as np
from collections import Counter
from logger import log_info, log_warning


def compute_health_report(population, compiled_sources, fitness_vectors,
                          evolution_tasks, generation, config,
                          evaluate_fn=None, timeout=0.5):
    """Compute and log evolutionary health metrics.

    Call every 10 generations. Lightweight — reuses existing evaluation data.
    """
    report = {}

    # ── 1. Genetic diversity ─────────────────────────────────────
    # Structural uniqueness: count unique wiring hashes
    wiring_hashes = []
    for org in population:
        h = getattr(org, 'wiring_hash', None)
        if callable(h):
            h = h()  # wiring_hash is a method, not a property
        if h is None:
            # Compute a simple structural hash
            h = hash(tuple(pc.primitive_name for pc in org.primitive_sequence))
        wiring_hashes.append(h)

    unique_structures = len(set(wiring_hashes))
    hash_counts = Counter(wiring_hashes)
    most_common_hash, most_common_count = hash_counts.most_common(1)[0]
    clone_fraction = most_common_count / len(population)

    report["unique_structures"] = unique_structures
    report["clone_fraction"] = round(clone_fraction, 3)
    report["top_3_hashes"] = [(h, c) for h, c in hash_counts.most_common(3)]

    if clone_fraction > 0.4:
        log_warning(
            f"MONOCULTURE: {clone_fraction:.0%} of population shares one structure "
            f"({most_common_count}/{len(population)} clones)",
            stage="health", generation=generation,
        )

    # ── 2. Primitive usage ───────────────────────────────────────
    prim_counts = Counter()
    for org in population:
        for pc in org.primitive_sequence:
            prim_counts[pc.primitive_name] += 1

    total_prims = sum(prim_counts.values())
    report["primitives_in_use"] = len(prim_counts)
    report["top_5_primitives"] = prim_counts.most_common(5)

    # Primitives that appear in >50% of organisms
    overused = [(p, c) for p, c in prim_counts.items()
                if c > len(population) * 0.5]
    if overused:
        report["overused_primitives"] = overused

    # ── 3. Fitness distribution ──────────────────────────────────
    accs = [fv.accuracy_margin for fv in fitness_vectors]
    raw_accs = [fv.raw_accuracy for fv in fitness_vectors]

    report["accuracy_margin"] = {
        "min": round(min(accs), 3),
        "p25": round(float(np.percentile(accs, 25)), 3),
        "median": round(float(np.median(accs)), 3),
        "p75": round(float(np.percentile(accs, 75)), 3),
        "max": round(max(accs), 3),
    }
    report["raw_accuracy"] = {
        "min": round(min(raw_accs), 3),
        "median": round(float(np.median(raw_accs)), 3),
        "max": round(max(raw_accs), 3),
        "pct_above_zero": round(sum(1 for a in raw_accs if a > 0) / len(raw_accs), 3),
    }

    # Fitness spread — is there a gradient?
    acc_spread = max(accs) - min(accs)
    report["accuracy_spread"] = round(acc_spread, 3)
    if acc_spread < 0.01:
        log_warning(
            f"FLAT FITNESS: accuracy spread {acc_spread:.4f} — no selection gradient",
            stage="health", generation=generation,
        )

    # ── 4. Mutation lineage analysis ─────────────────────────────
    mutation_types = Counter()
    for org in population:
        for m in org.lineage.mutations_applied:
            mutation_types[m] += 1

    report["mutation_types_in_pop"] = dict(mutation_types.most_common())

    llm_count = sum(c for m, c in mutation_types.items() if 'llm' in m)
    annealed_count = mutation_types.get('annealed', 0)
    drift_count = mutation_types.get('drift', 0) + mutation_types.get('parameter_mutation', 0)
    report["llm_in_population"] = llm_count
    report["annealed_in_population"] = annealed_count

    if llm_count > 0:
        log_info(
            f"LLM mutations alive: {llm_count} organisms with LLM lineage in population",
            stage="health", generation=generation,
        )

    # ── 5. Task-level accuracy (sample) ──────────────────────────
    # Evaluate the best organism on all tasks to see which ones it solves
    if evaluate_fn and compiled_sources and evolution_tasks:
        best_idx = max(range(len(fitness_vectors)),
                       key=lambda i: fitness_vectors[i].accuracy_margin)
        if compiled_sources[best_idx]:
            try:
                results = evaluate_fn(
                    compiled_sources[best_idx],
                    evolution_tasks[:50],  # Sample 50 tasks
                    timeout,
                )
                if results:
                    by_category = {}
                    for task, result in zip(evolution_tasks[:50], results):
                        cat = task.get('category', 'unknown')
                        if cat not in by_category:
                            by_category[cat] = {"correct": 0, "total": 0}
                        by_category[cat]["total"] += 1
                        if result.get("correct"):
                            by_category[cat]["correct"] += 1

                    solved_cats = {c: d for c, d in by_category.items()
                                   if d["correct"] > 0}
                    zero_cats = [c for c, d in by_category.items()
                                 if d["correct"] == 0]

                    report["categories_solved"] = len(solved_cats)
                    report["categories_zero"] = len(zero_cats)
                    report["per_category"] = {
                        c: f"{d['correct']}/{d['total']}"
                        for c, d in sorted(by_category.items())
                    }

                    if len(solved_cats) <= 3 and len(by_category) > 10:
                        log_warning(
                            f"NARROW: best organism solves only {len(solved_cats)}/{len(by_category)} categories",
                            stage="health", generation=generation,
                        )
            except Exception:
                pass

    # ── 6. Primitive count distribution ──────────────────────────
    prim_sizes = [org.primitive_count for org in population]
    report["primitive_count"] = {
        "min": min(prim_sizes),
        "median": int(np.median(prim_sizes)),
        "max": max(prim_sizes),
    }

    # ── Log the report ───────────────────────────────────────────
    log_info(
        f"HEALTH gen {generation}: "
        f"structs={unique_structures}/{len(population)} | "
        f"clones={clone_fraction:.0%} | "
        f"raw_acc={report['raw_accuracy']['median']:.0%} med / {report['raw_accuracy']['max']:.0%} max | "
        f"spread={acc_spread:.3f} | "
        f"llm_alive={llm_count} | "
        f"prims_used={len(prim_counts)}/{27}",
        stage="health", generation=generation,
        data=report,
    )

    return report
