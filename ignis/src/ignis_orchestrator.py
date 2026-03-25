import torch
import math
import gc
import json
import logging
import shutil
import time
from pathlib import Path
from typing import List

from ignis_config import IgnisConfig, ModelTarget
from tii_engine import load_tii_model, execute_tii_generation
from genome import SteeringGenome
from fitness import MultiTaskCrucible
from probe_runner import run_latent_probe
from alert import send_alert, print_visual_separator
from inception_protocol import prep_inception_seed
from ignis_logger import slog, LogContext

# ── Graceful Shutdown Semaphore ──────────────────────────────────────
# Drop a file named STOP into the results directory to request a clean
# shutdown.  The orchestrator checks for this file at three boundaries:
#   1. Between genomes  (fastest response, ~1 min)
#   2. Between generations  (after state is saved)
#   3. Between models  (in the outer cycle loop)
# Use  `python stop_ignis.py`  to create the semaphore from any terminal.
STOP_SEMAPHORE_NAME = "STOP"
PID_FILE_NAME = "orchestrator.pid"


class IgnisOrchestrator:
    def __init__(self, config_path=None):
        self.config = IgnisConfig.load(config_path)
        self.config.results_dir.mkdir(parents=True, exist_ok=True)
        self.stop_requested = False
        self.prev_inception_pc1 = None

        # ── PID Management ──
        import os
        self.pid_file = self.config.results_dir / PID_FILE_NAME
        self.pid_file.write_text(str(os.getpid()), encoding="utf-8")

        # Configure structured logging
        slog.configure(log_dir=self.config.results_dir / "logs")
        slog.info("Ignis Orchestrator initialised")

        # Multi-Task Crucible: multiplicative fitness across all traps
        self.crucible = MultiTaskCrucible()

        # Keep primary task prompt for falsification spot-checks
        self.task_prompt = self.crucible.battery[0]["prompt"]

        # Strategy Parameters (population-dependent, constant across models)
        self.mu = self.config.population_size // 2
        self.weights = torch.log(torch.tensor(self.mu + 0.5)) - torch.log(torch.arange(1, self.mu + 1).float())
        self.weights = self.weights / self.weights.sum()
        self.weights = self.weights.cuda()
        self.mueff = (self.weights.sum()**2 / (self.weights**2).sum()).item()

        slog.debug(f"CMA-ES strategy: pop={self.config.population_size}, mu={self.mu}, mueff={self.mueff:.2f}")

        # Per-model state (initialized by init_for_model)
        self.model = None
        self.model_target = None
        self.d_model = 0
        self.n_layers = 0
        self.target_layer = 0
        self.early_layer_cutoff = 0

    def init_for_model(self, model_target: ModelTarget):
        """Load a model and initialize all model-dependent CMA-ES state.

        Recovery:
          - If model load fails (OOM or download error), raises RuntimeError
            so the caller (run()) can skip this model and continue the cycle.
        """
        # Unload previous model if present
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
                  f"target_layer={self.target_layer} ({model_target.target_layer_ratio:.0%}), "
                  f"early_cutoff={self.early_layer_cutoff} ({model_target.early_layer_ratio:.0%})")
        slog.info(f"Model VRAM footprint: {vram_model:.2f} GB")

        # Diagonal CMA-ES
        self.is_diagonal = True

        # State initialization (may be overwritten by load_state)
        self.mean_vector = torch.zeros(self.d_model).cuda()
        self.C = torch.ones(self.d_model).cuda()
        self.sigma = model_target.sigma_override or self.config.mutation_rate

        self.gen_count = 0
        self.population: List[SteeringGenome] = []
        self.best_genome = None
        self.last_best_fitness = -float('inf')
        self.plateau_count = 0
        self.naive_baseline_output = ""
        self.random_baseline_mean = 0.0
        self.random_baseline_max = 0.0
        self.random_baseline_std = 0.0

        # Scout layer tracking — persistent across generations, reset per model
        self._layer_best: dict = {}   # layer_index → best fitness ever seen
        self._layer_evals: dict = {}  # layer_index → total eval count

        # Evolution paths
        self.pc = torch.zeros(self.d_model).cuda()
        self.ps = torch.zeros(self.d_model).cuda()

        # CMA-ES hyperparameters (d_model-dependent)
        self.cc = 4.0 / (self.d_model + 4.0)
        self.cs = (self.mueff + 2.0) / (self.d_model + self.mueff + 5.0)
        self.c1 = 2.0 / ((self.d_model + 1.3)**2 + self.mueff)
        self.cmu = min(1.0 - self.c1, 2.0 * (self.mueff - 2.0 + 1.0/self.mueff) / ((self.d_model + 2.0)**2 + self.mueff))
        self.damps = 1.0 + 2.0 * max(0.0, math.sqrt((self.mueff - 1.0) / (self.d_model + 1.0)) - 1.0) + self.cs
        self.chiN = math.sqrt(self.d_model) * (1.0 - 1.0/(4.0 * self.d_model) + 1.0/(21.0 * self.d_model**2))

        slog.trace(f"CMA-ES hyperparams: cc={self.cc:.6f}, cs={self.cs:.6f}, c1={self.c1:.6f}, "
                   f"cmu={self.cmu:.6f}, damps={self.damps:.4f}, chiN={self.chiN:.4f}")

        # Load persisted state or bootstrap from scratch
        self.load_state()
        if self.gen_count == 0:
            try:
                slog.info("Capturing naive model baseline (no steering)")
                input_tokens = self.model.to_tokens(self.task_prompt)
                output_tokens = self.model.generate(input_tokens, max_new_tokens=64, verbose=False)
                self.naive_baseline_output = self.model.to_string(output_tokens[0])
                slog.info(f"Naive baseline: {self.naive_baseline_output.strip()[:200]}")
            except Exception as e:
                slog.exception(f"Naive baseline capture failed: {e}")
                self.naive_baseline_output = "[BASELINE_CAPTURE_FAILED]"

            # Generate inception seed for this model if missing or norm-mismatched
            inception_path = results_dir / "gen_inception_seed.pt"
            effective_norm = self.model_target.seed_norm_override or self.config.seed_norm
            if inception_path.exists():
                # Check if the existing seed's norm matches the current config
                try:
                    existing_seed = torch.load(inception_path, weights_only=False)
                    existing_norm = existing_seed['vector'].norm().item()
                    norm_delta = abs(existing_norm - effective_norm) / max(effective_norm, 1e-8)
                    if norm_delta > 0.05:  # >5% deviation triggers regeneration
                        slog.warning(
                            f"Inception seed norm mismatch: existing={existing_norm:.2f}, "
                            f"target={effective_norm:.1f} (Δ={norm_delta:.1%}). "
                            f"Deleting stale seed and regenerating.")
                        inception_path.unlink()
                    else:
                        slog.debug(f"Inception seed norm OK: {existing_norm:.2f} ≈ {effective_norm:.1f}")
                except Exception as e:
                    slog.warning(f"Could not verify inception seed norm: {e}. Regenerating.")
                    inception_path.unlink(missing_ok=True)

            if not inception_path.exists():
                slog.info("No inception seed found — running Inception Protocol")
                inception_path, pc1 = prep_inception_seed(self.model, str(results_dir),
                                                          layer=self.target_layer, seed_norm=effective_norm)
                
                # Point 6: Cross-model inception metadata
                if pc1 is not None and self.prev_inception_pc1 is not None:
                    # Cosine similarity (both normalized internally in prep_inception_seed)
                    try:
                        cos_sim = torch.dot(pc1.float(), self.prev_inception_pc1.float()).item()
                        slog.info(f"[STEP:inception_meta] Cross-model PC1 Cosine Similarity: {cos_sim:.4f}")
                    except Exception as e:
                        slog.trace(f"Cross-model PC1 comparison failed: {e}")
                
                if pc1 is not None:
                    self.prev_inception_pc1 = pc1
            else:
                # Load existing to track for next model
                try:
                    seed_genome = SteeringGenome.load(str(inception_path))
                    self.prev_inception_pc1 = seed_genome.vector
                except:
                    pass

            self.warm_start()

            # Run random direction baseline (once per model)
            self.run_random_direction_baseline(n_samples=5)

    @property
    def _results_dir(self) -> Path:
        """Per-model results directory."""
        return self.config.model_results_dir(self.model_target)

    @property
    def _state_file(self) -> Path:
        """Per-model state file."""
        return self.config.model_state_file(self.model_target)

    @property
    def _jsonl_path(self) -> Path:
        """Structured per-evaluation log (JSONL black-box recorder)."""
        return self._results_dir / "discovery_log.jsonl"

    @property
    def _scout_csv_path(self) -> Path:
        """Persistent scout layer map — best fitness seen per layer."""
        return self._results_dir / "scout_layer_map.csv"

    def load_state(self):
        """Restore CMA-ES state from disk. On failure, starts fresh (gen 0)."""
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
            self.naive_baseline_output = state.get('naive_baseline_output', "")
            slog.info(f"State restored: gen={self.gen_count}, sigma={self.sigma:.4f}, "
                      f"best_fitness={self.last_best_fitness:.4f}, plateau={self.plateau_count}")
        except Exception as e:
            slog.error(f"State load FAILED — starting fresh: {e}")

    def warm_start(self):
        """Initializes mean_vector from inception seed or best files."""
        results_dir = self._results_dir
        inception_path = results_dir / "gen_inception_seed.pt"

        # Priority: Inception Seed > latest best
        target_path = None
        source_label = None
        if inception_path.exists():
            target_path = inception_path
            source_label = "inception_seed"
        else:
            best_files = list(results_dir.glob("gen_*_best.pt"))
            if best_files:
                valid_files = [f for f in best_files if "_" in f.name]
                if valid_files:
                    valid_files.sort(key=lambda x: int(x.name.split('_')[1]), reverse=True)
                    target_path = valid_files[0]
                    source_label = f"checkpoint:{target_path.name}"

        if target_path and target_path.exists():
            try:
                data = torch.load(target_path, weights_only=False)
                if 'vector' in data:
                    self.mean_vector = data['vector'].cuda()
                    self.last_best_fitness = -float('inf')
                    slog.info(f"Warm-started from {source_label} ({target_path.name}), "
                              f"vec_norm={self.mean_vector.norm().item():.4f}")
                else:
                    slog.warning(f"Warm-start file {target_path} has no 'vector' key — skipping")
            except Exception as e:
                slog.error(f"Warm-start FAILED from {target_path}: {e}")
        else:
            slog.info("No warm-start source found — using zero mean vector")

    def save_state(self):
        """Persist CMA-ES state + best genome to disk, then sync to Drive."""
        results_dir = self._results_dir
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
                'naive_baseline_output': self.naive_baseline_output
            }
            torch.save(state, self._state_file)
            slog.trace(f"State saved: gen={self.gen_count}, sigma={self.sigma:.4f}")

            if self.best_genome:
                checkpoint_path = results_dir / f"gen_{self.gen_count}_best.pt"
                self.best_genome.save(str(checkpoint_path))
                self.best_genome.save(str(results_dir / "best_genome.pt"))
        except Exception as e:
            slog.exception(f"State save FAILED at gen {self.gen_count}: {e}")

        # Sync to remote output directory (e.g., Google Drive)
        self.sync_to_drive()

    def sync_to_drive(self):
        """Copy the current model's results to the configured sync directory.
        Fails silently if the path is unavailable (e.g., Drive not mounted)."""
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

    def run_random_direction_baseline(self, n_samples: int = 5):
        """
        Evaluate n_samples random unit vectors through the crucible to establish
        the baseline fitness achievable by chance. Logs stats and stores the
        baseline mean for later comparison with evolved vectors.
        """
        slog.info(f"Random Direction Baseline: evaluating {n_samples} random vectors")
        baseline_scores = []
        for i in range(n_samples):
            try:
                rand_vec = torch.randn(self.d_model).cuda()
                effective_norm = self.model_target.seed_norm_override or self.config.seed_norm
                rand_vec = rand_vec / rand_vec.norm() * effective_norm  # match inception seed scale
                rand_genome = SteeringGenome(
                    layer_index=self.target_layer, vector=rand_vec
                )
                score, _ = self.crucible.evaluate_vector(
                    self.model, rand_genome, execute_tii_generation
                )
                baseline_scores.append(score)
                slog.trace(f"  Random direction {i+1}/{n_samples}: fitness={score:.4f}")
            except Exception as e:
                slog.warning(f"  Random direction {i+1} failed: {e}")

        if baseline_scores:
            import statistics
            self.random_baseline_mean = statistics.mean(baseline_scores)
            self.random_baseline_max = max(baseline_scores)
            self.random_baseline_std = statistics.stdev(baseline_scores) if len(baseline_scores) > 1 else 0.0
            slog.info(f"Random Baseline established: mean={self.random_baseline_mean:.4f}, "
                      f"max={self.random_baseline_max:.4f}, "
                      f"std={self.random_baseline_std:.4f}, n={len(baseline_scores)}")
        else:
            self.random_baseline_mean = 0.0
            self.random_baseline_max = 0.0
            self.random_baseline_std = 0.0
            slog.warning("Random baseline: no successful evaluations")

    def run_norm_sweep(self, genome: SteeringGenome):
        """
        Evaluate a survivor genome across a range of norms (0.25x to 4x)
        to diagnose the fitness-vs-norm response curve.
        """
        slog.info(f"Norm Sweep Diagnostic: evaluating survivor at 0.25x, 0.5x, 1x, 2x, 4x")
        results = {}
        original_norm = genome.vector.norm().item()

        for multiplier in [0.25, 0.5, 1.0, 2.0, 4.0]:
            try:
                scaled_vector = genome.vector.detach().clone() * multiplier
                test_genome = SteeringGenome(
                    layer_index=genome.layer_index,
                    vector=scaled_vector,
                    position_ratio=genome.position_ratio
                )
                score, _ = self.crucible.evaluate_vector(
                    self.model, test_genome, execute_tii_generation
                )
                results[multiplier] = score
                slog.trace(f"  └─ {multiplier:>4.2f}x norm ({original_norm * multiplier:>7.2f}): "
                           f"fitness={score:.4f}")
            except Exception as e:
                slog.warning(f"  └─ {multiplier}x sweep FAILED: {e}")
                results[multiplier] = -1.0

        # Log completion with a summary curve
        curve = " │ ".join([f"{m}x:{results.get(m, -1):.3f}" for m in [0.25, 0.5, 1.0, 2.0, 4.0]])
        slog.info(f"Norm Sweep Curve: {curve}")

    def sample_population(self):
        """Samples new genomes from the current Diagonal CMA-ES distribution."""
        self.population = []
        slog.trace(f"Sampling {self.config.population_size} genomes: "
                   f"sigma={self.sigma:.5f}, mean_norm={self.mean_vector.norm().item():.4f}")

        for i in range(self.config.population_size):
            z = torch.randn(self.d_model).cuda()
            vector = self.mean_vector + self.sigma * (self.C.sqrt() * z)

            # Evolve layer: 80% at target_layer, 20% exploration across wide range [0.3, 0.9]
            layer = self.target_layer
            exploration_type = "main"
            if torch.rand(1) < 0.2:
                low = int(0.3 * self.n_layers)
                high = int(0.9 * self.n_layers)
                layer = torch.randint(low, high + 1, (1,)).item()
                layer = max(self.early_layer_cutoff + 1, min(self.n_layers - 1, layer))
                exploration_type = "scout"

            # Evolve injection position: mostly last-token (1.0), with 20% exploration
            pos_ratio = 1.0
            if torch.rand(1) < 0.2:
                pos_ratio = max(0.0, min(1.0, 1.0 + 0.3 * torch.randn(1).item()))

            self.population.append(SteeringGenome(
                layer_index=layer, vector=vector, position_ratio=pos_ratio,
                exploration_type=exploration_type
            ))

        pos_ratios = [g.position_ratio for g in self.population]
        n_non_last = sum(1 for p in pos_ratios if p < 0.99)
        slog.trace(f"Population sampled: {len(self.population)} genomes, "
                   f"layers={set(g.layer_index for g in self.population)}, "
                   f"non-last-token={n_non_last}/{len(self.population)}")

    def _create_noise_genome(self, original_genome: SteeringGenome) -> SteeringGenome:
        """Creates a norm-matched Gaussian noise genome for Null-A test."""
        vec = torch.randn_like(original_genome.vector)
        norm = vec.norm()
        if norm > 1e-10:
            vec = (vec / norm) * original_genome.vector.norm()
        return SteeringGenome(
            layer_index=original_genome.layer_index, vector=vec,
            position_ratio=original_genome.position_ratio
        )

    def _create_ortho_genome(self, original_genome: SteeringGenome) -> SteeringGenome:
        """Creates an orthogonal norm-matched genome for Null-B test."""
        # Simple Gram-Schmidt relative to original
        ortho = torch.randn_like(original_genome.vector)
        dot_vv = torch.dot(original_genome.vector, original_genome.vector)
        if dot_vv.abs() > 1e-10:
            proj = (torch.dot(ortho, original_genome.vector) / dot_vv) * original_genome.vector
            ortho = ortho - proj
        
        norm = ortho.norm()
        if norm > 1e-10:
            ortho = (ortho / norm) * original_genome.vector.norm()
        
        return SteeringGenome(
            layer_index=original_genome.layer_index, vector=ortho,
            position_ratio=original_genome.position_ratio
        )

    def _create_flip_genome(self, original_genome: SteeringGenome) -> SteeringGenome:
        """Creates a sign-flipped (-v) genome."""
        return SteeringGenome(
            layer_index=original_genome.layer_index, vector=-original_genome.vector,
            position_ratio=original_genome.position_ratio
        )

    def _create_shuffle_genome(self, original_genome: SteeringGenome) -> SteeringGenome:
        """Creates a genome with shuffled vector components (Null-C)."""
        perm = torch.randperm(original_genome.vector.shape[0], device=original_genome.vector.device)
        return SteeringGenome(
            layer_index=original_genome.layer_index, vector=original_genome.vector[perm],
            position_ratio=original_genome.position_ratio
        )

    def update_distribution(self, sorted_pop: List[SteeringGenome]):
        """Robust Diagonal CMA-ES distribution update with NaN/Inf guards."""
        old_mean = self.mean_vector.clone()

        # 1. Update Mean
        new_mean = torch.zeros_like(self.mean_vector)
        for i in range(self.mu):
            new_mean += self.weights[i] * sorted_pop[i].vector
        self.mean_vector = new_mean

        # 2. Update Evolution Paths
        invsqrtC = 1.0 / self.C.sqrt()
        y = (self.mean_vector - old_mean) / self.sigma

        # Guard: check for NaN/Inf in y (can happen if sigma → 0)
        if not torch.isfinite(y).all():
            slog.error(f"NaN/Inf detected in CMA-ES update (y vector). "
                       f"sigma={self.sigma:.2e}. Resetting evolution paths.")
            self.ps.zero_()
            self.pc.zero_()
            self.sigma = max(self.sigma, 0.01)
            return

        self.ps = (1.0 - self.cs) * self.ps + math.sqrt(self.cs * (2.0 - self.cs) * self.mueff) * (invsqrtC * y)

        ps_norm = self.ps.norm()
        hsig_val = ps_norm / math.sqrt(1.0 - (1.0 - self.cs)**(2 * (self.gen_count + 1))) / self.chiN
        hsig = 1.0 if hsig_val < 1.4 + 2.0 / (self.d_model + 1.0) else 0.0

        self.pc = (1.0 - self.cc) * self.pc + hsig * math.sqrt(self.cc * (2.0 - self.cc) * self.mueff) * y

        # 3. Update Step Size Sigma
        self.sigma = self.sigma * math.exp((self.cs / self.damps) * (ps_norm / self.chiN - 1.0))

        # 4. Update Variance Vector C (Diagonal)
        self.C = (1.0 - self.c1 - self.cmu) * self.C + \
                 self.c1 * (self.pc**2 + (1.0 - hsig) * self.cc * (2.0 - self.cc) * self.C)

        for i in range(self.mu):
            diff = (sorted_pop[i].vector - old_mean) / self.sigma
            self.C += self.cmu * self.weights[i] * (diff**2)

        # Safety: clip sigma and C
        self.sigma = max(min(self.sigma, 10.0), 1e-5)
        self.C = torch.clamp(self.C, 1e-8, 1e6)

        slog.trace(f"Distribution updated: sigma={self.sigma:.5f}, "
                   f"mean_norm={self.mean_vector.norm().item():.4f}, "
                   f"C_range=[{self.C.min().item():.2e}, {self.C.max().item():.2e}], "
                   f"ps_norm={ps_norm.item():.4f}, hsig={hsig:.0f}")

    def log_manifold_geometry(self, generation: int, elites: List[SteeringGenome]):
        """
        Analyzes the geometry of the current elite population:
        1. Participation Ratio — effective dimensionality
        2. Elite Cosine Similarity — directional convergence
        3. CMA-ES Covariance Spectrum — search distribution shape
        """
        if not elites:
            return {}

        try:
            matrix = torch.stack([e.vector for e in elites])
            # SVD requires float32 on CUDA (bfloat16 not supported by gesvdj)
            _, s, _ = torch.svd(matrix.float())
            participation_ratio = ((s.sum()**2) / (s**2).sum()).item()

            norms = matrix / matrix.norm(dim=1, keepdim=True)
            cos_matrix = norms @ norms.T
            n = cos_matrix.shape[0]
            if n > 1:
                mask = torch.triu(torch.ones(n, n, device=cos_matrix.device), diagonal=1).bool()
                mean_cos = cos_matrix[mask].mean().item()
            else:
                mean_cos = 1.0

            C_sorted = torch.sort(self.C, descending=True).values
            top5 = C_sorted[:5].tolist()
            cov_ratio = (C_sorted[0] / C_sorted[-1]).item() if C_sorted[-1] > 0 else float('inf')

            # Pre-registered classification
            pr_lo = self.config.pr_vector_threshold
            pr_hi = self.config.pr_manifold_threshold
            if participation_ratio < pr_lo:
                pr_label = "VECTOR (single direction)"
            elif participation_ratio > pr_hi:
                pr_label = "MANIFOLD (distributed)"
            else:
                pr_label = "AMBIGUOUS (needs more data)"

            slog.info(f"Geometry: manifold_dim={participation_ratio:.2f} [{pr_label}], "
                      f"elite_cos={mean_cos:.3f}, "
                      f"cov_ratio={cov_ratio:.1f}, cov_top5=[{', '.join(f'{v:.4f}' for v in top5)}]")
            
            return {
                "participation_ratio": participation_ratio,
                "mean_cos": mean_cos,
                "top5": top5,
                "cov_ratio": cov_ratio
            }
        except Exception as e:
            slog.error(f"Geometry logging failed: {e}")
            return {}

    def _check_stop_semaphore(self) -> bool:
        """Check if the STOP semaphore file exists.

        Returns True if shutdown was requested.  The semaphore is consumed
        (deleted) on detection so the next run starts clean.
        The result is cached to ensure consistent state across loop boundaries.
        """
        if self.stop_requested:
            return True

        stop_file = self.config.results_dir / STOP_SEMAPHORE_NAME
        if stop_file.exists():
            try:
                # Read optional message from the file
                msg = stop_file.read_text(encoding="utf-8").strip()
                stop_file.unlink()
            except Exception:
                msg = ""
            reason = f" (reason: {msg})" if msg else ""
            slog.warning(f"STOP semaphore detected{reason} — initiating graceful shutdown")
            self.stop_requested = True
            return True
        return False

    def run_evolution(self):
        """Run the evolutionary loop for the current model.

        Recovery:
          - Per-genome exceptions are caught: the genome gets fitness=-1.0
            and the generation continues.
          - Per-generation OOM: saves state, does VRAM cleanup, and continues
            to the next generation (skipping the broken one).
          - Consecutive failure guard: if MAX_CONSECUTIVE_FAILURES generations
            fail back-to-back, aborts this model's run to avoid infinite loops.
        """
        MAX_CONSECUTIVE_FAILURES = 5
        consecutive_failures = 0
        max_gens = self.model_target.generations_per_cycle

        slog.info(f"Evolution START: model={self.model_target.name}, "
                  f"gen_start={self.gen_count}, max_gens={max_gens}")

        while self.gen_count < max_gens:
            gen_start_time = time.time()
            torch.cuda.reset_peak_memory_stats()

            with LogContext(model=self.model_target.slug, gen=f"{self.gen_count:03d}"):
                try:
                    slog.info(f"Generation {self.gen_count}/{max_gens} BEGIN "
                              f"(sigma={self.sigma:.5f}, plateau={self.plateau_count})")

                    # 1. Ask — sample population
                    self.sample_population()

                    # 2. Evaluate via Multi-Task Crucible + Causal Falsification
                    _gen_outputs = []  # accumulate full outputs → written to gen_N_outputs.json at end
                    for i, genome in enumerate(self.population):
                        with LogContext(genome=f"{i:03d}/{len(self.population):03d}"):
                            try:
                                # Step A: Multi-task fitness
                                with LogContext(step="crucible"):
                                    score, meta = self.crucible.evaluate_vector(
                                        self.model, genome, execute_tii_generation
                                    )
                                    # zone taxonomy
                                    zone = "dead"
                                    if score > self.random_baseline_mean + 2 * self.random_baseline_std:
                                        zone = "productive"
                                    elif score < self.random_baseline_mean - 2 * self.random_baseline_std:
                                        zone = "destructive"

                                    slog.info(f"Genome {i:03d}/{len(self.population):03d} │ "
                                              f"Fitness: {score:.4f} │ Norm: {genome.vector.norm().item():.2f} │ "
                                              f"Pos: {genome.position_ratio:.2f} │ Layer: {genome.layer_index} │ "
                                              f"[EXPLORE:{genome.exploration_type.upper()}] [ZONE:{zone.upper()}]")

                                # Step B: Causal falsification gate
                                # Only falsify genomes reaching BASELINE tier (0.3+).
                                _falsif = None  # populated below if falsification runs
                                if score >= 0.3:
                                    with LogContext(step="falsification"):
                                        slog.trace(f"Score {score:.2f} ≥ 0.3 (BASELINE) — running full falsification battery")
                                        # Human-readable probe run (captured in logs)
                                        run_latent_probe(self.model, genome, self.task_prompt)

                                        # Null-A: Gaussian Noise
                                        noise_genome = self._create_noise_genome(genome)
                                        noise_score, _ = self.crucible.evaluate_vector(self.model, noise_genome, execute_tii_generation)

                                        # Null-B: Orthogonal
                                        ortho_genome = self._create_ortho_genome(genome)
                                        ortho_score, _ = self.crucible.evaluate_vector(self.model, ortho_genome, execute_tii_generation)

                                        # Sign-Flip
                                        flip_genome = self._create_flip_genome(genome)
                                        flip_score, _ = self.crucible.evaluate_vector(self.model, flip_genome, execute_tii_generation)

                                        # Null-C: Shuffle
                                        shuf_genome = self._create_shuffle_genome(genome)
                                        shuf_score, _ = self.crucible.evaluate_vector(self.model, shuf_genome, execute_tii_generation)

                                        passed = noise_score < score * 0.8
                                        _falsif = {
                                            "noise": round(noise_score, 4),
                                            "ortho": round(ortho_score, 4),
                                            "flip":  round(flip_score, 4),
                                            "shuffle": round(shuf_score, 4),
                                            "sign_flip_delta": round(score - flip_score, 4),
                                            "ortho_delta": round(score - ortho_score, 4),
                                            "passed": passed,
                                        }

                                        # Structured scores line (raw values)
                                        slog.info(f"[STEP:falsification_scores] [GENOME:{i:03d}/{len(self.population):03d}] "
                                                  f"primary={score:.4f}, noise={noise_score:.4f}, ortho={ortho_score:.4f}, "
                                                  f"flip={flip_score:.4f}, shuffle={shuf_score:.4f}")

                                        # Single parseable verdict line with all ratios
                                        _dir_margin = score - max(noise_score, ortho_score, shuf_score)
                                        slog.info(
                                            f"[STEP:falsification_verdict] {'PASSED' if passed else 'FALSIFIED'} "
                                            f"direction_margin={_dir_margin:.4f}, "
                                            f"flip_delta={_falsif['sign_flip_delta']:.4f}, "
                                            f"noise_ratio={noise_score / score:.3f}, "
                                            f"ortho_ratio={ortho_score / score:.3f}, "
                                            f"shuffle_ratio={shuf_score / score:.3f}"
                                        )

                                        if not passed:
                                            slog.debug(f"FALSIFIED: noise_score={noise_score:.2f} ≥ "
                                                       f"{score * 0.8:.2f} (80% of {score:.2f})")
                                            genome.fitness = -1.0
                                        else:
                                            slog.debug(f"PASSED: noise_score={noise_score:.2f} < "
                                                       f"{score * 0.8:.2f} — direction is special")
                                            genome.fitness = score
                                            slog.info(f"PASSED genome {i:03d} → candidate for "
                                                      f"gen_{self.gen_count + 1}_best.pt "
                                                      f"(layer={genome.layer_index}, "
                                                      f"explore={genome.exploration_type.upper()})")

                                            # RLVF scoring for survivors
                                            try:
                                                rlvf_result = self.crucible.score_rlvf(
                                                    self.model, genome,
                                                    self._run_steered_inference,
                                                    score, meta.get("trap_outputs", {}),
                                                )
                                                genome.rlvf_fitness = rlvf_result.get("rlvf_fitness", 0.0)
                                                genome.rlvf_variance = rlvf_result.get("rlvf_variance", 0.0)
                                                genome.rlvf_n_tools = rlvf_result.get("rlvf_n_tools", 0)
                                                # Blend: 80% battery + 20% RLVF
                                                if genome.rlvf_n_tools >= 3:
                                                    genome.fitness = 0.8 * score + 0.2 * genome.rlvf_fitness
                                                    slog.info(f"RLVF blended: battery={score:.4f} "
                                                              f"rlvf={genome.rlvf_fitness:.4f} "
                                                              f"combined={genome.fitness:.4f}")
                                            except Exception as _rlvf_err:
                                                slog.debug(f"RLVF scoring skipped: {_rlvf_err}")

                                            # Diagnostic norm sweep for survivors
                                            self.run_norm_sweep(genome)
                                else:
                                    genome.fitness = score

                                # ── Black-box recorder: JSONL entry for every evaluation ──
                                try:
                                    _primary_trap = self.crucible.battery[0]["name"]
                                    _entry = {
                                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        "gen": self.gen_count,
                                        "genome_idx": i,
                                        "layer": genome.layer_index,
                                        "explore": genome.exploration_type,
                                        "zone": zone,
                                        "fitness": round(genome.fitness, 6),
                                        "marker_fitness": round(meta.get("marker_fitness", 0.0), 6),
                                        "logit_score": round(meta.get("logit_score", 0.0), 6),
                                        "rlvf_fitness": round(getattr(genome, "rlvf_fitness", 0.0), 6),
                                        "rlvf_variance": round(getattr(genome, "rlvf_variance", 0.0), 6),
                                        "rlvf_n_tools": getattr(genome, "rlvf_n_tools", 0),
                                        "trap_scores": {
                                            k: {"score": round(v.get("score", 0.0), 4),
                                                "tier": v.get("tier", "?")}
                                            for k, v in meta.get("traps", {}).items()
                                        },
                                        "logit_by_trap": {
                                            k: round(v, 4)
                                            for k, v in meta.get("logit_by_trap", {}).items()
                                        },
                                        "min_trap_score": round(min(
                                            (v.get("score", 0.0) for v in meta.get("traps", {}).values()),
                                            default=0.0
                                        ), 4),
                                        "injection_snapshot": meta.get("injection_snapshot", {}),
                                        "logit_shift_signature": meta.get("logit_shift_signature", {}),
                                        "falsification": _falsif,
                                        "output_sample": meta.get("traps", {}).get(
                                            _primary_trap, {}
                                        ).get("output", "")[:200],
                                    }
                                    with open(self._jsonl_path, "a", encoding="utf-8") as _jf:
                                        _jf.write(json.dumps(_entry) + "\n")

                                    # Accumulate full outputs for gen_N_outputs.json
                                    _gen_outputs.append({
                                        "genome_idx": i,
                                        "layer": genome.layer_index,
                                        "fitness": round(genome.fitness, 6),
                                        "outputs": {
                                            k: v.get("output", "")
                                            for k, v in meta.get("traps", {}).items()
                                        },
                                    })
                                except Exception as _je:
                                    slog.warning(f"JSONL write failed (non-fatal): {_je}")

                                # ── Layer tracking (for scout map) ──
                                if genome.fitness > -1.0:
                                    _l = genome.layer_index
                                    self._layer_evals[_l] = self._layer_evals.get(_l, 0) + 1
                                    if genome.fitness > self._layer_best.get(_l, -1.0):
                                        self._layer_best[_l] = genome.fitness

                                # Discovery alert (pre-registered criteria)
                                if genome.fitness > self.config.discovery_min_fitness:
                                    vs_random = (genome.fitness / self.random_baseline_mean
                                                 if self.random_baseline_mean > 0 else float('inf'))
                                    slog.warning(
                                        f"POTENTIAL DISCOVERY: fitness={genome.fitness:.2f}, "
                                        f"vs_random={vs_random:.1f}x "
                                        f"(threshold={self.config.discovery_vs_random_ratio:.1f}x)"
                                    )

                            except torch.cuda.OutOfMemoryError:
                                slog.warning(f"CUDA OOM evaluating genome {i} — assigning floor fitness")
                                gc.collect()
                                torch.cuda.empty_cache()
                                genome.fitness = -1.0

                            except Exception as e:
                                slog.exception(f"Genome {i} evaluation FAILED: {e}")
                                genome.fitness = -1.0

                        # Mid-generation progress (console-visible at halfway)
                        if i == len(self.population) // 2:
                            scored = [g for g in self.population[:i+1] if g.fitness > -1.0]
                            gen_best_so_far = max((g.fitness for g in scored), default=0.0)
                            slog.info(f"  ├─ {i+1}/{len(self.population)} evaluated │ "
                                      f"gen_best_so_far={gen_best_so_far:.4f}")

                        # ── Boundary 1: Stop Semaphore (between genomes) ──
                        if self._check_stop_semaphore():
                            slog.info(f"Stopping evolution loop early (at genome {i+1}/{len(self.population)})")
                            self._graceful_shutdown()
                            return

                    # 3. Tell — update distribution
                    self.population.sort(key=lambda x: x.fitness, reverse=True)

                    current_best_f = self.population[0].fitness
                    if current_best_f > self.last_best_fitness + 1e-4:
                        self.last_best_fitness = current_best_f
                        self.plateau_count = 0
                    else:
                        self.plateau_count += 1

                    if self.best_genome is None or current_best_f > self.best_genome.fitness:
                        self.best_genome = self.population[0]
                        _pt_ref = f"gen_{self.gen_count + 1}_best.pt"
                        slog.info(f"New gen best → {_pt_ref} "
                                  f"(fitness={current_best_f:.4f}, layer={self.best_genome.layer_index}, "
                                  f"explore={self.best_genome.exploration_type.upper()})")
                        if self.best_genome.fitness > 2.0:
                            send_alert(
                                f"CRUCIBLE Discovery on {self.model_target.name}",
                                f"Gen {self.gen_count}: Multi-Task Fitness {self.best_genome.fitness:.2f}",
                                self.config
                            )

                    # Plateau decay
                    if self.plateau_count >= 5:
                        old_sigma = self.sigma
                        self.sigma *= 0.85
                        self.plateau_count = 0
                        slog.info(f"Plateau decay: sigma {old_sigma:.5f} → {self.sigma:.5f}")

                    self.update_distribution(self.population)

                    # Point 5: Generation-level summary statistics for scraping
                    elites = [g for g in self.population if g.fitness > -1.0][:self.mu]
                    geo_metrics = self.log_manifold_geometry(self.gen_count, elites)
                    
                    valid_f = [g.fitness for g in self.population if g.fitness > -1.0]
                    mean_f = sum(valid_f) / len(valid_f) if valid_f else 0.0
                    
                    gen_elapsed = time.time() - gen_start_time
                    vram_peak_gb = torch.cuda.max_memory_allocated() / 1e9
                    vram_used = torch.cuda.memory_allocated() / 1e9
                    vram_reserved = torch.cuda.memory_reserved() / 1e9

                    # Machine-parseable summary (for scraping geometry metrics)
                    slog.info(f"[STEP:generation_summary] [GEN:{self.gen_count:03d}] "
                              f"best={current_best_f:.4f}, mean={mean_f:.4f}, sigma={self.sigma:.5f}, "
                              f"pr={geo_metrics.get('participation_ratio', 0.0):.2f}, "
                              f"elite_cos={geo_metrics.get('mean_cos', 0.0):.3f}, "
                              f"latency_s={gen_elapsed:.1f}, vram_peak_gb={vram_peak_gb:.2f}")

                    # Human-oriented single-grep trajectory line
                    n_falsified = sum(1 for g in self.population if g.fitness == -1.0)
                    n_productive = sum(
                        1 for g in self.population
                        if g.fitness > self.random_baseline_mean + 2 * self.random_baseline_std
                    )
                    _best_g = self.population[0]
                    slog.info(
                        f"[STEP:gen_summary] [GEN:{self.gen_count:03d}] "
                        f"mean_fit={mean_f:.4f}, best_fit={current_best_f:.4f}, "
                        f"sigma={self.sigma:.5f}, "
                        f"productive={n_productive}/{len(self.population)}, "
                        f"falsified={n_falsified}/{len(self.population)}, "
                        f"best_layer={_best_g.layer_index}, "
                        f"best_explore={_best_g.exploration_type.upper()}"
                    )

                    # Scout layer report for this generation
                    _scouts = [(g.layer_index, g.fitness) for g in self.population
                               if g.exploration_type == "scout" and g.fitness > -1.0]
                    if _scouts:
                        _scout_layers = sorted(set(l for l, _ in _scouts))
                        _scout_best_fit = max(f for _, f in _scouts)
                        _scout_best_layer = max(_scouts, key=lambda x: x[1])[0]
                        slog.info(
                            f"[STEP:scout_report] [GEN:{self.gen_count:03d}] "
                            f"layers_explored={_scout_layers}, "
                            f"scout_best_fit={_scout_best_fit:.4f}, "
                            f"scout_best_layer={_scout_best_layer}"
                        )

                    # Scout layer map CSV (cumulative, rewritten each gen)
                    try:
                        with open(self._scout_csv_path, "w", encoding="utf-8") as _csv:
                            _csv.write("layer,best_fitness,evals\n")
                            for _layer in sorted(self._layer_best.keys()):
                                _csv.write(f"{_layer},"
                                           f"{self._layer_best[_layer]:.6f},"
                                           f"{self._layer_evals.get(_layer, 0)}\n")
                    except Exception as _ce:
                        slog.warning(f"Scout CSV write failed (non-fatal): {_ce}")

                    # Full output JSON for this generation (for post-hoc marker analysis)
                    try:
                        _out_path = self._results_dir / f"gen_{self.gen_count:03d}_outputs.json"
                        with open(_out_path, "w", encoding="utf-8") as _of:
                            json.dump({"gen": self.gen_count, "genomes": _gen_outputs}, _of)
                    except Exception as _oe:
                        slog.warning(f"Output JSON write failed (non-fatal): {_oe}")

                    # Console generation summary
                    slog.info(f"Gen {self.gen_count:>3d}/{max_gens} │ "
                              f"best={current_best_f:.4f} │ σ={self.sigma:.5f} │ "
                              f"productive={n_productive}/{len(self.population)} │ "
                              f"falsified={n_falsified}/{len(self.population)} │ "
                              f"VRAM={vram_used:.1f}/{vram_peak_gb:.1f}GB peak │ "
                              f"{gen_elapsed:.1f}s")

                    self.gen_count += 1
                    self.save_state()

                    # ── Boundary 2: Stop Semaphore (between generations) ──
                    if self._check_stop_semaphore():
                        self._graceful_shutdown()
                        return

                    # Reset consecutive failure counter on success
                    consecutive_failures = 0

                    # VRAM hygiene
                    gc.collect()
                    torch.cuda.empty_cache()

                    # ── Periodic status dashboard (every 5 generations) ──
                    if self.gen_count % 5 == 0:
                        global_best = self.best_genome.fitness if self.best_genome else 0.0
                        vram_after_gc = torch.cuda.memory_allocated() / 1e9
                        print_visual_separator("─", 70,
                            f"STATUS @ Gen {self.gen_count}")
                        slog.info(
                            f"  Global best  : {global_best:.4f}\n"
                            f"  Random baseline: mean={self.random_baseline_mean:.4f}, "
                            f"max={self.random_baseline_max:.4f}\n"
                            f"  Sigma        : {self.sigma:.5f}\n"
                            f"  Plateau      : {self.plateau_count} gens\n"
                            f"  VRAM (post-GC): {vram_after_gc:.2f} GB\n"
                            f"  Model        : {self.model_target.name}\n"
                            f"  Layer        : {self.target_layer}/{self.n_layers}"
                        )

                except torch.cuda.OutOfMemoryError:
                    consecutive_failures += 1
                    slog.error(f"CUDA OOM at generation level (failure {consecutive_failures}/"
                               f"{MAX_CONSECUTIVE_FAILURES})")
                    gc.collect()
                    torch.cuda.empty_cache()
                    self.gen_count += 1  # skip this generation
                    self.save_state()

                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        slog.critical(f"Aborting model {self.model_target.name}: "
                                      f"{MAX_CONSECUTIVE_FAILURES} consecutive OOM failures")
                        return

                except Exception as e:
                    consecutive_failures += 1
                    slog.exception(f"Generation {self.gen_count} FAILED (failure "
                                   f"{consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}): {e}")
                    self.gen_count += 1  # skip
                    try:
                        self.save_state()
                    except Exception:
                        slog.error("Could not save state after generation failure")

                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        slog.critical(f"Aborting model {self.model_target.name}: "
                                      f"{MAX_CONSECUTIVE_FAILURES} consecutive failures")
                        return

        slog.info(f"Evolution COMPLETE for {self.model_target.name}: "
                  f"{self.gen_count} generations, best={self.last_best_fitness:.4f}")

    def _preflight_check(self):
        """Pre-flight validation: VRAM, config, environment.

        Called once at the start of run() before any model is loaded.
        Logs a summary of the environment so each run is self-documenting.
        """
        slog.info("─── PRE-FLIGHT CHECK ───")

        # 1. VRAM — ensure GPU is clean before we start
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
            allocated_mb = torch.cuda.memory_allocated() / 1e6
            reserved_mb = torch.cuda.memory_reserved() / 1e6
            total_mb = torch.cuda.get_device_properties(0).total_memory / 1e6
            gpu_name = torch.cuda.get_device_name(0)
            slog.info(f"GPU: {gpu_name} ({total_mb:.0f} MB total)")
            slog.info(f"VRAM: {allocated_mb:.1f} MB allocated, {reserved_mb:.1f} MB reserved")
            if allocated_mb > 100:
                slog.warning(f"VRAM not clean at startup ({allocated_mb:.0f} MB allocated). "
                             "Possible leaked tensors from a prior run.")
        else:
            slog.warning("No CUDA device detected — running on CPU (not recommended)")

        # 2. Config summary — log key parameters for reproducibility
        slog.info(f"Config: population={self.config.population_size}, "
                  f"seed_norm={self.config.seed_norm}, "
                  f"mutation_rate={self.config.mutation_rate}")
        slog.info(f"Models ({len(self.config.models)}): "
                  f"{[m.name for m in self.config.models]}")
        for m in self.config.models:
            effective_norm = m.seed_norm_override or self.config.seed_norm
            effective_sigma = m.sigma_override or self.config.mutation_rate
            slog.info(f"  {m.name}: seed_norm={effective_norm}, sigma={effective_sigma}, "
                      f"layer_ratio={m.target_layer_ratio:.0%}, "
                      f"gens_per_cycle={m.generations_per_cycle}")

        # 3. Stale state detection — warn if state files exist from a prior run
        for m in self.config.models:
            state_file = self.config.model_state_file(m)
            if state_file.exists():
                try:
                    state = torch.load(state_file, weights_only=False, map_location="cpu")
                    saved_norm = state['mean_vector'].norm().item()
                    saved_gen = state.get('gen_count', '?')
                    saved_sigma = state.get('sigma', '?')
                    effective_norm = m.seed_norm_override or self.config.seed_norm
                    norm_delta = abs(saved_norm - effective_norm) / max(effective_norm, 1e-8)
                    if norm_delta > 0.1:
                        slog.warning(
                            f"State/config MISMATCH for {m.name}: "
                            f"saved mean_norm={saved_norm:.2f} vs config seed_norm={effective_norm:.1f} "
                            f"(Δ={norm_delta:.0%}). Consider deleting state.json for a fresh start.")
                    else:
                        slog.info(f"Resuming {m.name} from gen={saved_gen}, "
                                  f"sigma={saved_sigma}, mean_norm={saved_norm:.2f}")
                except Exception:
                    slog.warning(f"Could not read state file for {m.name} — may be corrupt")
            else:
                slog.info(f"Fresh start for {m.name} (no saved state)")

        # 4. Results directory check
        slog.info(f"Results dir: {self.config.results_dir.resolve()}")
        if self.config.sync_output_dir:
            sync_ok = self.config.sync_output_dir.exists()
            slog.info(f"Sync dir: {self.config.sync_output_dir} "
                      f"({'OK' if sync_ok else 'NOT FOUND'})")

        slog.info("─── PRE-FLIGHT COMPLETE ───")

    def run(self):
        """Top-level entry point: cycle through all models."""
        self._preflight_check()

        slog.info("=" * 60)
        slog.info("Ignis MARATHON DEPLOYMENT")
        slog.info(f"Models: {[m.name for m in self.config.models]}")
        slog.info(f"Cycle continuously: {self.config.cycle_continuously}")
        slog.info("=" * 60)

        print_visual_separator("*", 80, "Ignis MARATHON DEPLOYMENT")

        cycle = 0
        try:
            while True:
                cycle += 1
                with LogContext(cycle=f"{cycle:03d}"):
                    slog.info(f"Cycle {cycle} BEGIN ({len(self.config.models)} models)")

                    for model_target in self.config.models:
                        # ── Boundary 3: Stop Semaphore (between models) ──
                        if self._check_stop_semaphore():
                             slog.info("Shutdown requested via semaphore — exiting marathon cycle")
                             self._graceful_shutdown()
                             return
                        try:
                            self.init_for_model(model_target)
                            self.run_evolution()

                            best_f = self.best_genome.fitness if self.best_genome else 0.0
                            slog.info(f"Model {model_target.name} cycle complete: "
                                      f"{self.gen_count} gens, best={best_f:.4f}")

                        except RuntimeError as e:
                            # init_for_model raises RuntimeError if model load fails
                            slog.error(f"Skipping model {model_target.name}: {e}")

                        except Exception as e:
                            slog.exception(f"Unexpected error with model {model_target.name}: {e}")

                        finally:
                            # VRAM cleanup before next model regardless of success/failure
                            if self.model is not None:
                                del self.model
                                self.model = None
                            gc.collect()
                            torch.cuda.empty_cache()
                            slog.debug("VRAM released after model cycle")

                    if not self.config.cycle_continuously:
                        slog.info("Single-pass mode — exiting after cycle 1")
                        break

                    slog.info(f"Cycle {cycle} COMPLETE — rotating back to first model")

        except KeyboardInterrupt:
            slog.warning("KeyboardInterrupt received — initiating graceful shutdown")
            self._graceful_shutdown()

    def _graceful_shutdown(self):
        """Save state, unload model, flush VRAM, and close logs cleanly."""
        # 1. Save CMA-ES state if we have an active model
        if self.model_target is not None:
            try:
                self.save_state()
                slog.info(f"State saved for {self.model_target.name} at gen {self.gen_count}")
            except Exception as e:
                slog.error(f"Failed to save state during shutdown: {e}")

        # 2. Unload model from VRAM
        if self.model is not None:
            del self.model
            self.model = None

        # 3. Flush VRAM
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            vram_after = torch.cuda.memory_allocated() / 1e9
            slog.info(f"VRAM released: {vram_after:.2f} GB remaining")

        # 4. Flush log handlers
        for handler in logging.getLogger("ignis").handlers:
            handler.flush()
            handler.close()

        # 5. Remove PID file
        if hasattr(self, 'pid_file') and self.pid_file.exists():
            self.pid_file.unlink()

        slog.info("Graceful shutdown complete")
        print("\n  >> Shutdown complete. State saved, VRAM released, logs flushed.")


if __name__ == "__main__":
    torch.cuda.set_device(0)
    orchestrator = IgnisOrchestrator()
    orchestrator.run()
