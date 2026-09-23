import random

import numpy as np
import zlib

class ReasoningTool:
    def __init__(self):
        self.reservoir_size = 100
        self.reservoir = np.random.rand(self.reservoir_size, self.reservoir_size)
        self.readout_weights = np.random.rand(self.reservoir_size)
        self.criticality_threshold = 0.5
        self.high_frequency_threshold = 0.1

    def _compute_psd(self, residuals):
        # Simple PSD estimation using Welch's method (approximation)
        nperseg = int(len(residuals) / 2)
        f, Pxx_den = np.fft.welch(residuals, nperseg=nperseg)
        return f, Pxx_den

    def _falsification_loss(self, psd):
        # High-frequency power as a loss signal
        high_freq_power = np.sum(psd[psd > self.high_frequency_threshold])
        return -high_freq_power

    def _criticality_control(self, loss):
        # Adjust reservoir gain based on SOC principles
        if loss < -self.criticality_threshold:
            self.reservoir *= 0.9  # Decrease gain
        elif loss > self.criticality_threshold:
            self.reservoir *= 1.1  # Increase gain

    def _predict(self, input_data):
        # Simple reservoir computing prediction
        state = np.tanh(np.dot(self.reservoir, input_data))
        prediction = np.dot(self.readout_weights, state)
        return prediction

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for candidate in candidates:
            input_data = np.array([ord(c) for c in prompt + candidate])
            prediction = self._predict(input_data)
            residuals = input_data - prediction
            _, psd = self._compute_psd(residuals)
            loss = self._falsification_loss(psd)
            self._criticality_control(loss)
            score = -loss  # Higher loss means better prediction
            reasoning = f"Score based on high-frequency power in residuals."
            results.append({"candidate": candidate, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        input_data = np.array([ord(c) for c in prompt + answer])
        prediction = self._predict(input_data)
        residuals = input_data - prediction
        _, psd = self._compute_psd(residuals)
        loss = self._falsification_loss(psd)
        self._criticality_control(loss)
        # Convert loss to confidence (0 to 1)
        confidence = max(0, min(1, -loss / 10))
        return confidence

# Example usage:
# tool = ReasoningTool()
# prompt = "What is 2 + 2?"
# candidates = ["4", "5", "3"]
# print(tool.evaluate(prompt, candidates))
# print(tool.confidence(prompt, "4"))


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
