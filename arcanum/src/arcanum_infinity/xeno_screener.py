"""
Xenolexicon Fast Screener — Rapid Genome Screening Mode

Cycles through a bank of provocation prompts, running short evolutionary
bursts on each to identify which prompts push the model into the most
fertile regions of structured novelty.

Usage:
    python run_screen.py --prompt-bank prompts.txt
    python run_screen.py --prompt-bank prompts.txt --screen-generations 3 --screen-population 10
    python run_screen.py --prompt-bank prompts.txt --screen-threshold 0.08 --resume

Design:
    - Loads the model ONCE (expensive), then reuses it for all prompts
    - For each prompt: resets CMA-ES state, runs a micro-burst, records best score
    - Writes a ranked CSV at the end so you can see which prompts are hottest
    - Supports --resume to skip prompts that have already been screened
"""

import torch
import math
import gc
import csv
import json
import time
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from .xeno_config import XenoConfig, ModelTarget
from .tii_engine import load_tii_model
from .genome import SteeringGenome
from .xeno_fitness import NoveltyFitnessEngine, PROVOCATIONS, NoveltyResult
from .specimen import capture_specimen
from .naming_engine import generate_specimen_name
from .xenolexicon_db import XenolexiconDB
from .alert import print_visual_separator
from .seti_logger import slog, LogContext


# ── Screening Configuration ──────────────────────────────────────────

@dataclass
class ScreenConfig:
    """Configuration specific to fast screening mode."""
    prompt_bank_path: Path = Path("prompts.txt")
    screen_generations: int = 2          # Generations per prompt burst
    screen_population: int = 10          # Genomes per generation (smaller = faster)
    screen_threshold: float = 0.10       # Min best score to flag as "HIT"
    capture_threshold: float = 0.20      # Lower capture threshold for fast mode
    resume: bool = False                 # Skip already-screened prompts
    results_dir: Path = Path("results/screening")
    start_index: int = 0                 # Start from this prompt index
    max_prompts: int = 0                 # 0 = all prompts


# ── Prompt Bank Loader ────────────────────────────────────────────────

def load_prompt_bank(path: Path) -> List[dict]:
    """
    Load prompts from a text file. Supports two formats:

    1. Simple: one question per line
    2. Sectioned: lines starting with [bracket] are section headers,
       lines starting with a digit are questions

    Returns list of {"name": str, "prompt": str, "source": str}
    """
    prompts = []
    current_source = "unknown"

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Section header: [chatgpt], [claude], [gemini pro], etc.
            if line.startswith("[") and line.endswith("]"):
                current_source = line[1:-1].strip()
                continue

            # Skip lines that are clearly metadata (like [Prompt])
            if line.startswith("["):
                current_source = line[1:-1].strip()
                continue

            # Numbered question: "1. What algebraic structure..."
            # or "1. What algebraic structure..."
            import re
            match = re.match(r'^\d+[\.\)]\s*(.+)', line)
            if match:
                question = match.group(1).strip()
                if len(question) > 20:  # Skip very short fragments
                    prompts.append({
                        "name": question[:60].replace(",", ";"),
                        "prompt": question,
                        "source": current_source,
                    })
                continue

            # Plain line (no number prefix) — treat as a question if long enough
            if len(line) > 30 and not line.startswith("-") and not line.startswith("*"):
                prompts.append({
                    "name": line[:60].replace(",", ";"),
                    "prompt": line,
                    "source": current_source,
                })

    return prompts


# ── The Fast Screener ─────────────────────────────────────────────────

