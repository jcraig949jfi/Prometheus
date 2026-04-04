"""
apollo.py — Main evolutionary loop for Apollo v2.

Evolves routing networks over the 25 Frame H primitives.
6-dimensional NSGA-II with ablation gate as bypass killer.

Phases:
  Warmup (gen 0-50):    Novelty-only, parameter mutation only
  Graduated (gen 50-200): Accuracy activates at 50, ablation at 100
  Main loop (gen 200+):  Full 6D NSGA-II, all mutation types, NCD decay
"""

import sys
import os
import random
import time
import yaml
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from genome import Organism, create_seed_population, random_organism
from gem_converter import create_mixed_seed_population
from compiler import compile_organism
from sandbox import evaluate_organism_on_tasks, safe_evaluate, quick_screen
from task_manager import TaskManager
from fitness import compute_ncd_baseline, compute_fitness, FitnessVector
from novelty import NoveltyArchive, compute_behavioral_signature
from selection import nsga2_select, select_elites
from mutation import mutate, drift, parameter_mutation, crossover
from ablation import ablation_test, compute_ablation_fitness
from ncd_counterpressure import discrimination_test, ncd_decay_weight, ncd_independence_score
from logger import (
    get_logger, reset_logger,
    log_info, log_debug, log_warning, log_error,
    log_organism, log_graveyard, log_dashboard,
)
from checkpointer import save_checkpoint, load_checkpoint, checkpoint_exists

# ── Path resolution ────────��──────────────────────────────────────────

# Project root: F:/Prometheus (or wherever the repo lives)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
APOLLO_DIR = Path(__file__).parent.parent.resolve()


def _resolve_path(rel_path: str, base: Path = PROJECT_ROOT) -> str:
    """Resolve a relative path against a base directory."""
    return str((base / rel_path).resolve())


def _resolve_apollo_path(rel_path: str) -> str:
    """Resolve a path relative to the apollo/ directory."""
    return str((APOLLO_DIR / rel_path).resolve())


# ── Config loading ────────────────────────────────────────────────────

