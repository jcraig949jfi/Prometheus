"""
Xenolexicon Novelty Fitness Engine

Replaces Ignis's MultiTaskCrucible with a novelty-scoring engine.
Instead of rewarding correctness, we reward structured distance from normal.

The novelty score is the product of two orthogonal axes:
  - Semantic Distance: how far the steered output is from the unsteered baseline
  - Structural Coherence: how internally organized the output is (sweet-spot perplexity)

High distance × high coherence = genuine structured novelty
High distance × low coherence  = random garbage
Low distance  × high coherence = normal output
"""

import math
import torch
from dataclasses import dataclass
from typing import Optional
from .seti_logger import slog, LogContext
from .tii_engine import TII_GENERATION_FAILED, get_steering_hook


# ── Provocation Prompts (Mathematical Domain MVP) ────────────────────

PROVOCATIONS = [
    {
        "name": "Open Conjecture",
        "prompt": (
            "Consider the relationship between prime gaps and digit sums. "
            "What patterns might exist that no one has described before? "
            "Think freely and speculatively."
        ),
    },
    {
        "name": "Concept Fusion",
        "prompt": (
            "What would happen if you applied the logic of topological "
            "invariants to number sequences? Describe any structure you see."
        ),
    },
    {
        "name": "Meta-Mathematical",
        "prompt": (
            "Describe a mathematical operation that doesn't exist yet "
            "but feels like it should. What would it do?"
        ),
    },
    {
        "name": "Boundary Probe",
        "prompt": (
            "What lies between a proof and a conjecture? Is there a "
            "third category of mathematical knowledge? Describe it."
        ),
    },
]


@dataclass
class NoveltyResult:
    """Result of evaluating a single provocation prompt."""
    provocation_name: str
    semantic_distance: float
    perplexity: float
    coherence: float
    novelty: float
    output_text: str
    output_embedding: Optional[torch.Tensor] = None


