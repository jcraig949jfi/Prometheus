"""
apollo.py — Main evolutionary loop. Entry point for Apollo v0.3.

Uses whole forge tools as organisms. Mutations modify parameters
and swap methods between tools. LLM mutation for structural changes.
"""

import sys
import os
import random
import time
import copy
import yaml
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from genome import Genome, create_genome_from_tool, create_seed_population
from compiler import compile_from_source, smoke_test, extract_parameters
from sandbox import check_imports, evaluate_organism_on_tasks, quick_screen
from task_manager import TaskManager
from fitness import compute_ncd_baseline, compute_fitness, FitnessVector
from novelty import NoveltyArchive, compute_behavioral_signature
from selection import nsga2_select, select_elites
from mutation import mutate, drift, point_mutate, crossover, method_swap
from mutation_llm import LLMMutator
from logger import log_organism, log_dashboard
from checkpointer import save_checkpoint, load_checkpoint, checkpoint_exists


def load_config(path: str = None) -> dict:
    if path is None:
        path = str(Path(__file__).parent.parent / "configs" / "manifest.yaml")
    with open(path, 'r') as f:
        return yaml.safe_load(f)['apollo']


def validate_organism(genome: Genome, tasks: list, config: dict) -> bool:
    """Validate an organism compiles, runs, and discriminates."""
    result = compile_from_source(genome.source_code)
    if not result.success:
        return False

    ok, err = check_imports(genome.source_code)
    if not ok:
        return False

    if tasks:
        runs, disc = smoke_test(genome.source_code, tasks[0])
        return runs  # Don't require discrimination for seed population

    return True


def evaluate_population(population: list, tasks: list, ncd_baseline: dict,
                         archive: NoveltyArchive, reference_tasks: list,
                         generation: int, config: dict) -> list:
    """Evaluate all organisms. Returns fitness vectors."""
    fitness_vectors = []
    pop_sigs = []

    # Compute behavioral signatures
    for genome in population:
        sig = compute_behavioral_signature(genome.source_code, reference_tasks)
        pop_sigs.append(sig)

    for i, genome in enumerate(population):
        # Quick screen
        screen_tasks = tasks[:config.get('quick_screen_count', 3)]
        if not quick_screen(genome.source_code, screen_tasks,
                           config.get('sandbox_timeout_seconds', 0.5)):
            fv = FitnessVector()
            fv.novelty_score = archive.novelty_score(pop_sigs[i], pop_sigs)
            fv.gene_count = genome.gene_count
            fitness_vectors.append(fv)
            continue

        # Full evaluation
        task_results = evaluate_organism_on_tasks(
            genome.source_code, tasks, config.get('sandbox_timeout_seconds', 0.5)
        )

        # NCD independence: check gene traces for FALLBACK usage
        n_tasks = len(task_results)
        n_ncd = sum(1 for r in task_results if 'ncd' in str(r.get('gene_trace', '')).lower())
        ncd_independence = 1.0 - (n_ncd / n_tasks) if n_tasks > 0 else 0.0

        fitness = compute_fitness(
            task_results, ncd_baseline,
            ncd_independence=ncd_independence,
            ncd_independence_weight=config.get('ncd_independence_weight', 0.5),
            gene_count=genome.gene_count,
        )

        # Novelty
        fitness.novelty_score = archive.novelty_score(pop_sigs[i], pop_sigs)
        fitness.gene_count = genome.gene_count

        fitness_vectors.append(fitness)

    return fitness_vectors


def produce_offspring(population: list, fitness_vectors: list,
                      generation: int, config: dict,
                      llm_mutator=None) -> list:
    """Generate offspring via mutation and crossover."""
    children = []
    n = config.get('offspring_per_generation', 50)
    crossover_rate = config.get('crossover_rate', 0.7) if generation >= config.get('mild_structural_until_gen', 30) else 0.0

    for _ in range(n):
        if random.random() < crossover_rate and len(population) >= 2:
            # LLM-assisted crossover when available
            p1, p2 = random.sample(population, 2)
            if llm_mutator and llm_mutator.is_loaded and random.random() < 0.5:
                try:
                    new_src = llm_mutator.combine(p1.source_code, p2.source_code)
                    if new_src:
                        child = p1.clone()
                        child.source_code = new_src
                        child.lineage['parent_ids'] = [p1.genome_id, p2.genome_id]
                        child.lineage['mutations_applied'] = ['llm_crossover']
                    else:
                        child = crossover(p1, p2)
                except Exception:
                    child = crossover(p1, p2)
            else:
                child = crossover(p1, p2)
        else:
            parent = random.choice(population)
            child = parent.clone()
            child.lineage['parent_ids'] = [parent.genome_id]

        child = mutate(child, population, generation, config, llm_mutator=llm_mutator)
        children.append(child)

    return children