class XenoScreener:
    """
    Rapid screening of provocation prompts for structured novelty potential.

    Loads the model once, then cycles through a bank of prompts. For each
    prompt, it resets CMA-ES, runs a short burst of evolution, and records
    the best novelty score. Prompts that score above the screening threshold
    are flagged as "HIT" for deeper exploration.
    """

    def __init__(self, xeno_config: XenoConfig, screen_config: ScreenConfig):
        self.xeno_config = xeno_config
        self.screen_config = screen_config
        self.results_dir = screen_config.results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Logging
        slog.configure(log_dir=self.results_dir / "logs")
        slog.info("Xenolexicon Fast Screener initialised")

        # State
        self.model = None
        self.model_target = None
        self.d_model = 0
        self.n_layers = 0
        self.target_layer = 0
        self.early_layer_cutoff = 0

        # Results tracking
        self.screening_results: List[dict] = []
        self.results_csv = self.results_dir / "screening_results.csv"
        self.results_jsonl = self.results_dir / "screening_log.jsonl"

        # Load existing results if resuming
        self._completed_prompts = set()
        if screen_config.resume and self.results_csv.exists():
            self._load_completed_prompts()

    def _load_completed_prompts(self):
        """Load already-screened prompts from previous run."""
        try:
            with open(self.results_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._completed_prompts.add(row.get("prompt", ""))
            slog.info(f"Resume mode: {len(self._completed_prompts)} prompts already screened")
        except Exception as e:
            slog.warning(f"Could not load previous results: {e}")

    def init_model(self):
        """Load model once for all screening runs."""
        model_target = self.xeno_config.models[0]
        self.model_target = model_target

        print_visual_separator("=", 80, f"SCREENING MODE: {model_target.name}")
        slog.info(f"Loading model: {model_target.name}")

        self.model = load_tii_model(model_target.name)
        if self.model is None:
            raise RuntimeError(f"Failed to load model {model_target.name}")

        self.d_model = self.model.cfg.d_model
        self.n_layers = self.model.cfg.n_layers
        self.target_layer = model_target.target_layer(self.n_layers)
        self.early_layer_cutoff = model_target.early_layer_cutoff(self.n_layers)

        vram = torch.cuda.memory_allocated() / 1e9
        slog.info(f"Model loaded: d_model={self.d_model}, n_layers={self.n_layers}, "
                  f"target_layer={self.target_layer}, VRAM={vram:.2f} GB")

    def _reset_cma_state(self):
        """Reset CMA-ES to fresh state for a new prompt screening burst."""
        pop_size = self.screen_config.screen_population
        mu = pop_size // 2

        self.mean_vector = torch.zeros(self.d_model).cuda()
        self.C = torch.ones(self.d_model).cuda()
        self.sigma = self.xeno_config.mutation_rate

        # Random init
        rand_init = torch.randn(self.d_model).cuda()
        seed_norm = (self.model_target.seed_norm_override
                     or self.xeno_config.seed_norm)
        self.mean_vector = rand_init / rand_init.norm() * seed_norm

        # CMA-ES weights for this population size
        self.mu = mu
        self.weights = (torch.log(torch.tensor(mu + 0.5))
                        - torch.log(torch.arange(1, mu + 1).float()))
        self.weights = self.weights / self.weights.sum()
        self.weights = self.weights.cuda()
        self.mueff = (self.weights.sum() ** 2 / (self.weights ** 2).sum()).item()

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

        self.gen_count = 0

    def _sample_population(self) -> List[SteeringGenome]:
        """Sample genomes from current CMA-ES distribution (screening size)."""
        pop = []
        pop_size = self.screen_config.screen_population

        for i in range(pop_size):
            z = torch.randn(self.d_model).cuda()
            vector = self.mean_vector + self.sigma * (self.C.sqrt() * z)

            # 80/20 layer exploration
            layer = self.target_layer
            exploration_type = "main"
            if torch.rand(1) < 0.2:
                low = int(0.3 * self.n_layers)
                high = int(0.9 * self.n_layers)
                layer = torch.randint(low, high + 1, (1,)).item()
                layer = max(self.early_layer_cutoff + 1, min(self.n_layers - 1, layer))
                exploration_type = "scout"

            pos_ratio = 1.0
            if torch.rand(1) < 0.2:
                pos_ratio = max(0.0, min(1.0, 1.0 + 0.3 * torch.randn(1).item()))

            pop.append(SteeringGenome(
                layer_index=layer, vector=vector, position_ratio=pos_ratio,
                exploration_type=exploration_type
            ))

        return pop

    def _update_distribution(self, sorted_pop: List[SteeringGenome]):
        """Diagonal CMA-ES update (same math as orchestrator)."""
        old_mean = self.mean_vector.clone()

        new_mean = torch.zeros_like(self.mean_vector)
        for i in range(self.mu):
            new_mean += self.weights[i] * sorted_pop[i].vector
        self.mean_vector = new_mean

        invsqrtC = 1.0 / self.C.sqrt()
        y = (self.mean_vector - old_mean) / self.sigma

        if not torch.isfinite(y).all():
            slog.warning("NaN/Inf in CMA-ES update — resetting paths")
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

        self.sigma *= math.exp((self.cs / self.damps) * (ps_norm / self.chiN - 1.0))

        self.C = ((1.0 - self.c1 - self.cmu) * self.C
                  + self.c1 * (self.pc ** 2
                               + (1.0 - hsig) * self.cc * (2.0 - self.cc) * self.C))

        for i in range(self.mu):
            diff = (sorted_pop[i].vector - old_mean) / self.sigma
            self.C += self.cmu * self.weights[i] * (diff ** 2)

        self.sigma = max(min(self.sigma, 10.0), 1e-5)
        self.C = torch.clamp(self.C, 1e-8, 1e6)

    def screen_single_prompt(self, prompt_info: dict, prompt_index: int,
                              total_prompts: int) -> dict:
        """
        Run a short evolutionary burst on a single provocation prompt.

        Returns a result dict with the prompt, best score, and timing info.
        """
        prompt_text = prompt_info["prompt"]
        source = prompt_info["source"]
        short_name = prompt_info["name"]

        slog.info(f"\n{'─' * 70}")
        slog.info(f"SCREENING [{prompt_index + 1}/{total_prompts}] "
                  f"({source}) {short_name}...")
        slog.info(f"  Full prompt: {prompt_text[:100]}...")

        # Temporarily replace PROVOCATIONS with just this one prompt
        # We monkey-patch the list in xeno_fitness so the engine evaluates
        # only this single prompt per genome (much faster)
        import arcanum_infinity.xeno_fitness as xf
        original_provocations = xf.PROVOCATIONS
        xf.PROVOCATIONS = [{
            "name": short_name,
            "prompt": prompt_text,
        }]

        # Create a fresh novelty engine and capture baseline for this prompt
        engine = NoveltyFitnessEngine(
            target_perplexity=self.xeno_config.target_perplexity,
        )
        engine.capture_baselines(self.model,
                                  max_new_tokens=self.xeno_config.max_new_tokens)

        # Reset CMA-ES
        self._reset_cma_state()

        burst_start = time.time()
        best_score = 0.0
        best_genome = None
        best_meta = None
        best_results = None
        gen_scores = []

        try:
            for gen in range(self.screen_config.screen_generations):
                gen_start = time.time()
                population = self._sample_population()

                # Evaluate all genomes
                for genome in population:
                    try:
                        score, meta, results = engine.evaluate_genome(
                            self.model, genome
                        )
                        genome.fitness = score

                        if score > best_score:
                            best_score = score
                            best_genome = genome
                            best_meta = meta
                            best_results = results

                    except torch.cuda.OutOfMemoryError:
                        gc.collect()
                        torch.cuda.empty_cache()
                        genome.fitness = -1.0
                    except Exception as e:
                        slog.warning(f"  Genome eval failed: {e}")
                        genome.fitness = -1.0

                # Sort and update CMA-ES
                population.sort(key=lambda x: x.fitness, reverse=True)
                self._update_distribution(population)
                self.gen_count += 1

                gen_best = population[0].fitness
                gen_scores.append(gen_best)
                gen_elapsed = time.time() - gen_start

                slog.info(f"  Gen {gen}: best={gen_best:.4f}, "
                          f"elapsed={gen_elapsed:.1f}s")

                # Early termination: if Gen 0 score is truly terrible, skip Gen 1
                if gen == 0 and gen_best < self.screen_config.screen_threshold * 0.3:
                    slog.info(f"  EARLY PUNT: Gen 0 score {gen_best:.4f} is too low")
                    break

        finally:
            # Restore original provocations
            xf.PROVOCATIONS = original_provocations

        burst_elapsed = time.time() - burst_start
        is_hit = best_score >= self.screen_config.screen_threshold

        # Determine verdict
        if best_score >= self.screen_config.capture_threshold:
            verdict = "CAPTURE"
        elif is_hit:
            verdict = "HIT"
        else:
            verdict = "SKIP"

        status_icon = {"CAPTURE": "🔥", "HIT": "✓", "SKIP": "·"}[verdict]

        slog.info(f"  {status_icon} [{verdict}] best={best_score:.4f} "
                  f"threshold={self.screen_config.screen_threshold} "
                  f"elapsed={burst_elapsed:.1f}s")

        result = {
            "index": prompt_index,
            "source": source,
            "prompt": prompt_text,
            "name": short_name,
            "best_score": round(best_score, 6),
            "gen_scores": [round(s, 6) for s in gen_scores],
            "verdict": verdict,
            "elapsed_seconds": round(burst_elapsed, 1),
            "layer": best_genome.layer_index if best_genome else -1,
        }

        # Include raw outputs if we found something interesting
        if best_results and (verdict in ["CAPTURE", "HIT"]):
            result["outputs"] = {r.provocation_name: r.output_text for r in best_results}

        # Write to JSONL immediately (crash-safe)
        try:
            with open(self.results_jsonl, "a", encoding="utf-8") as f:
                entry = {**result, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            slog.warning(f"JSONL write failed: {e}")

        # If this prompt hit capture threshold, try to grab a specimen
        if verdict == "CAPTURE" and best_genome and best_results:
            slog.info(f"  🧬 Attempting specimen capture for '{short_name}'")
            self._attempt_fast_capture(
                engine, best_genome, best_score, best_meta,
                best_results, prompt_info, prompt_index
            )

        gc.collect()
        torch.cuda.empty_cache()

        return result

    def _attempt_fast_capture(self, engine, genome, score, meta,
                               results, prompt_info, prompt_index):
        """
        Quick specimen capture during screening. Uses relaxed thresholds.
        """
        try:
            specimen_dir = self.results_dir / "specimens"
            specimen_dir.mkdir(parents=True, exist_ok=True)

            specimen = capture_specimen(
                genome=genome,
                generation=0,
                model_name=self.model_target.name,
                fitness=score,
                metadata=meta or {},
                novelty_results=results or [],
                results_dir=self.results_dir,
            )

            # Try naming
            try:
                name, description = generate_specimen_name(
                    model=self.model,
                    outputs=specimen.outputs,
                    generation=0,
                    layer=genome.layer_index,
                    specimen_id=specimen.specimen_id,
                    max_new_tokens=self.xeno_config.naming_max_tokens,
                )
                specimen.name = name
                specimen.description = description
            except Exception as e:
                slog.warning(f"  Naming failed: {e}")
                specimen.name = f"SCREEN-{prompt_index:03d}-L{genome.layer_index}"
                specimen.description = f"Fast screen capture from: {prompt_info['source']}"

            specimen.status = "screen_capture"

            slog.info(f"  🏆 Screen specimen: '{specimen.name}'")
            if specimen.description:
                slog.info(f"     {specimen.description[:120]}")

        except Exception as e:
            slog.error(f"  Screen capture failed: {e}")

    def run(self):
        """
        Main screening loop. Load prompts, load model, screen each prompt.
        """
        # Load prompt bank
        prompts = load_prompt_bank(self.screen_config.prompt_bank_path)
        if not prompts:
            slog.error(f"No prompts found in {self.screen_config.prompt_bank_path}")
            return

        slog.info(f"Loaded {len(prompts)} prompts from {self.screen_config.prompt_bank_path}")

        # Apply start_index and max_prompts
        start = self.screen_config.start_index
        end = len(prompts) if self.screen_config.max_prompts == 0 \
            else min(len(prompts), start + self.screen_config.max_prompts)
        prompts = prompts[start:end]

        slog.info(f"Screening prompts {start} to {start + len(prompts) - 1}")

        # Load model
        self.init_model()

        # Screen each prompt
        total = len(prompts)
        hits = 0
        captures = 0

        print_visual_separator("=", 80,
            f"FAST SCREENING: {total} prompts, "
            f"{self.screen_config.screen_generations} gens × "
            f"{self.screen_config.screen_population} genomes each")

        screen_start = time.time()

        for i, prompt_info in enumerate(prompts):
            # Resume support: skip already-screened prompts
            if self.screen_config.resume and prompt_info["prompt"] in self._completed_prompts:
                slog.info(f"  [SKIP] Already screened: {prompt_info['name'][:50]}...")
                continue

            try:
                result = self.screen_single_prompt(prompt_info, i, total)
                self.screening_results.append(result)

                if result["verdict"] == "HIT":
                    hits += 1
                elif result["verdict"] == "CAPTURE":
                    hits += 1
                    captures += 1

                # Progress summary every 10 prompts
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - screen_start
                    rate = (i + 1) / (elapsed / 60.0)
                    remaining = (total - i - 1) / rate if rate > 0 else 0
                    slog.info(f"\n{'═' * 70}")
                    slog.info(f"PROGRESS: {i + 1}/{total} screened | "
                              f"{hits} hits | {captures} captures | "
                              f"{rate:.1f} prompts/min | "
                              f"~{remaining:.0f} min remaining")
                    slog.info(f"{'═' * 70}")

            except KeyboardInterrupt:
                slog.info("Keyboard interrupt — saving results so far")
                break
            except Exception as e:
                slog.exception(f"Prompt {i} screening failed: {e}")
                self.screening_results.append({
                    "index": i,
                    "source": prompt_info.get("source", "?"),
                    "prompt": prompt_info["prompt"],
                    "name": prompt_info["name"],
                    "best_score": 0.0,
                    "gen_scores": [],
                    "verdict": "ERROR",
                    "elapsed_seconds": 0,
                    "layer": -1,
                })

        # Write final ranked results
        self._write_ranked_results()

        total_elapsed = time.time() - screen_start
        slog.info(f"\n{'═' * 70}")
        slog.info(f"SCREENING COMPLETE")
        slog.info(f"  Prompts screened: {len(self.screening_results)}/{total}")
        slog.info(f"  Hits (≥{self.screen_config.screen_threshold}): {hits}")
        slog.info(f"  Captures (≥{self.screen_config.capture_threshold}): {captures}")
        slog.info(f"  Total time: {total_elapsed / 60:.1f} minutes")
        slog.info(f"  Results: {self.results_csv}")
        slog.info(f"{'═' * 70}")

        # Cleanup
        if self.model is not None:
            del self.model
            self.model = None
            gc.collect()
            torch.cuda.empty_cache()

    def _write_ranked_results(self):
        """Write screening results as a ranked CSV, best scores first."""
        ranked = sorted(self.screening_results,
                        key=lambda r: r["best_score"], reverse=True)

        with open(self.results_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "rank", "verdict", "best_score", "source", "prompt",
                "gen_scores", "layer", "elapsed_s"
            ])
            for rank, r in enumerate(ranked, 1):
                writer.writerow([
                    rank,
                    r["verdict"],
                    r["best_score"],
                    r["source"],
                    r["prompt"],
                    json.dumps(r["gen_scores"]),
                    r["layer"],
                    r["elapsed_seconds"],
                ])

        slog.info(f"Ranked results written to {self.results_csv}")

        # Also print top 10 to console
        print(f"\n{'═' * 70}")
        print(f"  TOP PROMPTS BY NOVELTY SCORE")
        print(f"{'═' * 70}")
        for rank, r in enumerate(ranked[:10], 1):
            icon = {"CAPTURE": "🔥", "HIT": "✓", "SKIP": "·", "ERROR": "✗"}
            print(f"  {rank:>2}. [{icon.get(r['verdict'], '?')}] {r['best_score']:.4f} "
                  f"({r['source']}) {r['prompt'][:65]}...")
        if len(ranked) > 10:
            print(f"  ... and {len(ranked) - 10} more in {self.results_csv}")
        print(f"{'═' * 70}\n")
