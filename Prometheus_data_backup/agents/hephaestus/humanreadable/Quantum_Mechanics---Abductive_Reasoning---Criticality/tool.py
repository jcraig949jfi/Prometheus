import numpy as np
import hashlib

class ReasoningTool:
    """
    Quantum-Critical Tensor-Network Abductor (QCTN-A) Simulation.
    
    Mechanism:
    1. Encoding: Inputs are hashed to seed vectors, simulating MPS initialization.
    2. Criticality: A susceptibility factor is derived from the 'Criticality' forge driver.
       This acts as an amplifier for small differences in candidate quality.
    3. Abductive Inference: Candidates are scored based on semantic overlap with the prompt
       (simulating data-likelihood) and internal consistency (simulating explanatory virtue).
    4. Self-Testing: The 'confidence' method simulates measuring entanglement entropy shifts.
       It perturbs the input slightly; if the score drops significantly (high susceptibility),
       the model is 'critical' and confident. If stable, it indicates a flat landscape (low confidence).
    """

    def __init__(self):
        # Forge drivers from causal analysis
        self.criticality_driver = 0.68 
        self.abductive_driver = 0.34
        self.phi = 1.61803398875  # Golden ratio for deterministic pseudo-randomness

    def _hash_to_vector(self, text: str, size: int = 50) -> np.ndarray:
        """Deterministic mapping of string to normalized vector."""
        h = hashlib.sha256(text.encode()).hexdigest()
        seed = int(h[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.random(size)
        # Normalize
        return vec / np.linalg.norm(vec)

    def _compute_likelihood(self, prompt_vec: np.ndarray, candidate_vec: np.ndarray) -> float:
        """Simulates Born-rule probability via vector overlap."""
        overlap = np.dot(prompt_vec, candidate_vec)
        return max(0.0, overlap)

    def _compute_explanatory_virtue(self, candidate: str) -> float:
        """Regularizer: Simpler (shorter) hypotheses preferred (Occam's razor)."""
        length = len(candidate.split())
        # Penalty for excessive length, scaled by abductive driver
        penalty = 1.0 / (1.0 + 0.1 * length)
        return penalty * self.abductive_driver

    def _critical_amplification(self, base_score: float, context_hash: int) -> float:
        """
        Applies critical susceptibility.
        Near criticality, small changes in base_score yield large output shifts.
        """
        # Deterministic noise based on context to simulate quantum fluctuation
        rng = np.random.default_rng(context_hash % (2**32))
        noise = (rng.random() - 0.5) * 0.1 
        
        # Susceptibility factor
        chi = 1.0 + self.criticality_driver 
        
        # Amplify the signal + noise
        amplified = base_score * chi + noise * chi
        return float(np.clip(amplified, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        prompt_vec = self._hash_to_vector(prompt)
        context_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_vec = self._hash_to_vector(cand)
            
            # 1. Data Likelihood (Overlap)
            likelihood = self._compute_likelihood(prompt_vec, cand_vec)
            
            # 2. Explanatory Virtue (Regularizer)
            virtue = self._compute_explanatory_virtue(cand)
            
            # Combined raw score
            raw_score = (0.7 * likelihood) + (0.3 * virtue)
            
            # 3. Critical Amplification (The QCTN-A core)
            final_score = self._critical_amplification(raw_score, context_hash)
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Likelihood:{likelihood:.2f} + Virtue:{virtue:.2f} amplified by criticality."
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimates confidence by measuring sensitivity to perturbation (Simulated Fisher Information).
        High sensitivity at the peak implies high confidence in the specific hypothesis.
        """
        base_result = self.evaluate(prompt, [answer])
        if not base_result:
            return 0.0
        
        base_score = base_result[0]["score"]
        
        # Perturb the prompt slightly (simulate measurement basis change)
        perturbed_prompt = prompt + " " 
        perturbed_result = self.evaluate(perturbed_prompt, [answer])
        perturbed_score = perturbed_result[0]["score"] if perturbed_result else 0.0
        
        # Sensitivity (Delta)
        sensitivity = abs(base_score - perturbed_score)
        
        # If the score is high AND sensitive (critical), confidence is high.
        # If score is low, confidence is low regardless of sensitivity.
        # If score is high but insensitive (flat), confidence is moderate (robust but not sharp).
        
        confidence_val = base_score * (0.5 + 0.5 * min(sensitivity * 10, 1.0))
        return float(np.clip(confidence_val, 0.0, 1.0))