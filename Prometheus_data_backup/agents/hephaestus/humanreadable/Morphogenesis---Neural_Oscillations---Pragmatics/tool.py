import numpy as np
import math

class ReasoningTool:
    """
    Predictive Reactive-Diffusive Oscillator Network (PRDON) Approximation.
    
    Mechanism:
    1. Morphogenesis (Reaction-Diffusion): Candidates are mapped to a 1D lattice.
       A simplified FitzHugh-Nagumo step simulates activation/inhibition dynamics
       to generate spatial patterns representing hypothesis stability.
    2. Neural Oscillations: 
       - Theta (Global): Modulates the excitability threshold based on prompt complexity.
       - Gamma (Local): Binds high-activation regions; acts as a coherence score.
    3. Pragmatics (Gricean Constraints): 
       Penalty functions adjust scores based on Length (Quantity), Certainty keywords (Quality),
       and Structure (Manner). Relevance is approximated by keyword overlap.
    
    The final score is the equilibrium activation minus pragmatic penalties, normalized.
    """

    def __init__(self):
        self.lattice_size = 50
        self.diffusion_rate = 0.1
        self.reaction_rate = 0.05
        # Deterministic seed for internal noise if needed, though we avoid random noise here
        np.random.seed(42)

    def _compute_pragmatic_penalties(self, text: str, prompt: str) -> float:
        """Calculates a penalty (0.0 to 1.0) based on Grice's Maxims."""
        text_lower = text.lower()
        prompt_lower = prompt.lower()
        words = text_lower.split()
        p_words = set(prompt_lower.split())
        t_words = set(words)
        
        # Relevance: Overlap ratio
        overlap = len(t_words.intersection(p_words))
        relevance_penalty = 0.0
        if len(t_words) > 0:
            # Low overlap increases penalty
            overlap_ratio = overlap / len(t_words) if len(t_words) > 0 else 0
            relevance_penalty = max(0, 1.0 - (overlap_ratio * 2)) # Harsh if no overlap
            
        # Quantity: Too short or too long relative to prompt
        len_ratio = len(words) / (len(p_words) + 1)
        quantity_penalty = 0.0
        if len_ratio < 0.5: quantity_penalty = 0.3 # Too brief
        elif len_ratio > 5.0: quantity_penalty = 0.2 # Too verbose
        
        # Quality: Heuristic for hedging vs certainty
        certainty_words = {'is', 'are', 'was', 'were', 'definitely', 'clearly'}
        hedge_words = {'maybe', 'perhaps', 'might', 'could', 'uncertain'}
        cert_count = sum(1 for w in words if w in certainty_words)
        hedge_count = sum(1 for w in words if w in hedge_words)
        
        quality_penalty = 0.0
        if hedge_count > cert_count:
            quality_penalty = 0.1 * (hedge_count - cert_count)
            
        # Manner: Simple structure check (punctuation presence)
        manner_penalty = 0.0
        if '.' not in text and len(text) > 20:
            manner_penalty = 0.1
            
        total_penalty = min(1.0, relevance_penalty + quantity_penalty + quality_penalty + manner_penalty)
        return total_penalty

    def _simulate_morphogenesis(self, seed_strength: float) -> float:
        """
        Simulates a 1D Reaction-Diffusion step (FitzHugh-Nagumo simplified).
        Returns the average activation of the stable pattern.
        """
        # Initialize lattice with seed strength + small gradient
        u = np.ones(self.lattice_size) * seed_strength
        v = np.zeros(self.lattice_size) # Recovery variable
        
        # Discretized Laplacian (1D)
        laplacian = np.array([1, -2, 1]) 
        
        # Iterate for stability (Morphogenesis time-steps)
        for _ in range(10):
            # Diffusion term
            diff_u = self.diffusion_rate * np.convolve(u, laplacian, mode='same')
            
            # Reaction term (Simplified F-N)
            # du/dt = D*u_xx + u*(u-a)*(1-u) - v
            reaction = u * (u - 0.2) * (1 - u) - v
            
            u_new = u + 0.1 * (diff_u + reaction)
            
            # dv/dt = epsilon*(u - gamma*v)
            v_new = v + 0.01 * (u - 0.5 * v)
            
            # Clamp values
            u = np.clip(u_new, 0, 1)
            v = np.clip(v_new, 0, 1)
            
        # Gamma binding: High frequency sync implies high mean activation in stable state
        return float(np.mean(u))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        # Theta modulation: Global excitability based on prompt length (complexity proxy)
        theta_mod = 1.0 / (1.0 + math.log(len(prompt.split()) + 1))
        
        for cand in candidates:
            # 1. Seed generation based on semantic similarity proxy (hash/length combo)
            # Using length and char-sum as a deterministic pseudo-embedding proxy
            seed_val = (len(cand) * 0.1 + sum(ord(c) for c in cand) % 100) / 100.0
            seed_val = max(0.1, min(0.9, seed_val)) # Normalize seed
            
            # 2. Morphogenesis & Oscillation
            raw_activation = self._simulate_morphogenesis(seed_val * theta_mod)
            
            # 3. Pragmatic Filtering
            penalty = self._compute_pragmatic_penalties(cand, prompt)
            
            # Final Score: Activation * (1 - Penalty)
            final_score = raw_activation * (1.0 - penalty)
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Morphogenetic stability: {raw_activation:.2f}; Pragmatic penalty: {penalty:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]["score"]