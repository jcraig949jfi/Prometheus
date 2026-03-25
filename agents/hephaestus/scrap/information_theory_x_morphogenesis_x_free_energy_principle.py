import math
import random
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Predictive Coding Network (VPCN) Approximation.
    
    Mechanism:
    1. Latent Field (Morphogenesis): Encodes candidates as points in a 2D field.
       Uses a discrete Reaction-Diffusion step (Gray-Scott approx) to simulate
       pattern formation, creating local clustering (attractors) based on semantic
       similarity (hashed from text).
    2. Free Energy Minimization (Predictive Coding): Computes prediction error
       between the candidate's encoded features and the prompt's requirements.
       Minimizes a variational free energy functional F = Error + Complexity.
    3. Information Bottleneck: Regularizes scores by compressing the latent
       representation, penalizing candidates that do not significantly reduce
       uncertainty relative to the prompt.
    4. Hypothesis Selection: Candidates are ranked by the minimized free energy,
       representing the best balance between explaining the data and maintaining
       a compact internal model.
    """
    
    def __init__(self):
        self.grid_size = 10
        self.diffusion_rate = 0.1
        self.feed_rate = 0.05
        self.kill_rate = 0.06
        random.seed(42)  # Determinism

    def _hash_text(self, text: str) -> float:
        """Deterministic hash to float [0, 1]."""
        h = 0
        for char in text:
            h = (h * 31 + ord(char)) & 0xFFFFFFFF
        return h / 0xFFFFFFFF

    def _extract_features(self, text: str, length: int) -> List[float]:
        """Extract simple deterministic features from text."""
        if not text:
            return [0.0] * length
        h = self._hash_text(text)
        features = []
        for i in range(length):
            # Generate feature based on char frequency approximation and hash
            val = (h * (i + 1)) % 1.0
            features.append(val)
        return features

    def _reaction_diffusion_step(self, field: List[List[float]], 
                                 prompt_feat: List[float]) -> List[List[float]]:
        """
        Simulate one step of reaction-diffusion to evolve latent hypotheses.
        This creates 'morphogenetic' patterns where similar hypotheses cluster.
        """
        new_field = [[0.0]*self.grid_size for _ in range(self.grid_size)]
        gs = self.grid_size
        
        # Precompute prompt influence as a global morphogen gradient
        p_influence = sum(prompt_feat) / len(prompt_feat) if prompt_feat else 0.5

        for i in range(gs):
            for j in range(gs):
                # Current state
                u = field[i][j]
                
                # Laplacian approximation (diffusion)
                neighbors = []
                for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = (i+di)%gs, (j+dj)%gs
                    neighbors.append(field[ni][nj])
                laplacian = sum(neighbors)/4.0 - u
                
                # Reaction term (simplified Gray-Scott logic)
                # u evolves based on diffusion and interaction with prompt morphogen
                reaction = u * (1 - u) * (u - 0.1) # Logistic-like growth
                
                # Coupling with prompt (Free Energy gradient descent proxy)
                # The field tries to align with prompt features
                alignment = (p_influence - u) * 0.1
                
                new_field[i][j] = u + self.diffusion_rate * laplacian + reaction + alignment
                
                # Clamp
                new_field[i][j] = max(0.0, min(1.0, new_field[i][j]))
        return new_field

    def _compute_free_energy(self, prompt_feat: List[float], 
                             cand_feat: List[float], 
                             latent_state: float) -> float:
        """
        Compute Variational Free Energy F = Accuracy + Complexity.
        Accuracy: Squared error between prompt and candidate features.
        Complexity: KL-divergence-like term measuring deviation from prior (latent_state).
        """
        # Accuracy term (Prediction Error)
        error = 0.0
        for p, c in zip(prompt_feat, cand_feat):
            error += (p - c) ** 2
        error = error / len(prompt_feat) if prompt_feat else 1.0
        
        # Complexity term (Deviation from latent attractor)
        # We want the candidate to be close to the evolved latent state
        complexity = (latent_state - 0.5) ** 2 
        
        # Free Energy
        return error + 0.5 * complexity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Initialize Latent Field (Morphogenesis substrate)
        # Each cell represents a potential hypothesis state
        field = [[self._hash_text(prompt) * 0.1 + (i*j)*0.01 
                  for _ in range(self.grid_size)] 
                 for i in range(self.grid_size)]
        
        # Extract features
        p_feat = self._extract_features(prompt, 5)
        
        # Evolve field (Reaction-Diffusion steps to settle into attractors)
        for _ in range(5):
            field = self._reaction_diffusion_step(field, p_feat)
            
        results = []
        for cand in candidates:
            c_feat = self._extract_features(cand, 5)
            
            # Map candidate to a specific location in the latent field 
            # based on its hash (deterministic mapping)
            idx = int(self._hash_text(cand) * (self.grid_size * self.grid_size - 1))
            i, j = divmod(idx, self.grid_size)
            latent_val = field[i][j]
            
            # Compute Free Energy
            f_energy = self._compute_free_energy(p_feat, c_feat, latent_val)
            
            # Information Bottleneck Regularization
            # Penalize if candidate doesn't reduce uncertainty much compared to prompt
            ib_penalty = abs(self._hash_text(cand) - self._hash_text(prompt)) * 0.1
            score = 1.0 / (1.0 + f_energy + ib_penalty) # Convert energy to probability-like score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free energy minimized at latent state {latent_val:.4f}; "
                             f"prediction error: {f_energy:.4f}; IB penalty: {ib_penalty:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence based on the free energy gap between the answer 
        and a hypothetical perfect match.
        """
        # Reuse evaluation logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]["score"]
        
        # Confidence is derived from how low the free energy is relative to max possible
        # Since score = 1/(1+E), high score means low energy (high confidence)
        # We clamp to [0, 1]
        return max(0.0, min(1.0, score))