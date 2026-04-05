"""
racing.py — Multi-stage racing evaluation for Apollo v2c.

Successive halving: evaluate all organisms on a few tasks first,
kill the bottom 50%, repeat with more tasks, until survivors get
full evaluation. ~4x reduction in total task evaluations.
"""

import numpy as np
from logger import log_info, log_debug


def evaluate_with_racing(population, compiled_sources, tasks, config,
                         ncd_baseline, archive, reference_tasks, generation,
                         ablation_cache=None,
                         compute_fitness_fn=None,
                         evaluate_fn=None,
                         compute_sig_fn=None,
                         quick_screen_fn=None,
                         FitnessVector_cls=None):
    """Multi-stage racing evaluation. Returns list of FitnessVectors.

    Args:
        population: list of Organism objects
        compiled_sources: list of source code strings (or None)
        tasks: full list of evaluation tasks
        config: configuration dict
        ncd_baseline: NCD baseline dict
        archive: NoveltyArchive instance
        reference_tasks: tasks for behavioral signatures
        generation: current generation number
        ablation_cache: optional dict for caching ablation results
        compute_fitness_fn: callable(task_results, ncd_baseline, ...) -> FitnessVector
        evaluate_fn: callable(source, tasks, timeout) -> list[dict]
        compute_sig_fn: callable(source, tasks) -> np.ndarray
        quick_screen_fn: callable(source, tasks, timeout) -> bool
        FitnessVector_cls: FitnessVector class for default vectors

    Returns:
        list of FitnessVector, one per organism
    """
    n_pop = len(population)
    timeout = config.get("sandbox_timeout_seconds", 0.5)

    # Stage config — survival_rate=1.0 means keep all remaining
    stages = [
        {"n_tasks": min(10, len(tasks)), "survival_rate": 0.5},
        {"n_tasks": min(30, len(tasks)), "survival_rate": 0.5},
        {"n_tasks": len(tasks), "survival_rate": 1.0},
    ]

    # All organisms start active
    active_indices = list(range(n_pop))
    task_results = [None] * n_pop
    fitness_vectors = [None] * n_pop

    # Compute behavioral signatures for all organisms (needed for novelty)
    sig_tasks = reference_tasks[:config.get("signature_task_count", 15)]
    pop_sigs = []
    for source in compiled_sources:
        if source and compute_sig_fn:
            sig = compute_sig_fn(source, sig_tasks)
        else:
            sig = np.zeros(len(sig_tasks))
        pop_sigs.append(sig)

    # Assign default fitness for organisms with no compiled source
    for i in range(n_pop):
        if compiled_sources[i] is None:
            fv = FitnessVector_cls(primitive_count=population[i].primitive_count)
            fv.diversity = archive.novelty_score(pop_sigs[i], pop_sigs)
            fitness_vectors[i] = fv
            active_indices = [idx for idx in active_indices if idx != i]

    total_full_evals = n_pop * len(tasks)  # what full eval would cost
    total_actual_evals = 0

    for stage_num, stage in enumerate(stages):
        stage_tasks = tasks[:stage["n_tasks"]]
        active_before = list(active_indices)

        # Evaluate active organisms on this stage's tasks
        for idx in active_indices:
            if evaluate_fn:
                task_results[idx] = evaluate_fn(
                    compiled_sources[idx], stage_tasks, timeout
                )
            else:
                task_results[idx] = []
            total_actual_evals += len(stage_tasks)

        # Rank by accuracy on current tasks
        scores = []
        for idx in active_indices:
            if task_results[idx]:
                correct = sum(1 for r in task_results[idx] if r.get('correct'))
                scores.append((idx, correct / max(len(stage_tasks), 1)))
            else:
                scores.append((idx, 0.0))

        scores.sort(key=lambda x: x[1], reverse=True)

        cutoff = int(len(scores) * stage["survival_rate"])
        cutoff = max(cutoff, 1)  # keep at least 1
        active_indices = [idx for idx, _ in scores[:cutoff]]
        killed = len(active_before) - len(active_indices)

        best_score = scores[0][1] if scores else 0.0
        worst_score = scores[cutoff - 1][1] if scores and cutoff <= len(scores) else 0.0

        log_debug(
            f"Racing stage {stage_num}: {len(stage_tasks)} tasks | "
            f"{len(active_before)} -> {len(active_indices)} survived | "
            f"{killed} eliminated",
            stage="racing", generation=generation,
            data={
                "stage": stage_num,
                "n_tasks": len(stage_tasks),
                "active_before": len(active_before),
                "active_after": len(active_indices),
                "eliminated": killed,
                "best_score": best_score,
                "worst_surviving_score": worst_score,
            }
        )

        # Eliminated organisms get default fitness
        eliminated = [idx for idx, _ in scores[cutoff:]]
        for idx in eliminated:
            if fitness_vectors[idx] is None:
                fv = FitnessVector_cls(primitive_count=population[idx].primitive_count)
                fv.diversity = archive.novelty_score(pop_sigs[idx], pop_sigs)
                # Give partial credit based on stage accuracy
                partial_acc = 0.0
                if task_results[idx]:
                    n_correct = sum(1 for r in task_results[idx] if r.get('correct'))
                    partial_acc = n_correct / max(len(stage_tasks), 1)
                fv.accuracy_margin = partial_acc - ncd_baseline.get('accuracy', 0.0)
                fitness_vectors[idx] = fv

    # Compute full fitness for survivors
    from ncd_counterpressure import ncd_decay_weight, ncd_independence_score
    from ablation import ablation_test, compute_ablation_fitness
    ncd_weight = ncd_decay_weight(generation)

    for idx in active_indices:
        if fitness_vectors[idx] is not None:
            continue  # already assigned

        if task_results[idx] is None:
            task_results[idx] = []

        if compute_fitness_fn:
            fv = compute_fitness_fn(
                task_results[idx], ncd_baseline,
                ncd_weight=ncd_weight,
                primitive_count=population[idx].primitive_count,
            )
        else:
            fv = FitnessVector_cls(primitive_count=population[idx].primitive_count)

        fv.diversity = archive.novelty_score(pop_sigs[idx], pop_sigs)
        fv.ncd_independence = ncd_independence_score(task_results[idx])

        # Ablation
        if ablation_cache is not None and population[idx].genome_id in ablation_cache:
            fv.ablation_delta = ablation_cache[population[idx].genome_id]
        elif (generation >= config.get("ablation_activation_gen", 100)
              and fv.accuracy_margin > 0
              and generation % config.get("ablation_interval", 5) == 0):
            try:
                abl_results = ablation_test(
                    population[idx], compiled_sources[idx],
                    reference_tasks, timeout
                )
                fv.ablation_delta = compute_ablation_fitness(abl_results)
                fv.ablation_details = {
                    r.node_id: r.output_change_fraction for r in abl_results
                }
                if ablation_cache is not None:
                    ablation_cache[population[idx].genome_id] = fv.ablation_delta
            except Exception:
                pass

        fitness_vectors[idx] = fv

    # Fill any remaining None entries
    for i in range(n_pop):
        if fitness_vectors[i] is None:
            fitness_vectors[i] = FitnessVector_cls(
                primitive_count=population[i].primitive_count
            )

    total_evals_saved = total_full_evals - total_actual_evals
    savings_pct = (total_evals_saved / max(total_full_evals, 1)) * 100
    log_info(
        f"Racing complete: {total_evals_saved} evals saved ({savings_pct:.0f}% reduction)",
        stage="racing", generation=generation,
    )

    return fitness_vectors
