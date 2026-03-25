"""RLVF Fitness Function — scoring reasoning traces with forged tools.

F(T) = Σ wᵢ · Sᵢ(T) - λ · σ(S)

Where:
- Sᵢ(T) = score from the i-th forged tool
- wᵢ = Coeus-derived weight (adversarial robustness)
- λ · σ(S) = Nemesis variance penalty (tool disagreement = gaming indicator)

This is the interface between the forge pipeline and Rhea's evolutionary loop.
Reasoning traces that satisfy more robust tools get higher fitness.
Traces that score high on one tool but low on others get penalized.

Usage:
    from rlvf_fitness import RLVFFitness
    fitness = RLVFFitness()
    score = fitness.score_trace(prompt, answer, candidates)
"""

import json
import logging
from pathlib import Path

import numpy as np

from test_harness import load_tool_from_file

log = logging.getLogger("hephaestus.rlvf")

HEPHAESTUS_ROOT = Path(__file__).resolve().parent.parent
FORGE_DIR = HEPHAESTUS_ROOT / "forge"
COEUS_ROOT = HEPHAESTUS_ROOT.parent / "coeus"


class RLVFFitness:
    """Multi-tool fitness function for reasoning trace evaluation.

    Loads all forged tools, weights them by Coeus adversarial robustness,
    and applies a variance penalty for tool disagreement.
    """

    def __init__(self, lambda_penalty: float = 2.0,
                 min_tools: int = 3):
        """
        Args:
            lambda_penalty: weight on the variance penalty term
            min_tools: minimum number of tools required to compute fitness
        """
        self.lambda_penalty = lambda_penalty
        self.min_tools = min_tools
        self.tools = {}       # name -> tool instance
        self.weights = {}     # name -> weight (adversarial robustness)
        self._load_tools()
        self._load_weights()

    def _load_tools(self):
        """Load all forged tools."""
        if not FORGE_DIR.exists():
            return
        for py in sorted(FORGE_DIR.glob("*.py")):
            try:
                tool = load_tool_from_file(py)
                self.tools[py.stem] = tool
            except Exception as e:
                log.debug("Skipping tool %s: %s", py.stem, e)
                continue
        log.info("RLVF loaded %d tools", len(self.tools))

    def _load_weights(self):
        """Load Coeus adversarial survival as tool weights.

        Tools with higher adversarial survival get higher weight.
        Tools without adversarial data get weight 1.0 (neutral).
        """
        scores_path = COEUS_ROOT / "graphs" / "concept_scores.json"
        if not scores_path.exists():
            self.weights = {name: 1.0 for name in self.tools}
            return

        try:
            data = json.loads(scores_path.read_text(encoding="utf-8"))
            adv_survival = data.get("adversarial_survival", {})

            for tool_name in self.tools:
                # Extract concept names from tool name
                parts = tool_name.split("_x_")
                concepts = [p.replace("_", " ").title() for p in parts]

                # Average adversarial survival across the tool's concepts
                rates = []
                for concept in concepts:
                    adv = adv_survival.get(concept, {})
                    rate = adv.get("survival_rate")
                    if rate is not None:
                        rates.append(rate)

                if rates:
                    self.weights[tool_name] = max(0.1, np.mean(rates))
                else:
                    self.weights[tool_name] = 1.0

        except Exception as e:
            log.warning("Failed to load Coeus weights: %s", e)
            self.weights = {name: 1.0 for name in self.tools}

        if self.weights:
            log.info("RLVF weights loaded: mean=%.2f, min=%.2f, max=%.2f",
                     np.mean(list(self.weights.values())),
                     min(self.weights.values()),
                     max(self.weights.values()))
        else:
            log.info("RLVF weights loaded: no weights (no tools)")

    def score_trace(self, prompt: str, answer: str,
                    candidates: list[str] | None = None) -> dict:
        """Score a reasoning trace using all forged tools.

        Args:
            prompt: the reasoning prompt
            answer: the model's answer
            candidates: optional list of candidate answers (for evaluate())

        Returns dict with:
            fitness: the composite RLVF fitness score
            tool_scores: per-tool scores
            weighted_scores: per-tool weighted scores
            variance: tool score variance (disagreement)
            penalty: the variance penalty applied
            n_tools: number of tools that scored
        """
        if len(self.tools) < self.min_tools:
            return {"fitness": 0.0, "error": "insufficient_tools",
                    "n_tools": len(self.tools)}

        tool_scores = {}
        weighted_scores = {}

        for name, tool in self.tools.items():
            try:
                # Use confidence as the primary score
                score = tool.confidence(prompt, answer)
                tool_scores[name] = float(score)
                w = self.weights.get(name, 1.0)
                weighted_scores[name] = float(score * w)
            except Exception as e:
                log.debug("Tool %s failed on scoring: %s", name, e)
                continue

        if len(tool_scores) < self.min_tools:
            return {"fitness": 0.0, "error": "too_few_scores",
                    "n_tools": len(tool_scores)}

        # F(T) = Σ wᵢ · Sᵢ(T) - λ · σ(S)
        scores_array = np.array(list(tool_scores.values()))
        weights_array = np.array([self.weights.get(name, 1.0)
                                  for name in tool_scores])

        # Normalize weights to sum to 1
        w_sum = weights_array.sum()
        if w_sum > 0:
            weights_norm = weights_array / w_sum
        else:
            weights_norm = np.ones_like(weights_array) / len(weights_array)

        weighted_sum = float(np.sum(scores_array * weights_norm))
        variance = float(np.var(scores_array))
        penalty = self.lambda_penalty * variance

        fitness = weighted_sum - penalty

        return {
            "fitness": round(float(fitness), 4),
            "weighted_sum": round(weighted_sum, 4),
            "variance": round(variance, 4),
            "penalty": round(penalty, 4),
            "n_tools": len(tool_scores),
            "tool_scores": {k: round(v, 4) for k, v in tool_scores.items()},
        }

    def score_candidates(self, prompt: str,
                         candidates: list[str]) -> list[dict]:
        """Score and rank multiple candidate answers.

        Returns list sorted by fitness descending.
        """
        results = []
        for cand in candidates:
            score = self.score_trace(prompt, cand, candidates)
            score["candidate"] = cand
            results.append(score)

        results.sort(key=lambda x: x.get("fitness", 0), reverse=True)
        return results

    def summary(self) -> str:
        """Human-readable summary of the fitness function state."""
        lines = [
            f"RLVF Fitness Function",
            f"  Tools: {len(self.tools)}",
            f"  Lambda (variance penalty): {self.lambda_penalty}",
        ]
        if self.weights:
            lines.append(
                f"  Weight range: {min(self.weights.values()):.2f} - {max(self.weights.values()):.2f}"
            )
        else:
            lines.append("  No weights loaded")

        # Show top/bottom weighted tools
        ranked = sorted(self.weights.items(), key=lambda x: -x[1])
        if ranked:
            lines.append(f"  Top tools (by adversarial weight):")
            for name, w in ranked[:5]:
                lines.append(f"    {name:50s} w={w:.3f}")
            lines.append(f"  Bottom tools:")
            for name, w in ranked[-3:]:
                lines.append(f"    {name:50s} w={w:.3f}")

        return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    fitness = RLVFFitness()
    print(fitness.summary())
    print()

    # Test on a simple prompt
    result = fitness.score_trace(
        "Is 9.11 larger than 9.9?",
        "No",
        ["Yes", "No"],
    )
    print(f"Score for correct answer 'No': {result['fitness']:.4f}")
    print(f"  Weighted sum: {result['weighted_sum']:.4f}")
    print(f"  Variance penalty: {result['penalty']:.4f}")
    print(f"  Tools scored: {result['n_tools']}")

    result2 = fitness.score_trace(
        "Is 9.11 larger than 9.9?",
        "Yes",
        ["Yes", "No"],
    )
    print(f"\nScore for wrong answer 'Yes': {result2['fitness']:.4f}")
    print(f"  Correct answer fitness advantage: {result['fitness'] - result2['fitness']:+.4f}")
