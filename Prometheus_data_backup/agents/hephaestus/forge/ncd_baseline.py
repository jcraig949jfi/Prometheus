"""NCD (Normalized Compression Distance) Baseline Reasoning Tool.

Hand-crafted baseline using zlib compression to approximate Kolmogorov complexity.
Measures structural similarity between prompt and candidates via compression distance.
Provides a continuous fitness landscape (unlike hash-based approaches).

This is the quality floor: forged tools must beat NCD to survive.
"""

import zlib
import numpy as np


class ReasoningTool:
    def __init__(self, compression_level=6):
        self.level = compression_level

    def _c(self, text: str) -> int:
        """Compressed byte length of text."""
        return len(zlib.compress(text.encode("utf-8"), self.level))

    def _ncd(self, x: str, y: str) -> float:
        """Normalized Compression Distance. 0 = identical structure, 1 = unrelated."""
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        denom = max(cx, cy)
        if denom == 0:
            return 1.0
        return (cxy - min(cx, cy)) / denom

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by compression distance to prompt.

        Lower NCD = higher structural similarity = higher score.
        Includes information density penalty to prevent gaming via verbosity.
        """
        prompt_len = max(len(prompt), 1)
        results = []

        for cand in candidates:
            ncd_val = self._ncd(prompt, cand)

            # Information density: how compressible is the candidate itself?
            cand_raw_len = max(len(cand), 1)
            cand_compressed = self._c(cand)
            density = cand_compressed / cand_raw_len

            # Anti-echo: penalize candidates that are just bloated prompt copies
            echo_penalty = 1.2 if len(cand) > prompt_len * 2 else 1.0

            # Score: invert distance, penalize low-density and echo
            score = 1.0 / (1.0 + ncd_val * density * echo_penalty)

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"NCD={ncd_val:.4f}, density={density:.4f}",
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on NCD. Lower distance = higher confidence."""
        ncd_val = self._ncd(prompt, answer)
        conf = 1.0 - float(np.clip(ncd_val, 0.0, 1.0))
        return float(conf ** 2)
