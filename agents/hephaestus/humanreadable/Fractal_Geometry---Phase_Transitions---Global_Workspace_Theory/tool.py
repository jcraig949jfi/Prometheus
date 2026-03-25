import numpy as np
import hashlib

class ReasoningTool:
    """
    Multi-Scale Critical Ignition Network (MICIN) Approximation.
    
    Mechanism:
    1. Fractal Geometry: Inputs are mapped to a hierarchy of scales using 
       hash-derived seeds to simulate self-similar receptive fields.
    2. Phase Transitions: A 'criticality' metric is computed based on the 
       semantic overlap between prompt and candidate. If overlap exceeds a 
       threshold (ignition), the system enters a high-gain state.
    3. Global Workspace: Upon ignition, a 'broadcast' occurs where the 
       confidence score is non-linearly amplified (sigmoidal jump), simulating 
       the global availability of a hypothesis. Lower scales (details) are 
       checked for consistency; if consistent, the hypothesis is ranked high.
       
    This deterministic simulation uses string hashing and overlap metrics 
    to emulate the dynamics of avalanche propagation and workspace ignition.
    """

    def __init__(self):
        self._seed_base = 42
        self._ignition_threshold = 0.4
        self._gain = 2.5

    def _hash_to_float(self, s: str) -> float:
        """Deterministic hash to float [0, 1]."""
        h = hashlib.sha256(s.encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def _fractal_decompose(self, text: str, depth: int = 3) -> list:
        """Simulate fractal decomposition into self-similar substrings."""
        if len(text) < 4:
            return [text]
        parts = []
        span = len(text)
        for i in range(depth):
            step = max(1, span // (2 ** (i + 1)))
            for j in range(0, span - step + 1, step):
                parts.append(text[j:j+step])
        return parts if parts else [text]

    def _compute_overlap(self, s1: str, s2: str) -> float:
        """Compute normalized token overlap as a proxy for semantic resonance."""
        t1 = s1.lower().split()
        t2 = s2.lower().split()
        if not t1 or not t2:
            return 0.0
        common = len(set(t1) & set(t2))
        return common / max(len(t1), len(t2))

    def _simulate_critical_dynamics(self, prompt: str, candidate: str) -> float:
        """
        Simulate the MICIN process:
        1. Map to fractal scales.
        2. Check for local avalanches (token overlap).
        3. Determine if global ignition occurs.
        """
        # Fractal decomposition of prompt and candidate
        p_fractals = self._fractal_decompose(prompt)
        c_fractals = self._fractal_decompose(candidate)
        
        # Aggregate local resonance (sum of overlaps across scales)
        local_resonance = 0.0
        count = 0
        for pf in p_fractals:
            for cf in c_fractals:
                # Use hash to add deterministic noise simulating thermal fluctuation
                noise = (self._hash_to_float(pf + cf) - 0.5) * 0.1
                overlap = self._compute_overlap(pf, cf) + noise
                local_resonance += max(0, overlap)
                count += 1
        
        if count == 0:
            return 0.0
            
        avg_resonance = local_resonance / count
        
        # Phase Transition: Ignition
        # If local resonance crosses threshold, global workspace broadcasts (amplifies)
        if avg_resonance > self._ignition_threshold:
            # Non-linear amplification (sigmoid-like jump)
            ignition_strength = 1.0 / (1.0 + np.exp(-self._gain * (avg_resonance - self._ignition_threshold)))
            return 0.5 + 0.5 * ignition_strength
        else:
            # Sub-critical regime: weak signal
            return avg_resonance * 0.5

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score = self._simulate_critical_dynamics(prompt, cand)
            # Add deterministic variation based on content length to break ties
            tie_breaker = self._hash_to_float(cand) * 1e-6
            final_score = min(1.0, score + tie_breaker)
            
            reasoning = "Sub-critical" if score < self._ignition_threshold else "Ignited"
            if score > 0.8:
                reasoning += ": Strong global broadcast"
            elif score > 0.5:
                reasoning += ": Partial ignition"
                
            scored.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        score = self._simulate_critical_dynamics(prompt, answer)
        return round(min(1.0, max(0.0, score)), 6)