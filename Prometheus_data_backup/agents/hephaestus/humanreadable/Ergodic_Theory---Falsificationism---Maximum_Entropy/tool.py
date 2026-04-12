import math
import hashlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    EFME Engine Implementation (Ergodic-Falsification-Maximum-Entropy).
    
    Mechanism:
    1. MaxEnt Prior: Assigns initial probability based on candidate complexity 
       (length), favoring neither specific answers nor excessive complexity 
       (lambda * length).
    2. Ergodic Sampling: Uses a deterministic pseudo-random walk (seeded by prompt)
       to simulate exploring the hypothesis space without external randomness.
    3. Falsification Likelihood: Evaluates candidates against the prompt. 
       'Bold' predictions (specific, low prior) are penalized heavily if they 
       contradict prompt constraints (simulated via keyword logic).
    4. Posterior: Combines prior and falsification score to rank candidates.
    """

    def __init__(self):
        self.lambda_complexity = 0.1  # Constraint on model complexity
        self.beta_falsification = 2.0 # Strength of falsification penalty

    def _hash_seed(self, prompt: str) -> int:
        """Generate deterministic seed from prompt."""
        return int(hashlib.sha256(prompt.encode()).hexdigest()[:8], 16)

    def _compute_prior(self, candidate: str) -> float:
        """MaxEnt Prior: Exponential family based on complexity (length)."""
        complexity = len(candidate)
        # p(h) proportional to exp(-lambda * complexity)
        return math.exp(-self.lambda_complexity * complexity)

    def _compute_falsification_score(self, prompt: str, candidate: str) -> float:
        """
        Compute Falsification Score F(h).
        Returns 0.0 if consistent (survives), 1.0 if falsified.
        Simulates 'bold prediction' testing by checking for logical contradictions
        based on simple keyword heuristics.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Heuristic 1: Explicit negation in prompt vs candidate
        # If prompt says "not X" and candidate is "X", falsify.
        # Simple pattern matching for demonstration
        contradictions = [
            ("not ", "yes"), 
            ("impossible", "possible"),
            ("false", "true"),
            ("never", "always")
        ]
        
        falsified = False
        for neg_trigger, pos_claim in contradictions:
            if neg_trigger in p_lower and pos_claim in c_lower:
                # Check if the prompt actually contains the negation context
                # and the candidate asserts the positive.
                falsified = True
                break
        
        # Heuristic 2: Length mismatch as a proxy for "contradicting constraints"
        # If prompt asks for "short" and candidate is very long
        if "short" in p_lower and len(candidate) > 50:
            falsified = True
        if "long" in p_lower and len(candidate) < 10:
            falsified = True

        return 1.0 if falsified else 0.0

    def _ergodic_sample_score(self, prompt: str, candidate: str) -> float:
        """
        Simulate ergodic sampling convergence.
        In a real system, this averages over a Markov Chain.
        Here, we use a deterministic hash-based perturbation to simulate
        the 'time-average' converging to space-average for the given seed.
        """
        seed = self._hash_seed(prompt + candidate)
        # Deterministic pseudo-random factor simulating the ergodic path
        # This ensures different (prompt, candidate) pairs explore differently
        factor = ((seed % 1000) / 1000.0) * 0.1 - 0.05 
        return factor

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Normalize priors to avoid underflow in multiplication later
        priors = [self._compute_prior(c) for c in candidates]
        max_prior = max(priors) if priors else 1.0
        
        for i, candidate in enumerate(candidates):
            # 1. MaxEnt Prior
            prior = priors[i] / (max_prior + 1e-9)
            
            # 2. & 3. Falsification Likelihood
            # L(h|D) = exp(-beta * F(h))
            f_score = self._compute_falsification_score(prompt, candidate)
            likelihood = math.exp(-self.beta_falsification * f_score)
            
            # 4. Posterior Update (unnormalized)
            # We include the ergodic sampling term as a small regularization/noise
            # representing the exploration of the hypothesis space
            ergodic_term = 1.0 + self._ergodic_sample_score(prompt, candidate)
            
            posterior_score = prior * likelihood * ergodic_term
            
            # Generate reasoning string
            status = "Survived falsification" if f_score == 0 else "Falsified by constraints"
            reasoning = (
                f"Prior (complexity penalty): {prior:.4f}; "
                f"Falsification check: {status}; "
                f"Ergodic stability: {ergodic_term:.4f}"
            )
            
            results.append({
                "candidate": candidate,
                "score": posterior_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Derived from the posterior probability relative to a hypothetical 
        set of random alternatives.
        """
        # Evaluate the single answer in context
        # We simulate a comparison against a 'null' hypothesis to get a relative score
        eval_result = self.evaluate(prompt, [answer, "INVALID_ANSWER_PLACEHOLDER"])
        
        # Find the score of our answer
        target_score = 0.0
        total_score = 0.0
        
        for item in eval_result:
            if item["candidate"] == answer:
                target_score = item["score"]
            total_score += item["score"]
            
        if total_score == 0:
            return 0.0
            
        # Normalize to 0-1 range based on the binary comparison
        conf = target_score / total_score
        
        # Adjust for falsification: if it was falsified, confidence should be near 0
        # regardless of prior. The evaluate function handles the heavy lifting,
        # but we ensure strict bounds here.
        if self._compute_falsification_score(prompt, answer) == 1.0:
            return 0.05 # Very low confidence if falsified
            
        return min(1.0, max(0.0, conf))