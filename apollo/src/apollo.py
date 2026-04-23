"""
apollo.py — Main evolutionary loop for Apollo v2c.

Full integration of all roadmap features:
- NSGA-III selection (reference-point niching)
- Stagnation monitoring
- Multi-stage racing evaluation
- Batch LLM mutations
- Adaptive Operator Selection (AOS)
- MAP-Elites archive
- Shared LLM server mode

Phases:
  Warmup (gen 0-50):    Novelty-only, parameter mutation only
  Graduated (gen 50-200): Accuracy activates at 50, ablation at 100
  Main loop (gen 200+):  Full 6D NSGA-III, all mutation types, NCD decay
"""

import sys
import os
import random
import time
import warnings
import yaml
import numpy as np
from pathlib import Path

# Suppress numerical warnings from organism code (exp overflow, NaN, etc.)
warnings.filterwarnings("ignore", category=RuntimeWarning)
np.seterr(all='ignore')

sys.path.insert(0, str(Path(__file__).parent))
# Also add the original src dir for modules not overridden in v2c
_ORIG_SRC = str(Path(__file__).parent.parent / "src")
if _ORIG_SRC not in sys.path:
    sys.path.insert(1, _ORIG_SRC)

from genome import Organism, create_seed_population, random_organism
from gem_converter import create_mixed_seed_population
from compiler import compile_organism
from sandbox import evaluate_organism_on_tasks, safe_evaluate, quick_screen
from task_manager import TaskManager
from fitness import compute_ncd_baseline, compute_fitness, FitnessVector
from novelty import NoveltyArchive, compute_behavioral_signature
from selection import nsga3_select, nsga2_select, select_elites
from mutation import mutate, mutate_batch, drift, parameter_mutation, crossover
from ablation import ablation_test, compute_ablation_fitness
from ncd_counterpressure import discrimination_test, ncd_decay_weight, ncd_independence_score
from logger import (
    get_logger, reset_logger,
    log_info, log_debug, log_warning, log_error,
    log_organism, log_graveyard, log_autopsy, log_dashboard,
)
from checkpointer import save_checkpoint, load_checkpoint, checkpoint_exists

# v2c imports
from monitor import StagnationMonitor
from aos import AdaptiveOperatorSelector
from map_elites import MAPElitesArchive
from racing import evaluate_with_racing
from health import compute_health_report

# ── Path resolution ─────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
APOLLO_DIR = Path(__file__).parent.parent.resolve()


def _resolve_path(rel_path: str, base: Path = PROJECT_ROOT) -> str:
    return str((base / rel_path).resolve())


def _resolve_apollo_path(rel_path: str) -> str:
    return str((APOLLO_DIR / rel_path).resolve())


# ── Config loading ──────────────────────────────────────────────────

def load_config(path: str = None) -> dict:
    if path is None:
        path = str(APOLLO_DIR / "configs" / "manifest.yaml")
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return raw.get("apollo", raw)


# ── Helpers ─────────────────────────────────────────────────────────

def compile_and_validate(organism: Organism) -> tuple:
    cr = compile_organism(organism)
    if not cr.success:
        return None, False
    return cr.source_code, True


