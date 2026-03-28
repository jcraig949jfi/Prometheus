"""
fitness.py — Margin-over-NCD accuracy + Brier calibration + NCD independence.
"""

import numpy as np
import zlib
from dataclasses import dataclass, asdict


@dataclass
class FitnessVector:
    adjusted_margin_accuracy: float = 0.0
    margin_calibration: float = 0.0
    novelty_score: float = 0.0
    ncd_independence: float = 0.0
    raw_accuracy: float = 0.0
    raw_brier: float = 1.0
    raw_confidence_correct: float = 0.0
    crash_count: int = 0
    gene_count: int = 0

    def as_array(self) -> np.ndarray:
        """Return the 3 Pareto objectives as an array (all maximized)."""
        return np.array([
            self.adjusted_margin_accuracy,
            self.margin_calibration,
            self.novelty_score
        ])


class NCDBaseline:
    """Standalone NCD implementation for baseline computation."""

    def _ncd(self, s1: str, s2: str) -> float:
        b1 = s1.encode('utf-8', errors='replace')
        b2 = s2.encode('utf-8', errors='replace')
        b12 = (s1 + s2).encode('utf-8', errors='replace')
        l1 = len(zlib.compress(b1))
        l2 = len(zlib.compress(b2))
        l12 = len(zlib.compress(b12))
        if max(l1, l2) == 0:
            return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list) -> list:
        results = []
        for cand in candidates:
            ncd = self._ncd(prompt, cand)
            score = 1.0 - ncd  # Lower NCD = higher similarity = higher score
            results.append({'candidate': cand, 'score': score, 'reasoning': 'NCD baseline'})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ncd = self._ncd(prompt, answer)
        return max(0.0, min(1.0, 1.0 - ncd))


def compute_ncd_baseline(tasks: list) -> dict:
    """Compute NCD baseline accuracy and Brier score on tasks."""
    ncd = NCDBaseline()
    n_correct = 0
    brier_sum = 0.0

    for task in tasks:
        results = ncd.evaluate(task['prompt'], task['candidates'])
        if results:
            top = results[0]['candidate']
            correct = (top == task['correct'])
            if correct:
                n_correct += 1
            conf = ncd.confidence(task['prompt'], results[0]['candidate'])
            brier = (conf - (1.0 if correct else 0.0)) ** 2
            brier_sum += brier

    n = len(tasks)
    return {
        'accuracy': n_correct / n if n > 0 else 0.0,
        'brier': brier_sum / n if n > 0 else 1.0,
    }


def compute_fitness(task_results: list, ncd_baseline: dict,
                    ncd_independence: float = 1.0,
                    ncd_independence_weight: float = 0.5,
                    gene_count: int = 0) -> FitnessVector:
    """Compute fitness from per-task evaluation results."""
    n = len(task_results)
    if n == 0:
        return FitnessVector()

    # Accuracy
    n_correct = sum(1 for r in task_results if r.get('correct', False))
    raw_accuracy = n_correct / n

    # Brier score
    brier_sum = 0.0
    for r in task_results:
        correct = r.get('correct', False)
        conf = r.get('confidence_correct', 0.0) if correct else r.get('confidence_wrong', 0.0)
        # If correct, we want conf close to 1. If wrong, we want conf close to 0.
        # But confidence is always for the TOP-RANKED candidate
        if correct:
            brier_sum += (r.get('confidence_correct', 0.0) - 1.0) ** 2
        else:
            brier_sum += (r.get('confidence_correct', 0.0) - 0.0) ** 2
    raw_brier = brier_sum / n

    # Margins over NCD
    margin_accuracy = raw_accuracy - ncd_baseline.get('accuracy', 0.0)

    # Adjusted margin (NCD independence penalty)
    adjusted_margin = margin_accuracy * (ncd_independence_weight + (1 - ncd_independence_weight) * ncd_independence)

    # Calibration: 1 - brier, then subtract NCD's
    margin_calibration = (1.0 - raw_brier) - (1.0 - ncd_baseline.get('brier', 1.0))

    crash_count = sum(1 for r in task_results if r.get('error'))

    return FitnessVector(
        adjusted_margin_accuracy=adjusted_margin,
        margin_calibration=margin_calibration,
        novelty_score=0.0,  # Filled later by novelty module
        ncd_independence=ncd_independence,
        raw_accuracy=raw_accuracy,
        raw_brier=raw_brier,
        raw_confidence_correct=sum(r.get('confidence_correct', 0.0) for r in task_results) / n,
        crash_count=crash_count,
        gene_count=gene_count,
    )
