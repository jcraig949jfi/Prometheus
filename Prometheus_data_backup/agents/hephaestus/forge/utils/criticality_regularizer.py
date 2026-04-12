"""Criticality Regularizer — extracted from ME-CGA (Tier 2).

Not a standalone ReasoningTool. A meta-criterion that measures whether
a tool's scoring landscape has useful gradient (discriminative power).

If all candidates score the same (flat landscape), the tool isn't
discriminating. If one candidate dominates trivially, the landscape
is degenerate. The sweet spot is "critical" — where small differences
in candidate quality produce meaningful score differences.

Usage:
    base_tool = SomeReasoningTool()
    reg = CriticalityRegularizer(base_tool)
    adjusted = reg.regularized_evaluate(prompt, candidates)
    quality = reg.landscape_quality(prompt, candidates)
"""

import numpy as np


class CriticalityRegularizer:
    def __init__(self, base_tool, target_variance: float = 0.1):
        self.base = base_tool
        self.target_variance = target_variance

    def landscape_quality(self, prompt: str, candidates: list) -> dict:
        """Measure the quality of the scoring landscape.

        Returns dict with:
          - variance: raw score variance
          - entropy: Shannon entropy of normalized scores
          - criticality: how close variance is to target (1.0 = perfect)
          - is_flat: True if all scores are nearly identical
          - is_degenerate: True if one score dominates
        """
        results = self.base.evaluate(prompt, candidates)
        if not results or len(results) < 2:
            return {
                "variance": 0.0, "entropy": 0.0, "criticality": 0.0,
                "is_flat": True, "is_degenerate": False,
            }

        scores = np.array([r["score"] for r in results], dtype=np.float64)

        # Normalize to probability distribution
        shifted = scores - scores.min()
        total = shifted.sum()
        if total < 1e-12:
            return {
                "variance": 0.0, "entropy": 0.0, "criticality": 0.0,
                "is_flat": True, "is_degenerate": False,
            }

        probs = shifted / total
        probs = probs[probs > 0]

        variance = float(np.var(scores))
        entropy = float(-np.sum(probs * np.log2(probs)))
        max_entropy = np.log2(len(scores))

        # Criticality: Gaussian centered on target variance
        criticality = float(np.exp(
            -((variance - self.target_variance) ** 2)
            / (2 * self.target_variance ** 2 + 1e-12)
        ))

        is_flat = variance < 1e-6
        is_degenerate = (scores.max() - scores.min()) > 0 and (
            probs.max() > 0.95
        )

        return {
            "variance": variance,
            "entropy": entropy,
            "norm_entropy": float(entropy / max_entropy) if max_entropy > 0 else 0.0,
            "criticality": criticality,
            "is_flat": is_flat,
            "is_degenerate": is_degenerate,
        }

    def regularized_evaluate(self, prompt: str, candidates: list) -> list:
        """Run base evaluate, then adjust scores toward critical regime.

        If landscape is flat: amplify small differences.
        If landscape is degenerate: compress toward mean.
        If landscape is critical: leave scores alone.
        """
        results = self.base.evaluate(prompt, candidates)
        if not results or len(results) < 2:
            return results

        scores = np.array([r["score"] for r in results], dtype=np.float64)
        quality = self.landscape_quality(prompt, candidates)

        mean_s = scores.mean()
        std_s = scores.std() + 1e-12

        if quality["is_flat"]:
            # Amplify differences by stretching around mean
            adjusted = mean_s + (scores - mean_s) * 3.0
        elif quality["is_degenerate"]:
            # Compress toward mean to reduce dominance
            adjusted = mean_s + (scores - mean_s) * 0.5
        else:
            # Near critical — apply mild criticality weighting
            adjusted = scores * (0.8 + 0.2 * quality["criticality"])

        # Re-normalize to [0, 1]
        a_min, a_max = adjusted.min(), adjusted.max()
        if a_max - a_min > 1e-12:
            adjusted = (adjusted - a_min) / (a_max - a_min)
        else:
            adjusted = np.full_like(adjusted, 0.5)

        out = []
        for i, r in enumerate(results):
            out.append({
                "candidate": r["candidate"],
                "score": float(adjusted[i]),
                "reasoning": (
                    f"{r['reasoning']}; "
                    f"crit={quality['criticality']:.3f}, "
                    f"var={quality['variance']:.4f}"
                ),
            })
        out.sort(key=lambda r: r["score"], reverse=True)
        return out
