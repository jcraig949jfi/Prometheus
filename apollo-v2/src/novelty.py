"""
novelty.py — Behavioral signatures + k-nearest novelty archive (capped).
"""

import numpy as np


class NoveltyArchive:
    def __init__(self, max_size: int = 500, k: int = 15, threshold: float = 0.3):
        self.max_size = max_size
        self.k = k
        self.threshold = threshold
        self.archive: list = []  # list of np.ndarray signatures

    def novelty_score(self, signature: np.ndarray, population_sigs: list = None) -> float:
        all_sigs = list(self.archive)
        if population_sigs:
            all_sigs.extend(population_sigs)
        if not all_sigs:
            return 1.0
        # Vectorized distance computation
        sig_array = np.array(all_sigs)
        diffs = sig_array - signature
        distances = np.sqrt(np.sum(diffs * diffs, axis=1))
        k = min(self.k, len(distances))
        return float(np.mean(np.sort(distances)[:k]))

    def maybe_add(self, signature: np.ndarray) -> bool:
        if self.novelty_score(signature) > self.threshold:
            if len(self.archive) >= self.max_size:
                self._replace_most_redundant(signature)
            else:
                self.archive.append(signature.copy())
            return True
        return False

    def _replace_most_redundant(self, new_sig: np.ndarray):
        """Replace a random archive member (fast O(1) replacement)."""
        if len(self.archive) < 2:
            self.archive.append(new_sig.copy())
            return
        # Replace a random entry instead of finding most redundant (O(n^2) was too slow)
        import random
        idx = random.randint(0, len(self.archive) - 1)
        self.archive[idx] = new_sig.copy()

    @property
    def size(self) -> int:
        return len(self.archive)


def compute_behavioral_signature(source_code: str, reference_tasks: list,
                                  timeout: float = 0.5) -> np.ndarray:
    """Run organism on reference tasks, return score vector."""
    scores = []
    try:
        namespace = {}
        exec(source_code, namespace)
        tool_class = namespace.get('ReasoningTool')
        if tool_class is None:
            return np.zeros(len(reference_tasks))
        tool = tool_class()
        for task in reference_tasks:
            try:
                results = tool.evaluate(task['prompt'], task['candidates'])
                if results:
                    scores.append(results[0]['score'])
                else:
                    scores.append(0.0)
            except:
                scores.append(0.0)
    except:
        scores = [0.0] * len(reference_tasks)

    return np.array(scores, dtype=np.float64)