class NoveltyFitnessEngine:
    """
    Scores genomes on structured novelty rather than correctness.

    Requires a one-time baseline capture (unsteered model outputs and embeddings)
    before evaluation begins.
    """

    def __init__(self, target_perplexity: float = 50.0):
        self.target_perplexity = target_perplexity
        self.log_target = math.log(max(target_perplexity, 1.0))

        # Baseline cache (populated by capture_baselines)
        self.baseline_outputs: dict = {}       # provocation_name → text
        self.baseline_embeddings: dict = {}    # provocation_name → tensor [d_model]
        self._baselines_ready = False

        slog.trace(f"NoveltyFitnessEngine initialised: target_perplexity={target_perplexity}")

    def capture_baselines(self, model, max_new_tokens: int = 128):
        """
        Run the unsteered model on all provocations to establish baseline
        outputs and embeddings. Must be called once per model load.
        """
        slog.info(f"Capturing novelty baselines for {len(PROVOCATIONS)} provocations")
        self.baseline_outputs.clear()
        self.baseline_embeddings.clear()

        for prov in PROVOCATIONS:
            name = prov["name"]
            prompt = prov["prompt"]
            try:
                # Generate unsteered output
                input_tokens = model.to_tokens(prompt)
                output_tokens = model.generate(
                    input_tokens,
                    max_new_tokens=max_new_tokens,
                    stop_at_eos=True,
                    verbose=False,
                    prepend_bos=False,
                )
                output_text = model.to_string(output_tokens[0])
                self.baseline_outputs[name] = output_text

                # Capture final hidden state embedding (mean pool over output tokens)
                with torch.no_grad():
                    logits, cache = model.run_with_cache(output_tokens)
                    # Use the residual stream at the final layer
                    final_resid = cache[f"blocks.{model.cfg.n_layers - 1}.hook_resid_post"]
                    # Mean pool over all token positions
                    embedding = final_resid[0].mean(dim=0).float()
                    embedding = embedding / (embedding.norm() + 1e-10)
                    self.baseline_embeddings[name] = embedding

                slog.trace(f"Baseline '{name}': {len(output_text)} chars, "
                           f"emb_norm={embedding.norm().item():.4f}")

            except Exception as e:
                slog.error(f"Baseline capture failed for '{name}': {e}")
                self.baseline_outputs[name] = "[BASELINE_FAILED]"
                # Use a random unit vector as fallback embedding
                self.baseline_embeddings[name] = torch.randn(model.cfg.d_model).cuda().float()
                self.baseline_embeddings[name] /= self.baseline_embeddings[name].norm()

        self._baselines_ready = True
        slog.info(f"Baselines captured: {len(self.baseline_outputs)} provocations")

    def _compute_semantic_distance(self, output_embedding: torch.Tensor,
                                    baseline_embedding: torch.Tensor) -> float:
        """Cosine distance between steered and unsteered output embeddings."""
        cos_sim = torch.dot(output_embedding, baseline_embedding).item()
        # Cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite
        return max(0.0, 1.0 - cos_sim)

    def _compute_perplexity(self, model, text: str) -> float:
        """
        Compute perplexity of the text under the unsteered model.
        This measures how surprising the steered output is to the base model.
        """
        try:
            tokens = model.to_tokens(text)
            if tokens.shape[1] < 2:
                return 1.0  # Degenerate case

            with torch.no_grad():
                logits = model(tokens)

            # Shift: predict token[i+1] from logits[i]
            shift_logits = logits[0, :-1, :].float()
            shift_labels = tokens[0, 1:]

            log_probs = torch.log_softmax(shift_logits, dim=-1)
            token_log_probs = log_probs.gather(1, shift_labels.unsqueeze(1)).squeeze(1)

            # Perplexity = exp(-mean(log_probs))
            mean_log_prob = token_log_probs.mean().item()
            perplexity = math.exp(-mean_log_prob)

            return max(1.0, min(perplexity, 1e6))  # Clamp to reasonable range

        except Exception as e:
            slog.warning(f"Perplexity computation failed: {e}")
            return self.target_perplexity  # Neutral fallback

    def _compute_coherence(self, perplexity: float) -> float:
        """
        Coherence score based on distance from target perplexity.
        Sweet spot: moderate perplexity (surprising but structured).
        Score is 1.0 at target, decaying as a Gaussian in log-space.
        """
        log_ppl = math.log(max(perplexity, 1.0))
        distance = abs(log_ppl - self.log_target)
        # Gaussian with sigma=1.5 in log-perplexity space
        return math.exp(-(distance ** 2) / (2 * 1.5 ** 2))

    def _get_steered_embedding(self, model, genome, prompt: str,
                                max_new_tokens: int = 128) -> tuple:
        """
        Run steered generation and capture both the output text and its embedding.
        Returns (output_text, embedding_vector) or (sentinel, None) on failure.
        """
        layer = genome.layer_index
        vector = genome.vector
        pos_ratio = getattr(genome, 'position_ratio', 1.0)

        try:
            input_tokens = model.to_tokens(prompt)
            hook_name = f"blocks.{layer}.hook_resid_pre"

            # Generate steered output
            with model.hooks(fwd_hooks=[(hook_name,
                    get_steering_hook(vector, position_ratio=pos_ratio))]):
                output_tokens = model.generate(
                    input_tokens,
                    max_new_tokens=max_new_tokens,
                    stop_at_eos=True,
                    verbose=False,
                    prepend_bos=False,
                )

            output_text = model.to_string(output_tokens[0])

            # Capture embedding of the steered output (run WITHOUT steering
            # to get the base model's representation of the steered text)
            with torch.no_grad():
                logits, cache = model.run_with_cache(output_tokens)
                final_resid = cache[f"blocks.{model.cfg.n_layers - 1}.hook_resid_post"]
                embedding = final_resid[0].mean(dim=0).float()
                embedding = embedding / (embedding.norm() + 1e-10)

            return output_text, embedding

        except torch.cuda.OutOfMemoryError:
            slog.warning("CUDA OOM during steered generation")
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            return TII_GENERATION_FAILED, None

        except Exception as e:
            slog.exception(f"Steered generation failed: {e}")
            return TII_GENERATION_FAILED, None

    def evaluate_genome(self, model, genome) -> tuple:
        """
        Evaluate a genome's novelty across all provocation prompts.

        Returns:
            (fitness: float, metadata: dict, results: list[NoveltyResult])

        The fitness is the geometric mean of per-provocation novelty scores.
        """
        if not self._baselines_ready:
            raise RuntimeError("Must call capture_baselines() before evaluate_genome()")

        results = []
        novelty_scores = []

        for prov in PROVOCATIONS:
            name = prov["name"]
            prompt = prov["prompt"]

            try:
                with LogContext(provocation=name, step="steered_gen"):
                    output_text, embedding = self._get_steered_embedding(
                        model, genome, prompt
                    )

                    if output_text == TII_GENERATION_FAILED or embedding is None:
                        slog.warning(f"Generation failed for '{name}' — scoring floor")
                        results.append(NoveltyResult(
                            provocation_name=name,
                            semantic_distance=0.0,
                            perplexity=self.target_perplexity,
                            coherence=0.0,
                            novelty=0.01,
                            output_text="[GENERATION_FAILED]",
                        ))
                        novelty_scores.append(0.01)
                        continue

                with LogContext(provocation=name, step="scoring"):
                    # Semantic distance from baseline
                    baseline_emb = self.baseline_embeddings[name]
                    sem_dist = self._compute_semantic_distance(embedding, baseline_emb)

                    # Perplexity under unsteered model
                    # Score only the generated portion (strip prompt)
                    prompt_pos = output_text.find(prompt)
                    generated_text = (output_text[prompt_pos + len(prompt):]
                                      if prompt_pos != -1 else output_text)

                    ppl = self._compute_perplexity(model, generated_text)
                    coherence = self._compute_coherence(ppl)

                    # Combined novelty
                    novelty = sem_dist * coherence
                    novelty_scores.append(max(novelty, 0.01))

                    result = NoveltyResult(
                        provocation_name=name,
                        semantic_distance=sem_dist,
                        perplexity=ppl,
                        coherence=coherence,
                        novelty=novelty,
                        output_text=output_text,
                        output_embedding=embedding.cpu(),
                    )
                    results.append(result)

                    slog.trace(f"'{name}': dist={sem_dist:.4f}, ppl={ppl:.1f}, "
                               f"coh={coherence:.4f}, novelty={novelty:.4f}")

            except Exception as e:
                slog.exception(f"Provocation '{name}' evaluation failed: {e}")
                results.append(NoveltyResult(
                    provocation_name=name,
                    semantic_distance=0.0,
                    perplexity=self.target_perplexity,
                    coherence=0.0,
                    novelty=0.01,
                    output_text="[ERROR]",
                ))
                novelty_scores.append(0.01)

        # Geometric mean fitness
        if not novelty_scores:
            return 0.01, {}, results

        try:
            log_mean = sum(math.log(s) for s in novelty_scores) / len(novelty_scores)
            fitness = math.exp(log_mean)
        except (ValueError, OverflowError):
            fitness = 0.01

        # Metadata
        metadata = {
            "fitness": fitness,
            "per_provocation": {
                r.provocation_name: {
                    "semantic_distance": round(r.semantic_distance, 4),
                    "perplexity": round(r.perplexity, 2),
                    "coherence": round(r.coherence, 4),
                    "novelty": round(r.novelty, 4),
                }
                for r in results
            },
            "mean_semantic_distance": round(
                sum(r.semantic_distance for r in results) / len(results), 4
            ),
            "mean_coherence": round(
                sum(r.coherence for r in results) / len(results), 4
            ),
        }

        slog.debug(f"Novelty evaluation: fitness={fitness:.4f}, "
                   f"mean_dist={metadata['mean_semantic_distance']:.4f}, "
                   f"mean_coh={metadata['mean_coherence']:.4f}")

        return fitness, metadata, results
