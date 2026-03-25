import math
import hashlib

class ReasoningTool:
    """
    Implements a conceptual fusion of Morphogenesis, Predictive Coding, and Falsificationism.
    
    Mechanism:
    1. Morphogenesis (Hypothesis Field): Candidates are mapped to a 1D latent field. Their 
       initial 'activation' is determined by a hash-based seed, simulating spontaneous 
       pattern emergence (Turing patterns) without external bias.
    2. Predictive Coding (Error Dynamics): The system computes a 'prediction error' based 
       on the semantic alignment between the prompt and candidate (approximated via 
       lexical overlap and length heuristics for dependency-free operation).
    3. Falsificationism (Refutation): An error-amplification loop runs locally. Candidates 
       with high prediction error have their 'reactivity' increased, destabilizing their 
       activation score. Low-error candidates stabilize and grow.
       
    The final score represents the steady-state activation of the hypothesis after 
    error-driven pruning.
    """

    def __init__(self):
        self._state = {}

    def _hash_to_float(self, s: str) -> float:
        """Deterministic mapping of string to [0.4, 0.6] range (initial bias)."""
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        val = int(h[:8], 16) / 0xFFFFFFFF
        return 0.4 + 0.2 * val

    def _compute_prediction_error(self, prompt: str, candidate: str) -> float:
        """
        Approximates prediction error (surprise).
        Low error = high overlap/relevance. High error = low overlap.
        Uses simple token overlap and length ratio as a proxy for semantic fit.
        """
        p_tokens = set(prompt.lower().split())
        c_tokens = set(candidate.lower().split())
        
        # Intersection over Union (IoU) proxy
        intersection = len(p_tokens & c_tokens)
        union = len(p_tokens | c_tokens) if len(p_tokens | c_tokens) > 0 else 1
        overlap_score = intersection / union
        
        # Length heuristic (penalize extreme mismatches)
        len_ratio = min(len(candidate), len(prompt)) / (max(len(candidate), len(prompt)) + 1e-6)
        len_score = 1.0 - abs(0.5 - len_ratio) * 2 # Peaks at 0.5 ratio, simplified
        
        # Combined relevance (0 to 1, where 1 is perfect match)
        relevance = 0.7 * overlap_score + 0.3 * len_score
        
        # Prediction error is inverse of relevance
        return 1.0 - relevance

    def _morphogenetic_step(self, activation: float, error: float, dt: float = 0.1) -> float:
        """
        Simulates one step of Reaction-Diffusion dynamics.
        Reaction term: Driven by error. 
        Falsification: High error amplifies decay (destabilization).
        Diffusion: Implicitly handled by the competitive ranking later.
        """
        # Reaction term: Growth if error is low, Decay if error is high
        # Threshold for falsification: if error > 0.5, amplify decay
        if error > 0.5:
            # Falsification regime: Exponential decay amplified by error magnitude
            decay_rate = 2.0 * error 
            new_activation = activation * math.exp(-decay_rate * dt)
        else:
            # Confirmation regime: Slow growth towards stability
            growth_rate = 1.0 - error
            new_activation = activation + (growth_rate * (1.0 - activation) * dt)
            
        return max(0.0, min(1.0, new_activation))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        
        # Pre-calculate prompt hash for field consistency
        prompt_seed = self._hash_to_float(prompt)
        
        for cand in candidates:
            # 1. Morphogenesis: Initial activation from latent field (hash)
            # Combine candidate hash and prompt context for initial state
            initial_activation = (self._hash_to_float(cand) + prompt_seed) / 2.0
            
            # 2. Predictive Coding: Compute prediction error
            error = self._compute_prediction_error(prompt, cand)
            
            # 3. Falsification & Dynamics: Run simulation to steady state approximation
            # Instead of full PDE solve, we iterate the reaction term until convergence
            # This mimics the local update rule described in the theory
            activation = initial_activation
            steps = 10 # Discrete time steps for convergence
            for _ in range(steps):
                activation = self._morphogenetic_step(activation, error, dt=0.2)
                
            results.append({
                "candidate": cand,
                "score": round(activation, 6),
                "reasoning": f"Error: {error:.4f}, Final Activation: {activation:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluate logic."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]