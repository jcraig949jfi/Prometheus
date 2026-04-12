"""
fitness.py — 6-dimensional fitness for NSGA-II selection.

Dimensions (all maximized):
1. Accuracy margin over NCD baseline
2. Calibration (1 - Brier score, margin over NCD)
3. Ablation delta (min per-primitive impact — BYPASS KILLER)
4. Generalization (held-out accuracy margin)
5. Diversity (novelty score from archive)
6. Parsimony (fewer primitives preferred)
"""

import zlib
import numpy as np
from dataclasses import dataclass, field


@dataclass
class FitnessVector:
    # The 6 Pareto objectives (all maximized by NSGA-II)
    accuracy_margin: float = 0.0
    calibration: float = 0.0
    ablation_delta: float = 0.0
    generalization: float = 0.0
    diversity: float = 0.0
    parsimony: float = 0.0

    # Raw diagnostics (not in Pareto array)
    raw_accuracy: float = 0.0
    raw_brier: float = 1.0
    crash_count: int = 0
    primitive_count: int = 0
    ncd_independence: float = 0.0
    ablation_details: dict = field(default_factory=dict)

    def as_array(self) -> np.ndarray:
        """Return the 6 Pareto objectives as numpy array."""
        arr = np.array([
            self.accuracy_margin,
            self.calibration,
            self.ablation_delta,
            self.generalization,
            self.diversity,
            self.parsimony,
        ])
        return np.nan_to_num(arr, nan=-1.0, posinf=0.0, neginf=-1.0)


class NCDBaseline:
    """NCD implementation for baseline computation."""

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
            score = 1.0 - ncd
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
                    ncd_weight: float = 1.0,
                    primitive_count: int = 0) -> FitnessVector:
    """Compute fitness from per-task evaluation results.

    Args:
        task_results: list of dicts with 'correct', 'confidence_correct', etc.
        ncd_baseline: dict with 'accuracy' and 'brier'
        ncd_weight: NCD decay weight (1.0 full, 0.5 half, 0.0 raw)
        primitive_count: number of primitives in organism
    """
    n = len(task_results)
    if n == 0:
        return FitnessVector(primitive_count=primitive_count)

    # Accuracy
    n_correct = sum(1 for r in task_results if r.get('correct', False))
    raw_accuracy = n_correct / n

    # Brier score
    brier_sum = 0.0
    for r in task_results:
        correct = r.get('correct', False)
        conf = r.get('confidence_correct', 0.0)
        if correct:
            brier_sum += (conf - 1.0) ** 2
        else:
            brier_sum += (conf - 0.0) ** 2
    raw_brier = brier_sum / n

    # Margins over NCD (weighted by decay)
    ncd_acc = ncd_baseline.get('accuracy', 0.0) * ncd_weight
    accuracy_margin = raw_accuracy - ncd_acc

    ncd_cal = (1.0 - ncd_baseline.get('brier', 1.0)) * ncd_weight
    calibration = (1.0 - raw_brier) - ncd_cal

    # Parsimony: fewer primitives = higher score. Normalize: 1/count
    parsimony = 1.0 / max(primitive_count, 1)

    crash_count = sum(1 for r in task_results if r.get('error'))

    return FitnessVector(
        accuracy_margin=accuracy_margin,
        calibration=calibration,
        parsimony=parsimony,
        raw_accuracy=raw_accuracy,
        raw_brier=raw_brier,
        crash_count=crash_count,
        primitive_count=primitive_count,
        # ablation_delta, generalization, diversity filled by caller
    )