def run_viability_spike(population: list, tasks: list, config: dict) -> float:
    """Test viability of method-swap mutations."""
    print("\n=== VIABILITY SPIKE ===")
    n_samples = min(100, len(population) * 5)
    viable = 0

    for i in range(n_samples):
        parent = random.choice(population)
        child = method_swap(parent.clone(), population)
        result = compile_from_source(child.source_code)
        if result.success:
            runs, disc = smoke_test(child.source_code, tasks[0])
            if runs:
                viable += 1

    rate = viable / n_samples if n_samples > 0 else 0.0
    print(f"Method-swap viability: {viable}/{n_samples} = {rate:.1%}")
    return rate


def run_apollo():
    """Main entry point."""
    config = load_config()
    print("=" * 60)
    print("APOLLO v0.3 — Evolutionary Reasoning System")
    print("=" * 60)

    # ── Task Manager ──────────────────────────────────────────
    print("\nInitializing task manager...")
    task_mgr = TaskManager(
        trap_gen_path=config['trap_generator_path'],
        evolution_seed=config['evolution_seed'],
        held_out_seed=config['held_out_seed'],
        n_seed_traps=config['n_seed_traps'],
        n_rotating=config['n_rotating_tasks'],
        rotation_interval=config['task_rotation_interval'],
    )
    evolution_tasks = task_mgr.get_evolution_tasks()
    reference_tasks = task_mgr.get_reference_tasks()
    held_out_tasks = task_mgr.get_held_out_tasks()
    print(f"  Evolution: {len(evolution_tasks)} | Reference: {len(reference_tasks)} | Held-out: {len(held_out_tasks)}")

    # ── NCD Baseline ──────────────────────────────────────────
    print("\nComputing NCD baseline...")
    ncd_baseline = compute_ncd_baseline(evolution_tasks)
    ncd_held_out = compute_ncd_baseline(held_out_tasks)
    print(f"  NCD accuracy: {ncd_baseline['accuracy']:.1%} (evolution) / {ncd_held_out['accuracy']:.1%} (held-out)")

    # ── Seed Population ───────────────────────────────────────
    print("\nLoading seed population from forge_v3...")
    scores_path = str(Path(__file__).parent.parent / "v3_seed_candidates.json")
    population = create_seed_population(config['forge_library_path'], config['population_size'],
                                        scores_path=scores_path)
    print(f"  Loaded {len(population)} organisms")

    # Validate: just check they compile and run
    valid = []
    for g in population:
        try:
            r = compile_from_source(g.source_code)
            if r.success:
                ns = {}
                exec(g.source_code, ns)
                tool = ns['ReasoningTool']()
                results = tool.evaluate(evolution_tasks[0]['prompt'], evolution_tasks[0]['candidates'])
                if results:
                    valid.append(g)
        except:
            pass
    population = valid
    print(f"  Valid: {len(population)}")

    if len(population) < 5:
        print("CRITICAL: Too few valid organisms. Aborting.")
        return

    # ── LLM Mutator ────────────────────────────────────────────
    llm_mutator = None
    llm_model = config.get('llm_model', 'Qwen/Qwen2.5-Coder-3B-Instruct')
    print(f"\nLoading LLM mutator: {llm_model} (CPU mode)")
    try:
        llm_mutator = LLMMutator(model_name=llm_model, device="cpu")
        llm_mutator.load()
    except Exception as e:
        print(f"  LLM load failed: {e}. Running AST-only.")
        llm_mutator = None

    # ── Viability Spike ───────────────────────────────────────
    viability = run_viability_spike(population, evolution_tasks, config)

    # ── Initialize Archive + State ────────────────────────────
    archive = NoveltyArchive(
        max_size=config.get('novelty_archive_max_size', 500),
        k=config.get('novelty_k_nearest', 15),
        threshold=config.get('novelty_archive_threshold', 0.3),
    )
    generation = 0

    if checkpoint_exists():
        print("\nRecovering from checkpoint...")
        cp = load_checkpoint()
        if cp:
            population, archive, generation = cp
            print(f"  Resumed at generation {generation}")

    # ── Diversity-Only Warmup ─────────────────────────────────
    warmup_gens = config.get('diversity_warmup_generations', 50)
    if generation < warmup_gens:
        print(f"\n=== DIVERSITY WARMUP (gen {generation+1}-{warmup_gens}) ===")
        while generation < warmup_gens:
            generation += 1
            children = produce_offspring(population, [], generation, config, llm_mutator=None)  # No LLM during warmup
            # Keep only valid children
            children = [c for c in children if compile_from_source(c.source_code).success]

            all_orgs = population + children
            sigs = [compute_behavioral_signature(o.source_code, reference_tasks) for o in all_orgs]
            novelty_scores = [archive.novelty_score(s, sigs) for s in sigs]

            # Select by novelty
            paired = sorted(zip(all_orgs, novelty_scores), key=lambda x: x[1], reverse=True)
            population = [p[0] for p in paired[:config['population_size']]]

            for s in sigs:
                archive.maybe_add(s)

            if generation % 10 == 0:
                print(f"  Gen {generation}: pop={len(population)}, archive={archive.size}")
                save_checkpoint(population, archive, generation)

    # ── Main Evolution Loop ───────────────────────────────────
    print(f"\n=== STRUCTURAL EVOLUTION (gen {generation+1}+) ===")
    best_held_out = -1.0
    start_time = time.time()

    while True:
        generation += 1
        gen_start = time.time()

        # Task rotation
        if task_mgr.maybe_rotate(generation):
            evolution_tasks = task_mgr.get_evolution_tasks()
            ncd_baseline = compute_ncd_baseline(evolution_tasks)

        # Evaluate population
        fitness_vectors = evaluate_population(
            population, evolution_tasks, ncd_baseline, archive,
            reference_tasks, generation, config
        )

        # Produce offspring
        children = produce_offspring(population, fitness_vectors, generation, config, llm_mutator=llm_mutator)
        children = [c for c in children if compile_from_source(c.source_code).success]
        compiled_count = len(children)

        # Evaluate children
        child_fitness = evaluate_population(
            children, evolution_tasks, ncd_baseline, archive,
            reference_tasks, generation, config
        )

        # Selection with elitism
        all_orgs = population + children
        all_fitness = fitness_vectors + child_fitness
        gene_counts = [o.gene_count for o in all_orgs]

        elite_indices = select_elites(all_fitness, k=config['elite_count'], gene_counts=gene_counts)
        elites = [all_orgs[i] for i in elite_indices]

        remaining_idx = [i for i in range(len(all_orgs)) if i not in elite_indices]
        remaining_orgs = [all_orgs[i] for i in remaining_idx]
        remaining_fitness = [all_fitness[i] for i in remaining_idx]
        remaining_gc = [remaining_orgs[i].gene_count for i in range(len(remaining_orgs))]

        target = config['population_size'] - len(elites)
        if remaining_fitness and target > 0:
            sel_idx = nsga2_select(remaining_orgs, remaining_fitness, target, remaining_gc)
            survivors = [remaining_orgs[i] for i in sel_idx]
        else:
            survivors = []

        population = elites + survivors

        # Update novelty archive
        for genome in population:
            sig = compute_behavioral_signature(genome.source_code, reference_tasks)
            archive.maybe_add(sig)

        # Logging
        for genome, fv in zip(population[:5], fitness_vectors[:5]):  # Log elites
            log_organism(genome, fv, generation)

        comp_rate = compiled_count / max(config.get('offspring_per_generation', 50), 1)
        log_dashboard(generation, population, all_fitness[:len(population)], archive.size, comp_rate)

        gen_time = time.time() - gen_start

        # Print status
        if generation % 5 == 0 or generation <= 5:
            accs = [fv.adjusted_margin_accuracy for fv in fitness_vectors]
            best_acc = max(accs) if accs else 0
            median_acc = float(np.median(accs)) if accs else 0
            n_self_ref = sum(1 for g in population if g.has_self_referential_wiring())
            elapsed = (time.time() - start_time) / 3600
            print(f"Gen {generation:5d} | pop={len(population):3d} | "
                  f"best={best_acc:+.3f} | med={median_acc:+.3f} | "
                  f"comp={comp_rate:.0%} | archive={archive.size:3d} | "
                  f"self_ref={n_self_ref:2d} | {gen_time:.1f}s | {elapsed:.1f}h")

        # Held-out eval
        if generation % config.get('held_out_eval_interval', 10) == 0:
            best_idx = max(range(len(fitness_vectors)),
                          key=lambda i: fitness_vectors[i].adjusted_margin_accuracy) if fitness_vectors else 0
            if best_idx < len(population):
                ho_results = evaluate_organism_on_tasks(
                    population[best_idx].source_code, held_out_tasks,
                    config.get('sandbox_timeout_seconds', 0.5)
                )
                ho_acc = sum(1 for r in ho_results if r.get('correct')) / len(ho_results) if ho_results else 0
                ho_margin = ho_acc - ncd_held_out['accuracy']
                if ho_margin > best_held_out:
                    best_held_out = ho_margin
                    print(f"  ** New best held-out: margin={ho_margin:+.3f} (raw={ho_acc:.1%}) **")

        # Checkpoint
        if generation % config.get('checkpoint_interval', 10) == 0:
            save_checkpoint(population, archive, generation)

        # Success check (only print once)
        if best_held_out > 0 and generation == config.get('held_out_eval_interval', 10):
            print(f"\n  >>> CRITERION 1: Seed organism already beats NCD on held-out (margin={best_held_out:+.3f}). Watching for improvement. <<<\n")

        max_gen = config.get('max_generations')
        if max_gen and generation >= max_gen:
            print(f"\nReached max generations ({max_gen}). Stopping.")
            break


if __name__ == '__main__':
    import multiprocessing as mp
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass
    run_apollo()
