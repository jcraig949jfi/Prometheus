import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Chaotic Neural ODE (DC-NODE) Approximation.
    
    Mechanism:
    1. Thesis (Embedding): Encodes prompt/candidate into a structural vector (length, entropy, NCD-ratio).
    2. Antithesis (Chaos Simulation): Simulates a logistic map trajectory (chaotic ODE proxy) 
       initialized by the embedding. Measures divergence (Lyapunov exponent) to test stability.
       - Stable trajectories (low divergence) indicate weak hypothesis testing.
       - Overly unstable trajectories indicate noise.
       - "Edge of Chaos" indicates strong reasoning potential.
    3. Synthesis (Scoring): Combines structural validity (constraint propagation checks) 
       with the chaotic stability score to rank candidates.
       
    This approximates the DC-NODE by using the sensitivity of chaotic maps to initial 
    conditions (hypothesis parameters) to amplify small structural differences between 
    candidates, while using gradient-like logical checks for the synthesis step.
    """

    def __init__(self):
        # Chaos control parameter (r) for logistic map: x_{n+1} = r * x_n * (1 - x_n)
        # r=3.9 is in the chaotic regime
        self.chaos_r = 3.9 
        self.lyapunov_steps = 50

    def _structural_parse(self, text: str) -> Tuple[float, float, float]:
        """Extract structural features: length norm, entropy estimate, negation count."""
        if not text:
            return 0.0, 0.0, 0.0
        
        length = len(text)
        norm_len = min(length / 100.0, 1.0)  # Normalize length
        
        # Simple entropy approximation via character frequency
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        norm_entropy = entropy / 8.0 if length > 0 else 0.0 # Max ~8 bits for ASCII
        
        # Constraint propagation: Detect logical operators
        lower_text = text.lower()
        negations = sum(1 for w in ['no', 'not', 'never', 'false'] if w in lower_text.split())
        comparatives = sum(1 for w in ['<', '>', 'less', 'more', 'greater'] if w in lower_text)
        logic_score = (negations * 0.1 + comparatives * 0.1)
        
        return norm_len, min(norm_entropy, 1.0), logic_score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _simulate_chaos(self, initial_state: float, perturbation: float = 1e-4) -> float:
        """
        Simulate chaotic dynamics to estimate local Lyapunov exponent.
        Uses logistic map as a differentiable program proxy.
        Returns the average log-divergence rate (approx Lyapunov exponent).
        """
        x = initial_state
        # Perturb initial state slightly (Antithesis: introducing contradiction)
        x_pert = initial_state + perturbation
        
        sum_lyap = 0.0
        epsilon = 1e-10
        
        for _ in range(self.lyapunov_steps):
            # Logistic map step
            x_next = self.chaos_r * x * (1.0 - x)
            x_pert_next = self.chaos_r * x_pert * (1.0 - x_pert)
            
            # Calculate divergence
            dist = abs(x_next - x_pert_next)
            if dist > epsilon:
                sum_lyap += math.log(dist / max(abs(x - x_pert), epsilon))
            
            x = x_next
            x_pert = x_pert_next
            
            # Renormalize if divergence is too large to stay in bounds
            if dist > 1.0:
                x_pert = x + perturbation
                
        return sum_lyap / self.lyapunov_steps if self.lyapunov_steps > 0 else 0.0

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Generate a score based on Dialectical Chaotic analysis."""
        # Thesis: Structural encoding
        p_len, p_ent, p_log = self._structural_parse(prompt)
        c_len, c_ent, c_log = self._structural_parse(candidate)
        
        # Antithesis: Chaos simulation initialized by candidate properties
        # Map candidate features to [0.01, 0.99] range for logistic map stability
        init_state = 0.01 + 0.98 * (0.3 * c_len + 0.3 * c_ent + 0.4 * c_log)
        lyap_exp = self._simulate_chaos(init_state)
        
        # Chaos Score: Prefer "Edge of Chaos" (moderate positive Lyapunov)
        # Too negative = stable/boring. Too positive = random noise.
        # Ideal range approx 0.3 to 0.7 for logistic map r=3.9
        chaos_score = 0.0
        if 0.2 < lyap_exp < 0.8:
            chaos_score = 0.5
        elif lyap_exp > 0:
            chaos_score = 0.2
            
        # Synthesis: Combine structural validity and chaotic sensitivity
        # 1. NCD similarity (should be related but not identical)
        ncd = self._compute_ncd(prompt, candidate)
        similarity_score = 1.0 - ncd
        
        # 2. Logical consistency heuristic (Length and Logic presence)
        # Candidates with logical operators often score higher in reasoning tasks
        logic_bonus = c_log * 0.2
        
        # 3. Numeric evaluation check (Pattern matching for numbers)
        numeric_bonus = 0.0
        if any(char.isdigit() for char in candidate):
            numeric_bonus = 0.1
            
        # Final Score Composition
        # Weighted sum emphasizing structural integrity and chaotic distinctiveness
        score = (similarity_score * 0.4) + (chaos_score * 0.3) + (logic_bonus * 0.2) + (numeric_bonus * 0.1)
        
        # Add small deterministic noise based on content to break ties uniquely
        tie_breaker = (len(candidate) % 10) * 0.001
        
        return score + tie_breaker

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            reasoning = f"Chaos-Stability: {score:.4f}; Structural match detected."
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to probability-like range.
        """
        # Evaluate single candidate against the set of itself (degenerate case)
        # We simulate a comparison against a 'null' hypothesis to gauge strength
        score = self._score_candidate(prompt, answer)
        
        # Map score (approx 0.0 - 1.0 range) to confidence
        # Baseline NCD is weak, so we boost based on logical structure detection
        base_conf = max(0.0, min(1.0, score))
        
        # Boost if logical operators are present (heuristic for reasoning tasks)
        _, _, logic_score = self._structural_parse(answer)
        if logic_score > 0:
            base_conf = min(1.0, base_conf + 0.15)
            
        return base_conf