def evaluate_population(population: list, compiled_sources: list,
                        tasks: list, ncd_baseline: dict,
                        archive: NoveltyArchive, reference_tasks: list,
                        generation: int, config: dict,
                        ablation_cache: dict = None,
                        use_racing: bool = True) -> list:
    """Evaluate all organisms on 6 fitness dimensions.

    If use_racing is True, uses multi-stage racing evaluation.
    Otherwise falls back to standard full evaluation.
    """
    if use_racing:
        return evaluate_with_racing(
            population, compiled_sources, tasks, config,
            ncd_baseline, archive, reference_tasks, generation,
            ablation_cache=ablation_cache,
            compute_fitness_fn=compute_fitness,
            evaluate_fn=evaluate_organism_on_tasks,
            compute_sig_fn=compute_behavioral_signature,
            quick_screen_fn=quick_screen,
            FitnessVector_cls=FitnessVector,
        )

    # Standard evaluation (no racing)
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
                      config: dict, llm_mutator=None,
                      aos=None, use_batch: bool = True,
                      annealing_tasks=None) -> list:
    """Generate offspring via mutation and crossover.

    Returns list of (child, operator_name) if use_batch, else list of children.
    """
    n = config.get("offspring_per_generation", 50)
    crossover_rate = config.get("crossover_rate", 0.3)

    if generation < config.get("warmup_generations", 50):
        crossover_rate = 0.0

    # Phase 1: crossover to create base children
    children = []
    for _ in range(n):
        if random.random() < crossover_rate and len(population) >= 2:
            p1, p2 = random.sample(population, 2)
            child = crossover(p1, p2)
        else:
            parent = random.choice(population)
            child = parent.clone()
            child.lineage.parent_ids = [parent.genome_id]
        children.append(child)

    is_warmup = generation < config.get("warmup_generations", 50)
    active_llm = llm_mutator if not is_warmup else None

    # Phase 2: mutate (batched or serial)
    if use_batch and active_llm:
        batch_results = mutate_batch(
            children, population, generation, config,
            llm_mutator=active_llm, aos=aos,
            annealing_tasks=annealing_tasks
        )
        # Apply drift
        mutated = []
        for child, op_name in batch_results:
            child = drift(child, config.get("drift_sigma", 0.02))
            mutated.append((child, op_name))
        return mutated
    else:
        mutated = []
        for child in children:
            child = mutate(child, population, generation, config,
                          llm_mutator=active_llm,
                          annealing_tasks=annealing_tasks)
            child = drift(child, config.get("drift_sigma", 0.02))
            mutated.append((child, 'unknown'))
        return mutated


# ── Main entry point ────────────────────────────────────────────────

def _check_vram_available(min_free_gb: float = 10.0) -> bool:
    """Check if enough VRAM is free to load the LLM. Returns True if OK."""
    try:
        import torch
        if not torch.cuda.is_available():
            return False
        free = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1e9
        log_info(f"VRAM check: {free:.1f}GB free (need {min_free_gb:.1f}GB)", stage="bootstrap")
        if free < min_free_gb:
            log_warning(
                f"VRAM insufficient: {free:.1f}GB free < {min_free_gb:.1f}GB required. "
                f"Kill other GPU processes first.", stage="bootstrap")
            return False
        return True
    except Exception as e:
        log_warning(f"VRAM check failed: {e}", stage="bootstrap")
        return False


