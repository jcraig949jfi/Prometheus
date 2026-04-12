"""Perturbation Calibrator — extracted from EATM-S (Tier 2).

Not a standalone ReasoningTool. A confidence wrapper that takes any
base tool and calibrates its confidence by measuring stability across
prompt perturbations.

If a candidate scores consistently across perturbed versions of the
prompt, it's more robust. High variance = fragile = lower confidence.

Usage:
    base_tool = SomeReasoningTool()
    calibrator = PerturbationCalibrator(base_tool)
    calibrated_conf = calibrator.calibrated_confidence(prompt, answer)
    calibrated_rankings = calibrator.calibrated_evaluate(prompt, candidates)
"""

import re
import numpy as np


class PerturbationCalibrator:
    def __init__(self, base_tool, n_perturbations: int = 5):
        self.base = base_tool
        self.n_perturbations = n_perturbations

    def _perturb_prompt(self, prompt: str) -> list:
        """Generate deterministic prompt perturbations."""
        perturbations = [prompt]  # always include original

        words = prompt.split()

        # 1. Drop each content word (skip short function words)
        content_words = [w for w in words if len(w) > 3]
        if content_words:
            # Drop the longest content word
            drop = max(content_words, key=len)
            perturbations.append(" ".join(w for w in words if w != drop))

        # 2. Reverse clause order (split on punctuation)
        clauses = re.split(r"[.?!,;]", prompt)
        clauses = [c.strip() for c in clauses if c.strip()]
        if len(clauses) > 1:
            perturbations.append(". ".join(reversed(clauses)))

        # 3. Add "explain why" suffix
        perturbations.append(prompt.rstrip("?.!") + " explain why")

        # 4. Remove negation (tests if answer is stable under negation flip)
        neg_removed = re.sub(
            r"\b(not|never|no|n't)\b", "", prompt, flags=re.IGNORECASE
        ).strip()
        if neg_removed != prompt:
            perturbations.append(neg_removed)

        # 5. Paraphrase: swap "is" -> "are" or vice versa (shallow)
        swapped = prompt.replace(" is ", " are ").replace(" Is ", " Are ")
        if swapped != prompt:
            perturbations.append(swapped)

        return perturbations[: self.n_perturbations + 1]

    def calibrated_confidence(self, prompt: str, answer: str) -> float:
        """Run base tool's confidence across perturbations. Return stability-weighted mean."""
        perturbations = self._perturb_prompt(prompt)

        confs = []
        for p in perturbations:
            try:
                c = self.base.confidence(p, answer)
                confs.append(float(c))
            except Exception:
                confs.append(0.0)

        if not confs:
            return 0.0

        mean_conf = float(np.mean(confs))
        var_conf = float(np.var(confs))

        # Stability reward: low variance -> high weight
        stability = 1.0 / (1.0 + var_conf * 10)

        return float(np.clip(mean_conf * stability, 0.0, 1.0))

    def calibrated_evaluate(self, prompt: str, candidates: list) -> list:
        """Run base evaluate, then re-weight scores by perturbation stability."""
        base_results = self.base.evaluate(prompt, candidates)
        if not base_results:
            return base_results

        perturbations = self._perturb_prompt(prompt)

        # Gather scores across perturbations for each candidate
        cand_scores = {r["candidate"]: [] for r in base_results}

        for p in perturbations:
            try:
                perturbed = self.base.evaluate(p, candidates)
                score_map = {r["candidate"]: r["score"] for r in perturbed}
                for cand in cand_scores:
                    cand_scores[cand].append(score_map.get(cand, 0.0))
            except Exception:
                for cand in cand_scores:
                    cand_scores[cand].append(0.0)

        # Re-weight by stability
        results = []
        for r in base_results:
            scores = cand_scores[r["candidate"]]
            mean_s = float(np.mean(scores))
            var_s = float(np.var(scores))
            stability = 1.0 / (1.0 + var_s * 10)
            adjusted = mean_s * stability

            results.append({
                "candidate": r["candidate"],
                "score": float(adjusted),
                "reasoning": (
                    f"{r['reasoning']}; "
                    f"perturbation_stability={stability:.3f}"
                ),
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results