def load_config(path: str = None) -> dict:
    if path is None:
        path = str(APOLLO_DIR / "configs" / "manifest.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)["apollo"]


# ── Helpers ─────────���─────────────────────────────────────────────────

def compile_and_validate(organism: Organism) -> tuple:
    """Compile organism, return (source_code, success)."""
    cr = compile_organism(organism)
    if not cr.success:
        return None, False
    return cr.source_code, True


def evaluate_population(population: list, compiled_sources: list,
                        tasks: list, ncd_baseline: dict,
                        archive: NoveltyArchive, reference_tasks: list,
                        generation: int, config: dict,
                        ablation_cache: dict = None) -> list:
    """Evaluate all organisms on 6 fitness dimensions."""
    timeout = config.get("sandbox_timeout_seconds", 0.5)
    ncd_weight = ncd_decay_weight(generation)
    fitness_vectors = []
    pop_sigs = []

    sig_tasks = reference_tasks[:config.get("signature_task_count", 15)]
    for source in compiled_sources:
        if source:
            sig = compute_behavioral_signature(source, sig_tasks)
        else:
            sig = np.zeros(len(sig_tasks))
        pop_sigs.append(sig)

    for i, (organism, source) in enumerate(zip(population, compiled_sources)):
        if source is None:
            fv = FitnessVector(primitive_count=organism.primitive_count)
            fv.diversity = archive.novelty_score(pop_sigs[i], pop_sigs)
            fitness_vectors.append(fv)
            continue

        screen_tasks = tasks[:config.get("quick_screen_count", 3)]
        if not quick_screen(source, screen_tasks, timeout):
            fv = FitnessVector(primitive_count=organism.primitive_count)
            fv.diversity = archive.novelty_score(pop_sigs[i], pop_sigs)
            fitness_vectors.append(fv)
            continue

        task_results = evaluate_organism_on_tasks(source, tasks, timeout)

        fv = compute_fitness(
            task_results, ncd_baseline,
            ncd_weight=ncd_weight,
            primitive_count=organism.primitive_count,
        )

        fv.diversity = archive.novelty_score(pop_sigs[i], pop_sigs)
        fv.ncd_independence = ncd_independence_score(task_results)

        if ablation_cache is not None and organism.genome_id in ablation_cache:
            fv.ablation_delta = ablation_cache[organism.genome_id]
        elif generation >= config.get("ablation_activation_gen", 100) and fv.accuracy_margin > 0:
            if generation % config.get("ablation_interval", 5) == 0:
                abl_results = ablation_test(organism, source, reference_tasks, timeout)
                fv.ablation_delta = compute_ablation_fitness(abl_results)
                fv.ablation_details = {
                    r.node_id: r.output_change_fraction for r in abl_results
                }
                if ablation_cache is not None:
                    ablation_cache[organism.genome_id] = fv.ablation_delta

        fitness_vectors.append(fv)

    return fitness_vectors


def produce_offspring(population: list, compiled_sources: list,
                      fitness_vectors: list, generation: int,
                      config: dict, llm_mutator=None) -> list:
    """Generate offspring via mutation and crossover."""
    children = []
    n = config.get("offspring_per_generation", 50)
    crossover_rate = config.get("crossover_rate", 0.3)

    if generation < config.get("warmup_generations", 50):
        crossover_rate = 0.0

    for _ in range(n):
        if random.random() < crossover_rate and len(population) >= 2:
            p1, p2 = random.sample(population, 2)
            child = crossover(p1, p2)
        else:
            parent = random.choice(population)
            child = parent.clone()
            child.lineage.parent_ids = [parent.genome_id]

        child = mutate(child, population, generation, config, llm_mutator=llm_mutator)
        child = drift(child, config.get("drift_sigma", 0.02))
        children.append(child)

    return children


# ── Main entry point ────────��─────────────────────────────────────────

def run_apollo(smoke_test: bool = False):
    """Main entry point for Apollo v2."""
    config = load_config()
    max_gen = config.get("max_generations", 1000)
    if smoke_test:
        max_gen = min(max_gen, 100)
        config["population_size"] = min(config.get("population_size", 50), 20)

    # ── Resolve all paths from config ─────────────────────────────
    primitives_dir = _resolve_path(config.get("primitives_dir", "agents/hephaestus/src"))
    trap_gen_path = _resolve_path(config.get("trap_generator", "agents/hephaestus/src/trap_generator.py"))

    log_dir = _resolve_apollo_path(config.get("log_dir", "logs"))
    checkpoint_dir = _resolve_apollo_path(config.get("checkpoint_dir", "checkpoints"))
    lineage_path = str(Path(_resolve_apollo_path(config.get("lineage_dir", "lineage"))) / "lineage_v2.jsonl")
    graveyard_path = str(Path(_resolve_apollo_path(config.get("graveyard_dir", "graveyard"))) / "graveyard_v2.jsonl")
    dashboard_path = str(Path(_resolve_apollo_path(config.get("dashboard_dir", "dashboard"))) / "status_v2.jsonl")

    gem_dirs_raw = config.get("gem_dirs", [])
    gem_dirs = [_resolve_path(p) for p in gem_dirs_raw]

    # Ensure forge_primitives is importable
    if primitives_dir not in sys.path:
        sys.path.insert(0, primitives_dir)

    # ── Initialize structured logger ──────────────────────────────
    reset_logger()
    get_logger(log_dir)

    log_info("=" * 60, stage="bootstrap")
    log_info("APOLLO v2 — Evolutionary Primitive Routing", stage="bootstrap")
    log_info("=" * 60, stage="bootstrap")
    log_info(f"Population: {config['population_size']}", stage="bootstrap")
    log_info(f"Max generations: {max_gen}", stage="bootstrap")
    log_info(f"Smoke test: {smoke_test}", stage="bootstrap")
    log_info(f"Project root: {PROJECT_ROOT}", stage="bootstrap")
    log_info(f"Checkpoint dir: {checkpoint_dir}", stage="bootstrap")
    log_info(f"Log dir: {log_dir}", stage="bootstrap")

    # ── Task Manager ────��─────────────────────────────────────────
    log_info("Initializing task manager...", stage="bootstrap")
    task_mgr = TaskManager(
        trap_gen_path=trap_gen_path,
        n_reference=config.get("n_reference_tasks", 50),
        n_evolution=config.get("n_evolution_tasks", 100),
        n_held_out=config.get("n_held_out_tasks", 50),
        rotation_count=config.get("rotation_count", 10),
        rotation_interval=config.get("task_rotation_interval", 50),
    )
    evolution_tasks = task_mgr.get_evolution_tasks()
    reference_tasks = task_mgr.get_reference_tasks()
    held_out_tasks = task_mgr.get_held_out_tasks()
    log_info(
        f"Tasks loaded: evolution={len(evolution_tasks)}, "
        f"reference={len(reference_tasks)}, held_out={len(held_out_tasks)}",
        stage="bootstrap",
    )

    # ── NCD Baseline ��─────────────────────────────────────────────
    log_info("Computing NCD baseline...", stage="bootstrap")
    ncd_baseline = compute_ncd_baseline(evolution_tasks)
    ncd_held_out = compute_ncd_baseline(held_out_tasks)
    log_info(
        f"NCD accuracy: {ncd_baseline['accuracy']:.1%} (evolution) / "
        f"{ncd_held_out['accuracy']:.1%} (held-out)",
        stage="bootstrap",
        data={"ncd_evo_acc": ncd_baseline["accuracy"], "ncd_ho_acc": ncd_held_out["accuracy"]},
    )

    # ── Seed Population ───────��───────────────────────────────────
    log_info("Building seed population (gems + random)...", stage="bootstrap")
    population = create_mixed_seed_population(config["population_size"], gem_dirs=gem_dirs)
    log_info(f"Created {len(population)} organisms", stage="bootstrap")

    # Compile and validate all seeds
    compiled = []
    valid_pop = []
    for org in population:
        source, ok = compile_and_validate(org)
        if ok:
            compiled.append(source)
            valid_pop.append(org)
        else:
            log_graveyard(org, "compilation_failure", 0, graveyard_path=graveyard_path)

    population = valid_pop
    compiled_sources = compiled
    log_info(f"Valid after compilation: {len(population)}", stage="bootstrap")

    if len(population) < 5:
        log_warning("Too few valid organisms. Adding more random seeds...", stage="bootstrap")
        while len(population) < config["population_size"]:
            org = random_organism(3, 5)
            source, ok = compile_and_validate(org)
            if ok:
                population.append(org)
                compiled_sources.append(source)

    # ── LLM Mutator ──────────��─────────────────────────────────────
    llm_mutator = None
    llm_model = config.get("llm_model", "Qwen/Qwen2.5-Coder-3B-Instruct")
    if not smoke_test:
        log_info(f"Loading LLM mutator: {llm_model}", stage="bootstrap")
        try:
            from mutation_llm import LLMMutator
            llm_mutator = LLMMutator(
                model_name=llm_model,
                device=config.get("llm_device", "cuda"),
                max_tokens=config.get("llm_max_tokens", 512),
                temperature=config.get("llm_temperature", 0.7),
                load_in_8bit=config.get("llm_load_in_8bit", False),
            )
            llm_mutator.load()
            log_info("LLM mutator loaded", stage="bootstrap")
        except Exception as e:
            log_warning(f"LLM load failed: {e}. Running AST-only.", stage="bootstrap")
            llm_mutator = None
    else:
        log_info("Skipping LLM load (smoke test)", stage="bootstrap")

    # ── Initialize Archive + State ────────────────────────────────
    archive = NoveltyArchive(
        max_size=config.get("novelty_archive_max_size", 500),
        k=config.get("novelty_k_nearest", 15),
        threshold=config.get("novelty_archive_threshold", 0.05),
    )
    generation = 0
    ablation_cache = {}

    # Checkpoint recovery
    if checkpoint_exists(checkpoint_dir):
        log_info("Recovering from checkpoint...", stage="checkpoint")
        cp = load_checkpoint(checkpoint_dir)
        if cp:
            population, archive, generation = cp
            compiled_sources = []
            valid_pop = []
            for org in population:
                source, ok = compile_and_validate(org)
                if ok:
                    compiled_sources.append(source)
                    valid_pop.append(org)
            population = valid_pop
            log_info(
                f"Resumed at generation {generation}, pop={len(population)}",
                stage="checkpoint", generation=generation,
            )

    # ── Main Loop ─────────────────────────────────────────────────
    warmup_gens = config.get("warmup_generations", 50)
    accuracy_activation = config.get("accuracy_activation_gen", 50)
    ablation_activation = config.get("ablation_activation_gen", 100)
    checkpoint_interval = config.get("checkpoint_interval", 10)
    keep_last = config.get("checkpoint_keep_last", 5)

    start_time = time.time()
    best_held_out = -1.0

    log_info("=" * 60, stage="bootstrap")
    log_info(f"Starting evolution at gen {generation + 1}", stage="bootstrap",
             data={
                 "warmup_until": warmup_gens,
                 "accuracy_activates": accuracy_activation,
                 "ablation_activates": ablation_activation,
                 "population_size": len(population),
             })
    log_info(f"Warmup until gen {warmup_gens} (novelty-only, param mutation)", stage="bootstrap")
    log_info(f"Accuracy activates at gen {accuracy_activation}", stage="bootstrap")
    log_info(f"Ablation activates at gen {ablation_activation}", stage="bootstrap")
    log_info("=" * 60, stage="bootstrap")

    while generation < max_gen:
        generation += 1
        gen_start = time.time()

        # Determine phase
        is_warmup = generation <= warmup_gens
        if is_warmup:
            phase = "warmup"
        elif generation <= 200:
            phase = "graduated"
        else:
            phase = "main"

        # ── Task rotation ─────────────────────────────────────────
        if task_mgr.maybe_rotate(generation):
            evolution_tasks = task_mgr.get_evolution_tasks()
            ncd_baseline = compute_ncd_baseline(evolution_tasks)

        if task_mgr.maybe_refresh_held_out(generation):
            held_out_tasks = task_mgr.get_held_out_tasks()
            ncd_held_out = compute_ncd_baseline(held_out_tasks)

        # ── Evaluate population ────────��──────────────────────────
        fitness_vectors = evaluate_population(
            population, compiled_sources, evolution_tasks, ncd_baseline,
            archive, reference_tasks, generation, config,
            ablation_cache=ablation_cache,
        )

        # Phase gating: zero out dimensions not yet active
        if is_warmup:
            for fv in fitness_vectors:
                fv.accuracy_margin = 0.0
                fv.calibration = 0.0
                fv.ablation_delta = 0.0
                fv.generalization = 0.0
        if generation < ablation_activation:
            for fv in fitness_vectors:
                fv.ablation_delta = 0.0
        if generation < accuracy_activation:
            for fv in fitness_vectors:
                fv.accuracy_margin = 0.0

        # ── Produce offspring ──────────────────────────────���──────
        children = produce_offspring(
            population, compiled_sources, fitness_vectors,
            generation, config,
            llm_mutator=llm_mutator if not is_warmup else None,
        )

        # Compile children
        child_sources = []
        valid_children = []
        for child in children:
            source, ok = compile_and_validate(child)
            if ok:
                child_sources.append(source)
                valid_children.append(child)
            else:
                log_graveyard(child, "compilation_failure", generation,
                              graveyard_path=graveyard_path)

        compiled_count = len(valid_children)

        # NCD discrimination test
        ncd_test_interval = config.get("ncd_test_interval", 10)
        if (not is_warmup and generation >= 200
                and generation % ncd_test_interval == 0
                and len(reference_tasks) >= 10):
            ncd_filtered = []
            ncd_filtered_sources = []
            for child, source in zip(valid_children, child_sources):
                if discrimination_test(source, reference_tasks,
                                       min_differ=config.get("ncd_min_differ", 3)):
                    ncd_filtered.append(child)
                    ncd_filtered_sources.append(source)
                else:
                    log_graveyard(child, "ncd_equivalent", generation,
                                  graveyard_path=graveyard_path)
            ncd_killed = len(valid_children) - len(ncd_filtered)
            valid_children = ncd_filtered
            child_sources = ncd_filtered_sources
            if ncd_killed > 0:
                log_debug(
                    f"NCD filter killed {ncd_killed} organisms",
                    stage=phase, generation=generation,
                )

        # Evaluate children
        child_fitness = evaluate_population(
            valid_children, child_sources, evolution_tasks, ncd_baseline,
            archive, reference_tasks, generation, config,
            ablation_cache=ablation_cache,
        )

        # Apply same phase gating to children
        if is_warmup:
            for fv in child_fitness:
                fv.accuracy_margin = 0.0
                fv.calibration = 0.0
                fv.ablation_delta = 0.0
                fv.generalization = 0.0
        if generation < ablation_activation:
            for fv in child_fitness:
                fv.ablation_delta = 0.0
        if generation < accuracy_activation:
            for fv in child_fitness:
                fv.accuracy_margin = 0.0

        # ── Selection ──────────────────────────���──────────────────
        all_orgs = population + valid_children
        all_sources = compiled_sources + child_sources
        all_fitness = fitness_vectors + child_fitness
        all_prim_counts = [o.primitive_count for o in all_orgs]

        elite_count = config.get("elite_count", 5)
        elite_indices = select_elites(all_fitness, k=elite_count,
                                      gene_counts=all_prim_counts)
        elites = [(all_orgs[i], all_sources[i], all_fitness[i]) for i in elite_indices]

        remaining_idx = [i for i in range(len(all_orgs)) if i not in elite_indices]
        remaining_orgs = [all_orgs[i] for i in remaining_idx]
        remaining_fitness = [all_fitness[i] for i in remaining_idx]
        remaining_gc = [all_prim_counts[i] for i in remaining_idx]
        remaining_sources = [all_sources[i] for i in remaining_idx]

        target = config["population_size"] - len(elites)
        if remaining_fitness and target > 0:
            sel_idx = nsga2_select(remaining_orgs, remaining_fitness, target, remaining_gc)
            survivors = [(remaining_orgs[i], remaining_sources[i], remaining_fitness[i])
                         for i in sel_idx]
        else:
            survivors = []

        selected = elites + survivors
        population = [s[0] for s in selected]
        compiled_sources = [s[1] for s in selected]
        selected_fitness = [s[2] for s in selected]

        # ── Update novelty archive ────────────────────────────────
        sig_ref = reference_tasks[:config.get("signature_task_count", 15)]
        for source in compiled_sources:
            if source:
                sig = compute_behavioral_signature(source, sig_ref)
                archive.maybe_add(sig)

        # ── Logging ───────────────────────────────────────────────
        for org, fv in zip(population[:elite_count], selected_fitness[:elite_count]):
            log_organism(org, fv, generation, lineage_path=lineage_path)

        comp_rate = compiled_count / max(config.get("offspring_per_generation", 50), 1)
        ncd_w = ncd_decay_weight(generation)
        log_dashboard(generation, population, selected_fitness, archive.size,
                      comp_rate, ncd_weight=ncd_w, dashboard_path=dashboard_path)

        gen_time = time.time() - gen_start
        elapsed_h = (time.time() - start_time) / 3600

        # ── Console output (every 5 gens or first 5) ─────────────
        if generation % 5 == 0 or generation <= 5:
            accs = [fv.accuracy_margin for fv in selected_fitness]
            abls = [fv.ablation_delta for fv in selected_fitness]
            best_acc = max(accs) if accs else 0
            median_acc = float(np.median(accs)) if accs else 0
            best_abl = max(abls) if abls else 0
            n_lb = sum(1 for a in abls if a >= 0.20)
            log_info(
                f"[{phase:>9s}] pop={len(population):3d} | "
                f"best_acc={best_acc:+.3f} | med_acc={median_acc:+.3f} | "
                f"best_abl={best_abl:.2f} | n_lb={n_lb:2d} | "
                f"comp={comp_rate:.0%} | arch={archive.size:3d} | "
                f"ncd_w={ncd_w:.1f} | {gen_time:.1f}s | {elapsed_h:.1f}h",
                stage=phase, generation=generation,
                data={
                    "best_accuracy_margin": best_acc,
                    "median_accuracy_margin": median_acc,
                    "best_ablation_delta": best_abl,
                    "n_load_bearing": n_lb,
                    "compilation_rate": comp_rate,
                    "archive_size": archive.size,
                    "ncd_weight": ncd_w,
                    "gen_time_s": round(gen_time, 2),
                    "elapsed_h": round(elapsed_h, 2),
                },
            )

        # ── Held-out evaluation ─────��─────────────────────────────
        if generation % config.get("held_out_eval_interval", 10) == 0 and not is_warmup:
            best_idx = max(range(len(selected_fitness)),
                          key=lambda i: selected_fitness[i].accuracy_margin)
            if best_idx < len(population) and compiled_sources[best_idx]:
                ho_results = evaluate_organism_on_tasks(
                    compiled_sources[best_idx], held_out_tasks,
                    config.get("sandbox_timeout_seconds", 0.5)
                )
                ho_acc = sum(1 for r in ho_results if r.get("correct")) / len(ho_results) if ho_results else 0
                ho_margin = ho_acc - ncd_held_out["accuracy"]
                if ho_margin > best_held_out:
                    best_held_out = ho_margin
                    log_info(
                        f"New best held-out: margin={ho_margin:+.3f} (raw={ho_acc:.1%})",
                        stage="evaluation", generation=generation,
                        data={"held_out_margin": ho_margin, "held_out_accuracy": ho_acc},
                    )

                selected_fitness[best_idx].generalization = ho_margin

        # ── Capability step test ──────────────────────────────────
        if generation % 500 == 0 and generation > 0:
            cap_tasks = task_mgr.capability_step_test(generation)
            if cap_tasks:
                best_idx = max(range(len(selected_fitness)),
                              key=lambda i: selected_fitness[i].accuracy_margin)
                if compiled_sources[best_idx]:
                    cap_results = evaluate_organism_on_tasks(
                        compiled_sources[best_idx], cap_tasks,
                        config.get("sandbox_timeout_seconds", 0.5)
                    )
                    cap_acc = sum(1 for r in cap_results if r.get("correct")) / len(cap_results) if cap_results else 0
                    log_info(
                        f"Capability step test: accuracy={cap_acc:.1%}",
                        stage="evaluation", generation=generation,
                        data={"capability_step_accuracy": cap_acc},
                    )

        # ── Checkpoint ────────��─────────────────────────────��─────
        if generation % checkpoint_interval == 0:
            save_checkpoint(population, archive, generation,
                            checkpoint_dir=checkpoint_dir, keep_last=keep_last)

        # Clean ablation cache periodically
        if generation % 50 == 0:
            alive_ids = {o.genome_id for o in population}
            ablation_cache = {k: v for k, v in ablation_cache.items() if k in alive_ids}

    # ── Final report ──��───────────────────────────────────────────
    elapsed = (time.time() - start_time) / 3600
    accs = [fv.accuracy_margin for fv in selected_fitness]
    abls = [fv.ablation_delta for fv in selected_fitness]
    n_lb = sum(1 for a in abls if a >= 0.20)

    log_info("=" * 60, stage="shutdown")
    log_info(f"Apollo v2 completed: {generation} generations in {elapsed:.1f}h", stage="shutdown")
    log_info(f"Population: {len(population)}", stage="shutdown")
    log_info(f"Novelty archive: {archive.size}", stage="shutdown")
    log_info(f"Best held-out margin: {best_held_out:+.3f}", stage="shutdown")
    log_info(f"Best accuracy margin: {max(accs):+.3f}" if accs else "No accuracy data",
             stage="shutdown")
    log_info(f"Best ablation delta: {max(abls):.3f}" if abls else "No ablation data",
             stage="shutdown")
    log_info(f"Organisms with all-load-bearing primitives: {n_lb}", stage="shutdown")
    log_info("=" * 60, stage="shutdown",
             data={
                 "total_generations": generation,
                 "elapsed_hours": round(elapsed, 2),
                 "final_population": len(population),
                 "archive_size": archive.size,
                 "best_held_out_margin": best_held_out,
                 "best_accuracy_margin": max(accs) if accs else 0,
                 "best_ablation_delta": max(abls) if abls else 0,
                 "n_all_load_bearing": n_lb,
             })

    save_checkpoint(population, archive, generation,
                    checkpoint_dir=checkpoint_dir, keep_last=keep_last)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Apollo v2 — Evolutionary Primitive Routing")
    parser.add_argument("--smoke-test", action="store_true", help="Run 100 gens with small pop")
    parser.add_argument("--max-gens", type=int, default=None, help="Override max generations")
    args = parser.parse_args()

    if args.max_gens:
        config = load_config()
        config["max_generations"] = args.max_gens

    import multiprocessing as mp
    try:
        mp.set_start_method("spawn")
    except RuntimeError:
        pass

    run_apollo(smoke_test=args.smoke_test)