def _ensure_llm_server(server_url: str = "http://localhost:8800", timeout: int = 120) -> bool:
    """Ensure the LLM server is running. Start it if not. Returns True if available."""
    from llm_client import LLMClient
    client = LLMClient(base_url=server_url)

    # Check if already running
    if client.is_available():
        return True

    # Check VRAM before attempting to start server
    if not _check_vram_available(min_free_gb=10.0):
        return False

    # Not running — start it as a background process
    import subprocess
    server_script = str(Path(__file__).parent / "llm_server.py")
    python_exe = sys.executable

    log_info("LLM server not running — starting it...", stage="bootstrap")

    # Launch in a new process, detached
    if sys.platform == "win32":
        # On Windows, use CREATE_NEW_PROCESS_GROUP + DETACHED_PROCESS
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            [python_exe, server_script],
            creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.Popen(
            [python_exe, server_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    # Wait for server to come up (model loading takes ~10-15s)
    import time as _time
    start = _time.time()
    while _time.time() - start < timeout:
        if client.is_available():
            elapsed = _time.time() - start
            log_info(f"LLM server started in {elapsed:.1f}s", stage="bootstrap")
            return True
        _time.sleep(2)

    log_warning(f"LLM server did not start within {timeout}s", stage="bootstrap")
    return False


def run_apollo(smoke_test: bool = False, config_path: str = None,
               no_racing: bool = False, no_aos: bool = False):
    """Main entry point for Apollo v2c."""
    config = load_config(config_path)
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

    if primitives_dir not in sys.path:
        sys.path.insert(0, primitives_dir)

    # ── Initialize structured logger ──────────────────────────────
    reset_logger()
    get_logger(log_dir)

    log_info("=" * 60, stage="bootstrap")
    log_info("APOLLO v2c — Evolutionary Primitive Routing (Full Roadmap)", stage="bootstrap")
    log_info("=" * 60, stage="bootstrap")
    log_info(f"Population: {config['population_size']}", stage="bootstrap")
    log_info(f"Max generations: {max_gen}", stage="bootstrap")
    log_info(f"Smoke test: {smoke_test}", stage="bootstrap")
    log_info(f"Racing: {not no_racing}", stage="bootstrap")
    log_info(f"AOS: {not no_aos}", stage="bootstrap")
    log_info(f"Project root: {PROJECT_ROOT}", stage="bootstrap")

    # ── Task Manager ────────────────────────────────────────────────
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
    annealing_tasks = task_mgr.get_annealing_tasks(n=20)
    log_info(
        f"Tasks loaded: evolution={len(evolution_tasks)}, "
        f"reference={len(reference_tasks)}, held_out={len(held_out_tasks)}, "
        f"annealing={len(annealing_tasks)}",
        stage="bootstrap",
    )

    # ── NCD Baseline ────────────────────────────────────────────────
    log_info("Computing NCD baseline...", stage="bootstrap")
    ncd_baseline = compute_ncd_baseline(evolution_tasks)
    ncd_held_out = compute_ncd_baseline(held_out_tasks)
    log_info(
        f"NCD accuracy: {ncd_baseline['accuracy']:.1%} (evolution) / "
        f"{ncd_held_out['accuracy']:.1%} (held-out)",
        stage="bootstrap",
    )

    # ── Seed Population ─────────────────────────────────────────────
    log_info("Building seed population (gems + random)...", stage="bootstrap")
    population = create_mixed_seed_population(config["population_size"], gem_dirs=gem_dirs)
    log_info(f"Created {len(population)} organisms", stage="bootstrap")

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

    # ── LLM Mutator (always via server) ─────────────────────────────
    llm_mutator = None
    llm_model = config.get("llm_model", "Qwen/Qwen2.5-Coder-7B-Instruct")
    server_url = "http://localhost:8800"

    if not smoke_test:
        try:
            from llm_client import LLMClient
            from mutation_llm import LLMMutator

            # Auto-start server if not running
            if _ensure_llm_server(server_url):
                client = LLMClient(base_url=server_url)
                health = client.health()
                log_info(
                    f"LLM server ready: model={health.get('model')}, "
                    f"VRAM={health.get('vram_allocated_gb')}GB",
                    stage="bootstrap",
                )
                llm_mutator = LLMMutator(
                    model_name=llm_model,
                    max_tokens=config.get("llm_max_tokens", 512),
                    temperature=config.get("llm_temperature", 0.7),
                )
                llm_mutator.set_client(client)

                # Optional: DeepSeek API as alternative LLM (50/50 split)
                deepseek_key = config.get("deepseek_api_key", None)
                deepseek_ratio = config.get("deepseek_ratio", 0.0)
                if deepseek_key and deepseek_ratio > 0:
                    try:
                        from deepseek_client import DeepSeekClient
                        ds_client = DeepSeekClient(
                            api_key=deepseek_key,
                            model=config.get("deepseek_model", "deepseek-chat"),
                        )
                        llm_mutator.set_alt_client(ds_client, ratio=deepseek_ratio)
                        log_info(
                            f"DeepSeek alt LLM enabled: {deepseek_ratio:.0%} of calls",
                            stage="bootstrap",
                        )
                    except Exception as e:
                        log_warning(f"DeepSeek setup failed: {e}. Using Qwen only.", stage="bootstrap")
            else:
                log_warning("Could not start LLM server. Running AST-only.", stage="bootstrap")
        except Exception as e:
            log_warning(f"LLM setup failed: {e}. Running AST-only.", stage="bootstrap")
            llm_mutator = None
    else:
        log_info("Skipping LLM (smoke test)", stage="bootstrap")

    # ── Initialize Archive + State ────────────────────────────────
    archive = NoveltyArchive(
        max_size=config.get("novelty_archive_max_size", 500),
        k=config.get("novelty_k_nearest", 15),
        threshold=config.get("novelty_archive_threshold", 0.05),
    )
    generation = 0
    ablation_cache = {}

    # ── v2c: Initialize new components ────────────────────────────
    stagnation_monitor = StagnationMonitor(
        window=config.get("stagnation_window", 50)
    )

    aos = None
    if not no_aos:
        aos = AdaptiveOperatorSelector(
            operators=['route', 'parameter', 'wiring', 'swap'],
            alpha=config.get("aos_alpha", 0.3),
            p_min=config.get("aos_p_min", 0.05),
        )
        log_info("AOS initialized (adaptive operator selection)", stage="bootstrap")

    me_archive = MAPElitesArchive()
    log_info(f"MAP-Elites archive initialized ({me_archive.max_size} cells)", stage="bootstrap")

    use_racing = not no_racing
    use_batch = llm_mutator is not None
    log_info(f"Racing evaluation: {use_racing}", stage="bootstrap")
    log_info(f"Batch mutation: {use_batch}", stage="bootstrap")

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

    # ── Shared Pool ───────────────────────────────────────────────
    shared_pool_path = config.get("shared_pool", None)
    if shared_pool_path is None:
        shared_pool_path = config.get("paths", {}).get("shared_pool", None)
    pool = None
    island_id = config.get("island_id", config.get("instance", {}).get("island_id", "standalone"))
    if shared_pool_path:
        try:
            from shared_pool import SharedPool
            pool = SharedPool(shared_pool_path, island_id)
            stats = pool.pool_stats()
            log_info(
                f"Shared pool connected: {shared_pool_path} "
                f"(atoms={stats['total_atoms']}, entries={stats['leaderboard_entries']})",
                stage="bootstrap",
            )
        except Exception as e:
            log_warning(f"Shared pool init failed: {e}. Running standalone.", stage="bootstrap")
            pool = None
    else:
        log_info("No shared pool configured — running standalone", stage="bootstrap")

    atoms_deposited_count = 0

    # ── Main Loop ─────────────────────────────────────────────────
    warmup_gens = config.get("warmup_generations", 50)
    accuracy_activation = config.get("accuracy_activation_gen", 50)
    ablation_activation = config.get("ablation_activation_gen", 100)
    checkpoint_interval = config.get("checkpoint_interval", 10)
    keep_last = config.get("checkpoint_keep_last", 5)
    aos_accuracy_only_until = config.get("aos_accuracy_only_until", 300)
    annealing_rounds = config.get("annealing_rounds", 10)

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
    log_info("=" * 60, stage="bootstrap")

    selected_fitness = []

    while generation < max_gen:
      try:
        generation += 1
        gen_start = time.time()

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

        # Get curriculum-adjusted tasks based on population capability
        try:
            best_raw_acc = max((fv.raw_accuracy for fv in fitness_vectors), default=0.0)
        except (UnboundLocalError, NameError):
            best_raw_acc = 0.0  # First iteration after checkpoint resume
        curriculum_tasks = task_mgr.get_curriculum_tasks(generation, best_raw_acc)

        # ── Evaluate population (no racing — these survived last gen) ─
        fitness_vectors = evaluate_population(
            population, compiled_sources, curriculum_tasks, ncd_baseline,
            archive, reference_tasks, generation, config,
            ablation_cache=ablation_cache,
            use_racing=False,
        )

        # Phase gating
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

        # ── Produce offspring (batched with AOS) ──────────────────
        offspring_results = produce_offspring(
            population, compiled_sources, fitness_vectors,
            generation, config,
            llm_mutator=llm_mutator,
            aos=aos,
            use_batch=use_batch,
            annealing_tasks=annealing_tasks,
        )

        # Compile children
        child_sources = []
        valid_children = []
        operator_names = []
        for child, op_name in offspring_results:
            source, ok = compile_and_validate(child)
            if ok:
                child_sources.append(source)
                valid_children.append(child)
                operator_names.append(op_name)
            else:
                log_graveyard(child, "compilation_failure", generation,
                              graveyard_path=graveyard_path)

        compiled_count = len(valid_children)

        if compiled_count < len(offspring_results):
            failed = len(offspring_results) - compiled_count
            log_info(
                f"Compilation: {compiled_count}/{len(offspring_results)} survived ({failed} killed)",
                stage="compilation", generation=generation,
            )

        # NCD discrimination test
        ncd_test_interval = config.get("ncd_test_interval", 10)
        if (not is_warmup and generation >= 200
                and generation % ncd_test_interval == 0
                and len(reference_tasks) >= 10):
            ncd_filtered = []
            ncd_filtered_sources = []
            ncd_filtered_ops = []
            for child, source, op in zip(valid_children, child_sources, operator_names):
                if discrimination_test(source, reference_tasks,
                                       min_differ=config.get("ncd_min_differ", 3)):
                    ncd_filtered.append(child)
                    ncd_filtered_sources.append(source)
                    ncd_filtered_ops.append(op)
                else:
                    log_graveyard(child, "ncd_equivalent", generation,
                                  graveyard_path=graveyard_path)
            ncd_killed = len(valid_children) - len(ncd_filtered)
            valid_children = ncd_filtered
            child_sources = ncd_filtered_sources
            operator_names = ncd_filtered_ops
            if ncd_killed > 0:
                log_info(
                    f"NCD filter: {ncd_killed} killed, {len(ncd_filtered)} survived",
                    stage=phase, generation=generation,
                    data={"ncd_killed": ncd_killed, "ncd_survived": len(ncd_filtered)},
                )

        # Evaluate children
        child_fitness = evaluate_population(
            valid_children, child_sources, curriculum_tasks, ncd_baseline,
            archive, reference_tasks, generation, config,
            ablation_cache=ablation_cache,
            use_racing=use_racing,
        )

        # Phase gating for children
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

        # ── AOS reward update ─────────────────────────────────────
        if aos is not None and not is_warmup:
            # Use accuracy-only reward for early gens, Pareto for later
            for child_fv, op_name in zip(child_fitness, operator_names):
                # Find best-matching parent for Pareto comparison
                best_reward = 0.0
                for parent_fv in fitness_vectors:
                    reward = AdaptiveOperatorSelector.compute_reward(
                        child_fv, parent_fv, generation,
                        accuracy_only_until=aos_accuracy_only_until,
                    )
                    if reward > best_reward:
                        best_reward = reward
                        break  # Found a dominated parent, no need to check more
                aos.update(op_name, best_reward)

        # ── AOS periodic summary ─────────────────────────────────
        if generation % 10 == 0 and aos is not None:
            log_info(
                f"AOS probabilities: {aos.get_probabilities()}",
                stage="aos", generation=generation,
                data={"probabilities": aos.get_probabilities(), "counts": dict(aos.counts)},
            )

        # ── Selection (NSGA-III) ──────────────────────────────────
        all_orgs = population + valid_children
        all_sources = compiled_sources + child_sources
        all_fitness = fitness_vectors + child_fitness
        all_prim_counts = [o.primitive_count for o in all_orgs]

        elite_count = config.get("elite_count", 5)
        elite_indices = select_elites(all_fitness, k=elite_count,
                                      gene_counts=all_prim_counts)
        elites = [(all_orgs[i], all_sources[i], all_fitness[i])
                  for i in elite_indices]

        remaining_idx = [i for i in range(len(all_orgs)) if i not in elite_indices]
        remaining_orgs = [all_orgs[i] for i in remaining_idx]
        remaining_fitness = [all_fitness[i] for i in remaining_idx]
        remaining_gc = [all_prim_counts[i] for i in remaining_idx]
        remaining_sources = [all_sources[i] for i in remaining_idx]

        target = config["population_size"] - len(elites)
        if remaining_fitness and target > 0:
            sel_idx = nsga3_select(remaining_orgs, remaining_fitness,
                                   target, remaining_gc)
            survivors = [(remaining_orgs[i], remaining_sources[i],
                         remaining_fitness[i]) for i in sel_idx]
        else:
            survivors = []

        n_accepted = len([s for s in survivors
                         if s[0] in valid_children]) if valid_children else 0

        selected = elites + survivors

        # ── Selection death logging ──────────────────────────────────
        selected_ids = {s[0].genome_id for s in selected}
        for org, fv in zip(all_orgs, all_fitness):
            if org.genome_id not in selected_ids:
                muts = org.lineage.mutations_applied
                is_llm = any('llm' in m for m in muts)
                if is_llm or generation % 10 == 0:  # Always log LLM deaths, sample others
                    log_debug(
                        f"Selection death: {org.genome_id[:12]} | "
                        f"muts={muts} | acc={fv.accuracy_margin:+.3f} | "
                        f"abl={fv.ablation_delta:.3f} | div={fv.diversity:.3f}",
                        stage="selection", generation=generation,
                        data={
                            "genome_id": org.genome_id,
                            "mutations": muts,
                            "is_llm_mutated": is_llm,
                            "accuracy_margin": fv.accuracy_margin,
                            "ablation_delta": fv.ablation_delta,
                            "diversity": fv.diversity,
                            "raw_accuracy": fv.raw_accuracy,
                        }
                    )

        population = [s[0] for s in selected]
        compiled_sources = [s[1] for s in selected]
        selected_fitness = [s[2] for s in selected]

        # ── Update novelty archive ────────────────────────────────
        sig_ref = reference_tasks[:config.get("signature_task_count", 15)]
        for org, source, fv in zip(population, compiled_sources, selected_fitness):
            if source:
                sig = compute_behavioral_signature(source, sig_ref)
                archive.maybe_add(sig)
                # Also update MAP-Elites archive
                novelty = fv.diversity if fv.diversity > 0 else archive.novelty_score(sig)
                me_archive.try_insert(org, sig, novelty, info={
                    "genome_id": org.genome_id,
                    "accuracy_margin": fv.accuracy_margin,
                    "generation": generation,
                })

        # ── Stagnation Monitor ────────────────────────────────────
        if not is_warmup:
            stagnation_monitor.update(
                selected_fitness, archive.size,
                accepted=n_accepted,
                total=len(offspring_results),
                neutral_count=0,
            )

        alerts = stagnation_monitor.check_alerts(generation) if not is_warmup else []
        for alert in alerts:
            log_warning(alert, stage="monitor", generation=generation)

        # Intervention: inject random organisms on stagnation
        if stagnation_monitor.should_intervene(generation) and not is_warmup:
            n_inject = max(1, int(len(population) * 0.3))
            injected = 0
            for _ in range(n_inject * 2):
                org = random_organism(3, 5)
                source, ok = compile_and_validate(org)
                if ok and len(population) > n_inject:
                    # Replace worst organism
                    worst_idx = min(range(len(selected_fitness)),
                                   key=lambda j: selected_fitness[j].accuracy_margin)
                    population[worst_idx] = org
                    compiled_sources[worst_idx] = source
                    selected_fitness[worst_idx] = FitnessVector(
                        primitive_count=org.primitive_count
                    )
                    injected += 1
                    if injected >= n_inject:
                        break
            if injected > 0:
                log_info(
                    f"Stagnation intervention: injected {injected} random organisms",
                    stage="monitor", generation=generation,
                )

        # ── Logging ───────────────────────────────────────────────
        for org, fv in zip(population[:elite_count], selected_fitness[:elite_count]):
            log_organism(org, fv, generation, lineage_path=lineage_path)

        comp_rate = compiled_count / max(config.get("offspring_per_generation", 50), 1)
        ncd_w = ncd_decay_weight(generation)
        log_dashboard(generation, population, selected_fitness, archive.size,
                      comp_rate, ncd_weight=ncd_w, dashboard_path=dashboard_path)

        gen_time = time.time() - gen_start
        elapsed_h = (time.time() - start_time) / 3600

        # Console output
        if generation % 5 == 0 or generation <= 5:
            accs = [fv.accuracy_margin for fv in selected_fitness]
            abls = [fv.ablation_delta for fv in selected_fitness]
            best_acc = max(accs) if accs else 0
            median_acc = float(np.median(accs)) if accs else 0
            best_abl = max(abls) if abls else 0
            n_lb = sum(1 for a in abls if a >= 0.20)

            # Include AOS and MAP-Elites info
            aos_str = ""
            if aos is not None:
                probs = aos.get_probabilities()
                aos_str = f" | AOS: r={probs.get('route',0):.2f} p={probs.get('parameter',0):.2f} w={probs.get('wiring',0):.2f} s={probs.get('swap',0):.2f}"

            log_info(
                f"[{phase:>9s}] pop={len(population):3d} | "
                f"best_acc={best_acc:+.3f} | med_acc={median_acc:+.3f} | "
                f"best_abl={best_abl:.2f} | n_lb={n_lb:2d} | "
                f"comp={comp_rate:.0%} | arch={archive.size:3d} | "
                f"me={me_archive.size:2d}/{me_archive.max_size} | "
                f"ncd_w={ncd_w:.1f} | {gen_time:.1f}s | {elapsed_h:.1f}h"
                f"{aos_str}",
                stage=phase, generation=generation,
                data={
                    "best_accuracy_margin": best_acc,
                    "median_accuracy_margin": median_acc,
                    "best_ablation_delta": best_abl,
                    "n_load_bearing": n_lb,
                    "compilation_rate": comp_rate,
                    "archive_size": archive.size,
                    "map_elites_size": me_archive.size,
                    "ncd_weight": ncd_w,
                    "gen_time_s": round(gen_time, 2),
                    "elapsed_h": round(elapsed_h, 2),
                    "aos_probs": aos.get_probabilities() if aos else None,
                    "monitor_stats": stagnation_monitor.get_stats(),
                },
            )

        # ── Held-out evaluation ───────────────────────────────────
        if generation % config.get("held_out_eval_interval", 10) == 0 and not is_warmup:
            best_idx = max(range(len(selected_fitness)),
                          key=lambda i: selected_fitness[i].accuracy_margin)
            if best_idx < len(population) and compiled_sources[best_idx]:
                ho_results = evaluate_organism_on_tasks(
                    compiled_sources[best_idx], held_out_tasks,
                    config.get("sandbox_timeout_seconds", 0.5)
                )
                ho_acc = (sum(1 for r in ho_results if r.get("correct"))
                         / len(ho_results)) if ho_results else 0
                ho_margin = ho_acc - ncd_held_out["accuracy"]
                if ho_margin > best_held_out:
                    best_held_out = ho_margin
                    log_info(
                        f"New best held-out: margin={ho_margin:+.3f} (raw={ho_acc:.1%})",
                        stage="evaluation", generation=generation,
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
                    cap_acc = (sum(1 for r in cap_results if r.get("correct"))
                             / len(cap_results)) if cap_results else 0
                    log_info(
                        f"Capability step test: accuracy={cap_acc:.1%}",
                        stage="evaluation", generation=generation,
                    )

        # ── Checkpoint ────────────────────────────────────────────
        if generation % checkpoint_interval == 0:
            save_checkpoint(population, archive, generation,
                            checkpoint_dir=checkpoint_dir, keep_last=keep_last)

        # ── Health diagnostics (every 10 gens) ────────────────────
        if generation % 10 == 0 and not is_warmup:
            try:
                compute_health_report(
                    population, compiled_sources, selected_fitness,
                    curriculum_tasks, generation, config,
                    evaluate_fn=evaluate_organism_on_tasks,
                    timeout=config.get("sandbox_timeout_seconds", 0.5),
                )
            except Exception as e:
                log_warning(f"Health report failed: {e}", stage="health", generation=generation)

        # ── Shared Pool Operations ────────────────────────────────
        if pool is not None and generation % 50 == 0 and not is_warmup:
            try:
                for org, fv, source in zip(population[:5], selected_fitness[:5],
                                            compiled_sources[:5]):
                    if fv.ablation_delta >= 0.20 and source:
                        sig = compute_behavioral_signature(source, reference_tasks[:15])
                        if pool.check_distinctness(sig, threshold=0.85):
                            atom = {
                                "atom_id": f"{island_id}_{generation}_{org.genome_id[:8]}",
                                "ablation_delta": fv.ablation_delta,
                                "accuracy_margin": fv.accuracy_margin,
                                "generation": generation,
                                "primitive_count": org.primitive_count,
                                "genome_id": org.genome_id,
                            }
                            pool.deposit_atom(atom, sig)
                            atoms_deposited_count += 1
                            log_info(
                                f"Deposited atom: {atom['atom_id']}",
                                stage="pool", generation=generation,
                            )
            except Exception as e:
                log_warning(f"Pool deposit failed: {e}", stage="pool",
                           generation=generation)

            try:
                accs_lb = [fv.accuracy_margin for fv in selected_fitness]
                abls_lb = [fv.ablation_delta for fv in selected_fitness]
                metrics = {
                    "atoms_deposited": atoms_deposited_count,
                    "best_accuracy": max(accs_lb) if accs_lb else 0,
                    "best_ablation": max(abls_lb) if abls_lb else 0,
                    "population_diversity": archive.size,
                }
                pool.update_leaderboard(metrics, generation)
            except Exception as e:
                log_warning(f"Leaderboard update failed: {e}", stage="pool",
                           generation=generation)

        if pool is not None and generation % 100 == 0 and generation >= 200:
            try:
                foreign_atoms = pool.withdraw_atoms(exclude_own=True, max_count=10)
                if foreign_atoms:
                    log_info(
                        f"Found {len(foreign_atoms)} foreign atoms in pool",
                        stage="pool", generation=generation,
                    )
            except Exception as e:
                log_warning(f"Pool withdrawal failed: {e}", stage="pool",
                           generation=generation)

        # Clean ablation cache periodically
        if generation % 50 == 0:
            alive_ids = {o.genome_id for o in population}
            ablation_cache = {k: v for k, v in ablation_cache.items()
                            if k in alive_ids}

      except KeyboardInterrupt:
        log_info("Interrupted by user", stage="shutdown", generation=generation)
        break
      except Exception as e:
        log_error(f"Error in generation {generation}: {e}", stage="error", generation=generation)
        import traceback
        log_error(traceback.format_exc(), stage="error", generation=generation)
        # Emergency checkpoint
        try:
            save_checkpoint(population, archive, generation,
                            checkpoint_dir=checkpoint_dir, keep_last=keep_last)
            log_info(f"Emergency checkpoint saved at gen {generation}", stage="checkpoint")
        except Exception:
            pass
        break

    # ── Final report ─────────────────────────────────────────────
    elapsed = (time.time() - start_time) / 3600
    accs = [fv.accuracy_margin for fv in selected_fitness]
    abls = [fv.ablation_delta for fv in selected_fitness]
    n_lb = sum(1 for a in abls if a >= 0.20)

    log_info("=" * 60, stage="shutdown")
    log_info(f"Apollo v2c completed: {generation} generations in {elapsed:.1f}h",
             stage="shutdown")
    log_info(f"Population: {len(population)}", stage="shutdown")
    log_info(f"Novelty archive: {archive.size}", stage="shutdown")
    log_info(f"MAP-Elites coverage: {me_archive.size}/{me_archive.max_size} "
             f"({me_archive.coverage():.0%})", stage="shutdown")
    log_info(f"Best held-out margin: {best_held_out:+.3f}", stage="shutdown")
    log_info(f"Best accuracy margin: {max(accs):+.3f}" if accs else "No accuracy data",
             stage="shutdown")
    log_info(f"Best ablation delta: {max(abls):.3f}" if abls else "No ablation data",
             stage="shutdown")
    log_info(f"Organisms with all-load-bearing primitives: {n_lb}", stage="shutdown")
    if aos:
        log_info(f"Final AOS probabilities: {aos.get_probabilities()}", stage="shutdown")
    log_info(f"Stagnation monitor: {stagnation_monitor.get_stats()}", stage="shutdown")
    log_info("=" * 60, stage="shutdown",
             data={
                 "total_generations": generation,
                 "elapsed_hours": round(elapsed, 2),
                 "final_population": len(population),
                 "archive_size": archive.size,
                 "map_elites_size": me_archive.size,
                 "best_held_out_margin": best_held_out,
                 "best_accuracy_margin": max(accs) if accs else 0,
                 "best_ablation_delta": max(abls) if abls else 0,
                 "n_all_load_bearing": n_lb,
             })

    save_checkpoint(population, archive, generation,
                    checkpoint_dir=checkpoint_dir, keep_last=keep_last)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Apollo v2c — Evolutionary Primitive Routing (Full Roadmap)"
    )
    parser.add_argument("--config", type=str, default=None,
                        help="Path to instance config file")
    parser.add_argument("--smoke-test", action="store_true",
                        help="Run 100 gens with small pop")
    parser.add_argument("--max-gens", type=int, default=None,
                        help="Override max generations")
    parser.add_argument("--island-id", type=str, default=None,
                        help="Override island ID")
    parser.add_argument("--no-racing", action="store_true",
                        help="Disable multi-stage racing evaluation")
    parser.add_argument("--no-aos", action="store_true",
                        help="Disable adaptive operator selection")
    args = parser.parse_args()

    import multiprocessing as mp
    try:
        mp.set_start_method("spawn")
    except RuntimeError:
        pass

    run_apollo(
        smoke_test=args.smoke_test,
        config_path=args.config,
        no_racing=args.no_racing,
        no_aos=args.no_aos,
    )
