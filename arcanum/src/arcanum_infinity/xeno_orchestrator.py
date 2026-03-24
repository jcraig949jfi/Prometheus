"""
Xenolexicon Orchestrator — forked from Ignis's SETIV2Orchestrator.

Same CMA-ES loop, same TII injection, same model rotation.
Different fitness: novelty instead of correctness.
New output: named specimens in the Xenolexicon catalog.
"""

import torch
import math
import gc
import json
import logging
import shutil
import time
import os
from pathlib import Path
from typing import List

from .xeno_config import XenoConfig, ModelTarget
from .tii_engine import load_tii_model, execute_tii_generation
from .genome import SteeringGenome
from .xeno_fitness import NoveltyFitnessEngine
from .naming_engine import generate_specimen_name
from .specimen import Specimen, capture_specimen
from .xenolexicon_db import XenolexiconDB
from .alert import send_alert, print_visual_separator
from .seti_logger import slog, LogContext

# ── Graceful Shutdown ─────────────────────────────────────────────────
STOP_SEMAPHORE_NAME = "STOP"
PID_FILE_NAME = "orchestrator.pid"


class XenoOrchestrator:
    """
    Evolutionary search for structured novelty in transformer latent space.

    Reuses Ignis's:
      - TII engine (residual stream injection)
      - SteeringGenome representation
      - CMA-ES distribution update (diagonal)
      - Model rotation and state persistence
      - Graceful shutdown semaphore

    Replaces:
      - MultiTaskCrucible → NoveltyFitnessEngine
      - Falsification battery → Reproducibility + Distinctness checks
      - Discovery alerts → Specimen capture + naming
    """

    def __init__(self, config=None, results_dir=None):
        # Handle both XenoConfig object and path
        if isinstance(config, XenoConfig):
            self.config = config
        else:
            self.config = XenoConfig.load(config)

        if results_dir:
            self.config.results_dir = Path(results_dir)

        self.config.results_dir.mkdir(parents=True, exist_ok=True)
        self.stop_requested = False

        # PID management
        self.pid_file = self.config.results_dir / PID_FILE_NAME
        self.pid_file.write_text(str(os.getpid()), encoding="utf-8")

        # Logging
        slog.configure(log_dir=self.config.results_dir / "logs")
        slog.info("Xenolexicon Orchestrator initialised")

        # Novelty engine (replaces MultiTaskCrucible)
        self.novelty_engine = NoveltyFitnessEngine(
            target_perplexity=self.config.target_perplexity,
        )

        # Xenolexicon catalog (created per-model in init_for_model)
        self.catalog: XenolexiconDB = None

        # CMA-ES strategy parameters (population-dependent)
        self.mu = self.config.population_size // 2
        self.weights = (torch.log(torch.tensor(self.mu + 0.5))
                        - torch.log(torch.arange(1, self.mu + 1).float()))
        self.weights = self.weights / self.weights.sum()
        self.weights = self.weights.cuda()
        self.mueff = (self.weights.sum() ** 2 / (self.weights ** 2).sum()).item()

        slog.debug(f"CMA-ES strategy: pop={self.config.population_size}, "
                   f"mu={self.mu}, mueff={self.mueff:.2f}")

        # Per-model state (initialized by init_for_model)
        self.model = None
        self.model_target = None
        self.d_model = 0
        self.n_layers = 0
        self.target_layer = 0
        self.early_layer_cutoff = 0

    # ═══════════════════════════════════════════════════════════════════
    # MODEL INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════

    def init_for_model(self, model_target: ModelTarget):
        """Load a model and initialize CMA-ES state + novelty baselines."""
        # Unload previous model
        if self.model is not None:
            slog.debug("Releasing VRAM from previous model")
            del self.model
            self.model = None
            gc.collect()
            torch.cuda.empty_cache()

        self.model_target = model_target
        results_dir = self.config.model_results_dir(model_target)
        results_dir.mkdir(parents=True, exist_ok=True)

        print_visual_separator("=", 80, f"LOADING: {model_target.name}")
        slog.info(f"Loading model: {model_target.name}")

        self.model = load_tii_model(model_target.name)
        if self.model is None:
            raise RuntimeError(f"Failed to load model {model_target.name} — skipping")

        # Model geometry
        self.d_model = self.model.cfg.d_model
        self.n_layers = self.model.cfg.n_layers
        self.target_layer = model_target.target_layer(self.n_layers)
        self.early_layer_cutoff = model_target.early_layer_cutoff(self.n_layers)

        vram_model = torch.cuda.memory_allocated() / 1e9
        slog.info(f"Model geometry: d_model={self.d_model}, n_layers={self.n_layers}, "
                  f"target_layer={self.target_layer} ({model_target.target_layer_ratio:.0%})")
        slog.info(f"Model VRAM footprint: {vram_model:.2f} GB")

        # CMA-ES state initialization
        self.is_diagonal = True
        self.mean_vector = torch.zeros(self.d_model).cuda()
        self.C = torch.ones(self.d_model).cuda()
        self.sigma = model_target.sigma_override or self.config.mutation_rate

        self.gen_count = 0
        self.population: List[SteeringGenome] = []
        self.best_genome = None
        self.last_best_fitness = -float('inf')
        self.plateau_count = 0

        # Random baseline for novelty calibration
        self.random_baseline_mean = 0.0
        self.random_baseline_max = 0.0
        self.random_baseline_std = 0.0

        # Layer tracking
        self._layer_best: dict = {}
        self._layer_evals: dict = {}

        # Evolution paths
        self.pc = torch.zeros(self.d_model).cuda()
        self.ps = torch.zeros(self.d_model).cuda()

        # CMA-ES hyperparameters
        self.cc = 4.0 / (self.d_model + 4.0)
        self.cs = (self.mueff + 2.0) / (self.d_model + self.mueff + 5.0)
        self.c1 = 2.0 / ((self.d_model + 1.3) ** 2 + self.mueff)
        self.cmu = min(1.0 - self.c1,
                       2.0 * (self.mueff - 2.0 + 1.0 / self.mueff)
                       / ((self.d_model + 2.0) ** 2 + self.mueff))
        self.damps = (1.0 + 2.0 * max(0.0, math.sqrt((self.mueff - 1.0)
                      / (self.d_model + 1.0)) - 1.0) + self.cs)
        self.chiN = (math.sqrt(self.d_model)
                     * (1.0 - 1.0 / (4.0 * self.d_model)
                        + 1.0 / (21.0 * self.d_model ** 2)))

        # Load persisted state or start fresh
        self.load_state()

        # Initialize novelty baselines (unsteered model outputs)
        if self.gen_count == 0:
            self.novelty_engine.capture_baselines(self.model,
                                                   max_new_tokens=self.config.max_new_tokens)
            # Random baseline for calibration
            self._run_random_novelty_baseline()

            # Initialize with random mean vector (no inception for novelty search)
            rand_init = torch.randn(self.d_model).cuda()
            effective_norm = model_target.seed_norm_override or self.config.seed_norm
            self.mean_vector = rand_init / rand_init.norm() * effective_norm
            slog.info(f"Random init: mean_norm={self.mean_vector.norm().item():.4f}")
        else:
            # Still need baselines even on resume
            self.novelty_engine.capture_baselines(self.model,
                                                   max_new_tokens=self.config.max_new_tokens)

        # Initialize catalog
        self.catalog = XenolexiconDB(
            results_dir=results_dir,
            distinctness_threshold=self.config.distinctness_threshold,
        )
        slog.info(f"Catalog loaded: {self.catalog.catalog_size()} existing specimens")

    # ═══════════════════════════════════════════════════════════════════
    # STATE PERSISTENCE (identical to Ignis)
    # ═══════════════════════════════════════════════════════════════════

    @property
    def _results_dir(self) -> Path:
        return self.config.model_results_dir(self.model_target)

    @property
    def _state_file(self) -> Path:
        return self.config.model_state_file(self.model_target)

    @property
    def _jsonl_path(self) -> Path:
        return self._results_dir / "evaluation_log.jsonl"

    def load_state(self):
        """Restore CMA-ES state from disk."""
        if not self._state_file.exists():
            slog.debug(f"No state file at {self._state_file} — starting fresh")
            return
        try:
            state = torch.load(self._state_file, weights_only=False)
            self.mean_vector = state['mean_vector'].cuda()
            self.C = state['C'].cuda()
            self.sigma = state['sigma']
            self.gen_count = state['gen_count']
            self.pc = state['pc'].cuda()
            self.ps = state['ps'].cuda()
            self.last_best_fitness = state.get('last_best_fitness', -float('inf'))
            self.plateau_count = state.get('plateau_count', 0)
            slog.info(f"State restored: gen={self.gen_count}, sigma={self.sigma:.4f}, "
                      f"best_fitness={self.last_best_fitness:.4f}")
        except Exception as e:
            slog.error(f"State load FAILED — starting fresh: {e}")

    def save_state(self):
        """Persist CMA-ES state to disk."""
        try:
            state = {
                'mean_vector': self.mean_vector.cpu(),
                'C': self.C.cpu(),
                'sigma': self.sigma,
                'gen_count': self.gen_count,
                'pc': self.pc.cpu(),
                'ps': self.ps.cpu(),
                'is_diagonal': True,
                'last_best_fitness': self.last_best_fitness,
                'plateau_count': self.plateau_count,
            }
            torch.save(state, self._state_file)
            slog.trace(f"State saved: gen={self.gen_count}, sigma={self.sigma:.4f}")

            if self.best_genome:
                results_dir = self._results_dir
                checkpoint_path = results_dir / f"gen_{self.gen_count}_best.pt"
                self.best_genome.save(str(checkpoint_path))
                self.best_genome.save(str(results_dir / "best_genome.pt"))
        except Exception as e:
            slog.exception(f"State save FAILED at gen {self.gen_count}: {e}")

        self._sync_to_drive()

    def _sync_to_drive(self):
        """Copy results to sync directory (non-fatal on failure)."""
        sync_dir = self.config.sync_output_dir
        if sync_dir is None:
            return
        try:
            src = self._results_dir
            dst = sync_dir / self.model_target.slug
            dst.mkdir(parents=True, exist_ok=True)
            for f in src.iterdir():
                if f.is_file():
                    shutil.copy2(f, dst / f.name)
            slog.trace(f"Synced results to {dst}")
        except Exception as e:
            slog.warning(f"Drive sync failed (non-fatal): {e}")

    # ═══════════════════════════════════════════════════════════════════
    # CMA-ES DISTRIBUTION (identical to Ignis)
    # ═══════════════════════════════════════════════════════════════════

    def sample_population(self):
        """Sample genomes from the CMA-ES distribution."""
        self.population = []
        slog.trace(f"Sampling {self.config.population_size} genomes: "
                   f"sigma={self.sigma:.5f}")

        for i in range(self.config.population_size):
            z = torch.randn(self.d_model).cuda()
            vector = self.mean_vector + self.sigma * (self.C.sqrt() * z)

            # 80/20 layer exploration (same as Ignis)
            layer = self.target_layer
            exploration_type = "main"
            if torch.rand(1) < 0.2:
                low = int(0.3 * self.n_layers)
                high = int(0.9 * self.n_layers)
                layer = torch.randint(low, high + 1, (1,)).item()
                layer = max(self.early_layer_cutoff + 1, min(self.n_layers - 1, layer))
                exploration_type = "scout"

            # Position exploration (same as Ignis)
            pos_ratio = 1.0
            if torch.rand(1) < 0.2:
                pos_ratio = max(0.0, min(1.0, 1.0 + 0.3 * torch.randn(1).item()))

            self.population.append(SteeringGenome(
                layer_index=layer, vector=vector, position_ratio=pos_ratio,
                exploration_type=exploration_type
            ))

    def update_distribution(self, sorted_pop: List[SteeringGenome]):
        """Diagonal CMA-ES distribution update (identical to Ignis)."""
        old_mean = self.mean_vector.clone()

        # Update mean
        new_mean = torch.zeros_like(self.mean_vector)
        for i in range(self.mu):
            new_mean += self.weights[i] * sorted_pop[i].vector
        self.mean_vector = new_mean

        # Update evolution paths
        invsqrtC = 1.0 / self.C.sqrt()
        y = (self.mean_vector - old_mean) / self.sigma

        if not torch.isfinite(y).all():
            slog.error("NaN/Inf in CMA-ES update — resetting paths")
            self.ps.zero_()
            self.pc.zero_()
            self.sigma = max(self.sigma, 0.01)
            return

        self.ps = ((1.0 - self.cs) * self.ps
                   + math.sqrt(self.cs * (2.0 - self.cs) * self.mueff)
                   * (invsqrtC * y))

        ps_norm = self.ps.norm()
        hsig_val = (ps_norm
                    / math.sqrt(1.0 - (1.0 - self.cs) ** (2 * (self.gen_count + 1)))
                    / self.chiN)
        hsig = 1.0 if hsig_val < 1.4 + 2.0 / (self.d_model + 1.0) else 0.0

        self.pc = ((1.0 - self.cc) * self.pc
                   + hsig * math.sqrt(self.cc * (2.0 - self.cc) * self.mueff) * y)

        # Update step size
        self.sigma *= math.exp((self.cs / self.damps) * (ps_norm / self.chiN - 1.0))

        # Update diagonal covariance
        self.C = ((1.0 - self.c1 - self.cmu) * self.C
                  + self.c1 * (self.pc ** 2
                               + (1.0 - hsig) * self.cc * (2.0 - self.cc) * self.C))

        for i in range(self.mu):
            diff = (sorted_pop[i].vector - old_mean) / self.sigma
            self.C += self.cmu * self.weights[i] * (diff ** 2)

        # Safety clamps
        self.sigma = max(min(self.sigma, 10.0), 1e-5)
        self.C = torch.clamp(self.C, 1e-8, 1e6)

        slog.trace(f"Distribution updated: sigma={self.sigma:.5f}, "
                   f"mean_norm={self.mean_vector.norm().item():.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # RANDOM NOVELTY BASELINE
    # ═══════════════════════════════════════════════════════════════════

    def _run_random_novelty_baseline(self):
        """Evaluate random vectors to establish novelty baseline."""
        n = self.config.random_baseline_samples
        slog.info(f"Random Novelty Baseline: evaluating {n} random vectors")
        scores = []

        for i in range(n):
            try:
                rand_vec = torch.randn(self.d_model).cuda()
                effective_norm = (self.model_target.seed_norm_override
                                  or self.config.seed_norm)
                rand_vec = rand_vec / rand_vec.norm() * effective_norm
                rand_genome = SteeringGenome(
                    layer_index=self.target_layer, vector=rand_vec
                )
                score, _, _ = self.novelty_engine.evaluate_genome(
                    self.model, rand_genome
                )
                scores.append(score)
                slog.trace(f"  Random {i + 1}/{n}: novelty={score:.4f}")
            except Exception as e:
                slog.warning(f"  Random {i + 1} failed: {e}")

        if scores:
            import statistics
            self.random_baseline_mean = statistics.mean(scores)
            self.random_baseline_max = max(scores)
            self.random_baseline_std = (statistics.stdev(scores)
                                        if len(scores) > 1 else 0.0)
            slog.info(f"Random Novelty Baseline: mean={self.random_baseline_mean:.4f}, "
                      f"max={self.random_baseline_max:.4f}, "
                      f"std={self.random_baseline_std:.4f}")
        else:
            slog.warning("Random novelty baseline: no successful evaluations")

    # ═══════════════════════════════════════════════════════════════════
    # REPRODUCIBILITY CHECK
    # ═══════════════════════════════════════════════════════════════════

    def _check_reproducibility(self, genome: SteeringGenome) -> float:
        """
        Re-run a genome multiple times and check output consistency.

        Returns reproducibility score (mean pairwise cosine of output embeddings).
        """
        n_runs = self.config.reproducibility_runs
        embeddings = []

        for run_i in range(n_runs):
            try:
                _, meta, results = self.novelty_engine.evaluate_genome(
                    self.model, genome
                )
                # Collect all output embeddings from this run
                run_embs = [r.output_embedding for r in results
                            if r.output_embedding is not None]
                if run_embs:
                    centroid = torch.stack(run_embs).mean(dim=0)
                    centroid = centroid / (centroid.norm() + 1e-10)
                    embeddings.append(centroid)
            except Exception as e:
                slog.warning(f"Reproducibility run {run_i + 1} failed: {e}")

        if len(embeddings) < 2:
            slog.warning("Not enough reproducibility runs — returning 0.0")
            return 0.0

        # Mean pairwise cosine similarity
        cos_sims = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = torch.dot(embeddings[i], embeddings[j]).item()
                cos_sims.append(sim)

        repro = sum(cos_sims) / len(cos_sims) if cos_sims else 0.0
        slog.debug(f"Reproducibility: {repro:.4f} (from {len(embeddings)} runs)")
        return repro

    # ═══════════════════════════════════════════════════════════════════
    # SPECIMEN CAPTURE + NAMING
    # ═══════════════════════════════════════════════════════════════════

    def _capture_and_name_specimen(
        self,
        genome: SteeringGenome,
        fitness: float,
        metadata: dict,
        novelty_results: list,
    ) -> Specimen:
        """
        Full specimen capture pipeline:
        1. Create specimen with provenance
        2. Check reproducibility
        3. Check distinctness against catalog
        4. Generate compound name
        5. Add to catalog
        """
        results_dir = self._results_dir

        # 1. Capture
        specimen = capture_specimen(
            genome=genome,
            generation=self.gen_count,
            model_name=self.model_target.name,
            fitness=fitness,
            metadata=metadata,
            novelty_results=novelty_results,
            results_dir=results_dir,
        )

        # 2. Reproducibility
        slog.info(f"Checking reproducibility for specimen {specimen.specimen_id}")
        repro = self._check_reproducibility(genome)
        specimen.reproducibility = round(repro, 4)

        if repro < self.config.reproducibility_threshold:
            specimen.status = "rejected"
            slog.info(f"Specimen {specimen.specimen_id} REJECTED: "
                      f"reproducibility={repro:.4f} < {self.config.reproducibility_threshold}")
        else:
            # 3. Distinctness
            emb_path = results_dir / "specimens" / f"{specimen.specimen_id}_emb.pt"
            if emb_path.exists():
                centroid = torch.load(str(emb_path), weights_only=False)
                is_distinct, min_dist, nearest = self.catalog.check_distinctness(centroid)
                specimen.distinctness = round(min_dist, 4)

                if not is_distinct:
                    specimen.status = "rejected"
                    slog.info(f"Specimen {specimen.specimen_id} REJECTED: "
                               f"too similar to {nearest} (dist={min_dist:.4f})")
                else:
                    specimen.status = "validated"
            else:
                specimen.status = "validated"
                slog.warning("No embedding file — skipping distinctness check")

        # 4. Naming (even for rejected — might be interesting)
        try:
            name, description = generate_specimen_name(
                model=self.model,
                outputs=specimen.outputs,
                generation=self.gen_count,
                layer=genome.layer_index,
                specimen_id=specimen.specimen_id,
                max_new_tokens=self.config.naming_max_tokens,
            )
            specimen.name = name
            specimen.description = description
        except Exception as e:
            slog.error(f"Naming failed: {e}")
            specimen.name = f"XENO-{self.gen_count:03d}-L{genome.layer_index}"
            specimen.description = "Naming engine failed."

        # 5. Add to catalog
        emb_for_cache = None
        if specimen.status == "validated" and emb_path.exists():
            emb_for_cache = torch.load(str(emb_path), weights_only=False)

        self.catalog.add_specimen(specimen, embedding=emb_for_cache)

        # Log the capture
        status_icon = "✓" if specimen.status == "validated" else "✗"
        slog.info(f"[{status_icon}] Specimen '{specimen.name}' ({specimen.specimen_id}): "
                  f"novelty={specimen.novelty_score:.4f}, "
                  f"repro={specimen.reproducibility:.4f}, "
                  f"distinct={specimen.distinctness:.4f}, "
                  f"status={specimen.status}")
        if specimen.description:
            slog.info(f"  Description: {specimen.description[:120]}")

        return specimen

    # ═══════════════════════════════════════════════════════════════════
    # SHUTDOWN
    # ═══════════════════════════════════════════════════════════════════

    def _check_stop_semaphore(self) -> bool:
        if self.stop_requested:
            return True
        stop_file = self.config.results_dir / STOP_SEMAPHORE_NAME
        if stop_file.exists():
            try:
                msg = stop_file.read_text(encoding="utf-8").strip()
                stop_file.unlink()
            except Exception:
                msg = ""
            reason = f" (reason: {msg})" if msg else ""
            slog.warning(f"STOP semaphore detected{reason}")
            self.stop_requested = True
            return True
        return False

    def _graceful_shutdown(self):
        """Save state, unload model, flush VRAM."""
        if self.model_target is not None:
            try:
                self.save_state()
                slog.info(f"State saved for {self.model_target.name} at gen {self.gen_count}")
            except Exception as e:
                slog.error(f"Failed to save state during shutdown: {e}")

        if self.model is not None:
            del self.model
            self.model = None

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            vram_after = torch.cuda.memory_allocated() / 1e9
            slog.info(f"VRAM released: {vram_after:.2f} GB remaining")

        for handler in logging.getLogger("xenolexicon").handlers:
            handler.flush()
            handler.close()

        if hasattr(self, 'pid_file') and self.pid_file.exists():
            self.pid_file.unlink()

        slog.info("Graceful shutdown complete")
        print("\n  >> Shutdown complete. State saved, VRAM released.")

    # ═══════════════════════════════════════════════════════════════════
    # EVOLUTION LOOP — THE MAIN EVENT
    # ═══════════════════════════════════════════════════════════════════

    def run(self):
        """Standard entry point for the orchestrator."""
        for model_target in self.config.models:
            try:
                self.init_for_model(model_target)
                self.run_evolution()
                if self.stop_requested:
                    break
            except Exception as e:
                slog.exception(f"Fatal error in model cycle for {model_target.name}: {e}")
            finally:
                self._graceful_shutdown()

    def run_evolution(self):
        """
        Evolutionary search for structured novelty.

        Same Ask-Evaluate-Tell loop as Ignis, but:
        - Fitness = novelty (semantic distance × coherence)
        - Genomes exceeding threshold → specimen capture + naming
        - No falsification battery (replaced by reproducibility)
        """
        MAX_CONSECUTIVE_FAILURES = 5
        consecutive_failures = 0
        max_gens = self.model_target.generations_per_cycle

        slog.info(f"Xenolexicon Evolution START: model={self.model_target.name}, "
                  f"gen_start={self.gen_count}, max_gens={max_gens}")

        specimens_this_run = 0

        while self.gen_count < max_gens:
            gen_start_time = time.time()
            torch.cuda.reset_peak_memory_stats()

            with LogContext(model=self.model_target.slug, gen=f"{self.gen_count:03d}"):
                try:
                    slog.info(f"Generation {self.gen_count}/{max_gens} BEGIN "
                               f"(sigma={self.sigma:.5f}, plateau={self.plateau_count})")

                    # ── 1. ASK — sample population ──
                    self.sample_population()

                    # ── 2. EVALUATE — novelty scoring ──
                    gen_specimens = []

                    for i, genome in enumerate(self.population):
                        with LogContext(genome=f"{i:03d}/{len(self.population):03d}"):
                            try:
                                with LogContext(step="novelty"):
                                    score, meta, novelty_results = \
                                        self.novelty_engine.evaluate_genome(
                                            self.model, genome
                                        )

                                    # Zone taxonomy (relative to random baseline)
                                    zone = "dead"
                                    if score > self.random_baseline_mean + 2 * self.random_baseline_std:
                                        zone = "productive"
                                    elif score < self.random_baseline_mean - 2 * self.random_baseline_std:
                                        zone = "destructive"

                                    genome.fitness = score

                                    slog.info(
                                        f"Genome {i:03d}/{len(self.population):03d} │ "
                                        f"Novelty: {score:.4f} │ "
                                        f"Dist: {meta.get('mean_semantic_distance', 0):.3f} │ "
                                        f"Coh: {meta.get('mean_coherence', 0):.3f} │ "
                                        f"Layer: {genome.layer_index} │ "
                                        f"[{genome.exploration_type.upper()}] "
                                        f"[ZONE:{zone.upper()}]"
                                    )

                                # ── SPECIMEN CAPTURE ──
                                # If novelty exceeds threshold, capture as specimen
                                if score >= self.config.novelty_threshold:
                                    slog.info(f"Novelty {score:.4f} ≥ threshold "
                                               f"{self.config.novelty_threshold} — "
                                               f"initiating specimen capture")
                                    specimen = self._capture_and_name_specimen(
                                        genome, score, meta, novelty_results
                                    )
                                    gen_specimens.append(specimen)
                                    if specimen.status == "validated":
                                        specimens_this_run += 1

                                # ── JSONL black-box recorder ──
                                try:
                                    entry = {
                                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        "gen": self.gen_count,
                                        "genome_idx": i,
                                        "layer": genome.layer_index,
                                        "explore": genome.exploration_type,
                                        "zone": zone,
                                        "novelty": round(score, 6),
                                        "semantic_distance": round(
                                            meta.get("mean_semantic_distance", 0.0), 4),
                                        "coherence": round(
                                            meta.get("mean_coherence", 0.0), 4),
                                        "per_provocation": meta.get("per_provocation", {}),
                                        "specimen_id": (
                                            gen_specimens[-1].specimen_id
                                            if gen_specimens and gen_specimens[-1].status != "rejected"
                                            else None
                                        ),
                                    }
                                    with open(self._jsonl_path, "a", encoding="utf-8") as jf:
                                        jf.write(json.dumps(entry) + "\n")
                                except Exception as je:
                                    slog.warning(f"JSONL write failed: {je}")

                                # Layer tracking
                                if genome.fitness > -1.0:
                                    _l = genome.layer_index
                                    self._layer_evals[_l] = self._layer_evals.get(_l, 0) + 1
                                    if genome.fitness > self._layer_best.get(_l, -1.0):
                                        self._layer_best[_l] = genome.fitness

                            except torch.cuda.OutOfMemoryError:
                                slog.warning(f"CUDA OOM evaluating genome {i}")
                                gc.collect()
                                torch.cuda.empty_cache()
                                genome.fitness = -1.0

                            except Exception as e:
                                slog.exception(f"Genome {i} evaluation FAILED: {e}")
                                genome.fitness = -1.0

                        # Mid-generation progress
                        if i == len(self.population) // 2:
                            scored = [g for g in self.population[:i + 1] if g.fitness > -1.0]
                            best_so_far = max((g.fitness for g in scored), default=0.0)
                            slog.info(f"  ├─ {i + 1}/{len(self.population)} evaluated │ "
                                       f"gen_best_so_far={best_so_far:.4f}")

                        # Stop semaphore check
                        if self._check_stop_semaphore():
                            slog.info(f"Stopping at genome {i + 1}/{len(self.population)}")
                            return

                    # ── 3. TELL — update CMA-ES distribution ──
                    self.population.sort(key=lambda x: x.fitness, reverse=True)

                    current_best_f = self.population[0].fitness
                    if current_best_f > self.last_best_fitness + 1e-4:
                        self.last_best_fitness = current_best_f
                        self.plateau_count = 0
                    else:
                        self.plateau_count += 1

                    if self.best_genome is None or current_best_f > self.best_genome.fitness:
                        self.best_genome = self.population[0]
                        slog.info(f"New gen best: fitness={current_best_f:.4f}, "
                                  f"layer={self.best_genome.layer_index}")

                    # Plateau decay
                    if self.plateau_count >= 5:
                        old_sigma = self.sigma
                        self.sigma *= 0.85
                        self.plateau_count = 0
                        slog.info(f"Plateau decay: sigma {old_sigma:.5f} → {self.sigma:.5f}")

                    self.update_distribution(self.population)

                    # ── Generation summary ──
                    valid_f = [g.fitness for g in self.population if g.fitness > -1.0]
                    mean_f = sum(valid_f) / len(valid_f) if valid_f else 0.0

                    gen_elapsed = time.time() - gen_start_time
                    vram_peak_gb = torch.cuda.max_memory_allocated() / 1e9
                    vram_used = torch.cuda.memory_allocated() / 1e9

                    n_productive = sum(
                        1 for g in self.population
                        if g.fitness > self.random_baseline_mean + 2 * self.random_baseline_std
                    )
                    n_captured = len(gen_specimens)
                    n_validated = sum(1 for s in gen_specimens if s.status == "validated")
                    catalog_summary = self.catalog.get_catalog_summary()

                    slog.info(
                        f"[STEP:gen_summary] [GEN:{self.gen_count:03d}] "
                        f"mean_novelty={mean_f:.4f}, best_novelty={current_best_f:.4f}, "
                        f"sigma={self.sigma:.5f}, "
                        f"productive={n_productive}/{len(self.population)}, "
                        f"captured={n_captured}, validated={n_validated}, "
                        f"catalog_total={catalog_summary.get('total', 0)}"
                    )

                    # Console summary
                    slog.info(
                        f"Gen {self.gen_count:>3d}/{max_gens} │ "
                        f"best={current_best_f:.4f} │ σ={self.sigma:.5f} │ "
                        f"specimens={n_validated}/{n_captured} │ "
                        f"catalog={catalog_summary.get('total', 0)} │ "
                        f"VRAM={vram_used:.1f}/{vram_peak_gb:.1f}GB │ "
                        f"{gen_elapsed:.1f}s"
                    )

                    # Log any new specimen names for human-readable tracking
                    for s in gen_specimens:
                        if s.status == "validated":
                            slog.info(f"  ╰─ NEW: '{s.name}' — {s.description[:80]}")

                    self.gen_count += 1
                    self.save_state()

                    # Stop check between generations
                    if self._check_stop_semaphore():
                        return

                    consecutive_failures = 0
                    gc.collect()
                    torch.cuda.empty_cache()

                    # Periodic dashboard
                    if self.gen_count % 5 == 0:
                        global_best = self.best_genome.fitness if self.best_genome else 0.0
                        print_visual_separator("─", 70,
                                               f"XENOLEXICON STATUS @ Gen {self.gen_count}")

                except Exception as e:
                    consecutive_failures += 1
                    slog.exception(f"Generation {self.gen_count} FAILED ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}): {e}")
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        slog.critical("Too many consecutive failures — aborting evolution loop")
                        return
                    time.sleep(10)
