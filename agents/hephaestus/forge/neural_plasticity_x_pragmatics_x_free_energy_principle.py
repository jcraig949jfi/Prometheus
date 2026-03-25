import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a simplified Neuro-Pragmatic Free Energy architecture.
    
    Mechanism:
    1. Predictive Coding (Free Energy): Uses NCD (Normalized Compression Distance) 
       as a proxy for prediction error between the prompt context and candidate answer.
       Lower error = higher likelihood.
    2. Neural Plasticity (Hebbian-STDP): Dynamically adjusts weights of semantic 
       features (negations, comparatives, numbers) based on their co-occurrence 
       with successful constraint matching. Features that reduce 'surprise' (error) 
       are strengthened.
    3. Pragmatics (RSA): Applies a 'Gricean Utility' filter. Candidates that are 
       tautological (repeat prompt exactly) or irrelevant (high entropy/no semantic 
       overlap) are penalized, simulating conversational implicature.
       
    The system iteratively scores candidates by minimizing free energy (prediction error)
    while maximizing pragmatic utility, effectively performing hypothesis testing.
    """

    def __init__(self):
        # Hebbian weights for structural features (initialized to 1.0)
        # Order: [has_negation, has_comparative, has_number, has_conditional]
        self.synaptic_weights = np.array([1.0, 1.0, 1.0, 1.0])
        self.learning_rate = 0.1
        self.epsilon = 1e-6

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features for plasticity weighting."""
        t = text.lower()
        f1 = 1.0 if any(n in t for n in ['no', 'not', 'never', 'none', 'false']) else 0.0
        f2 = 1.0 if any(c in t for c in ['>', '<', 'more', 'less', 'greater', 'smaller', 'better', 'worse']) else 0.0
        f3 = 1.0 if re.search(r'\d+', t) else 0.0
        f4 = 1.0 if any(w in t for w in ['if', 'then', 'unless', 'implies']) else 0.0
        return np.array([f1, f2, f3, f4])

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as proxy for prediction error."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _pragmatic_utility(self, prompt: str, candidate: str) -> float:
        """
        RSA-style utility: Penalizes tautologies (low information) 
        and irrelevant high-entropy noise.
        """
        p_set = set(prompt.lower().split())
        c_set = set(candidate.lower().split())
        
        # Overlap ratio (Relevance)
        if len(p_set) == 0: return 0.0
        overlap = len(p_set & c_set) / len(p_set | c_set) if len(p_set | c_set) > 0 else 0
        
        # Penalty for exact repetition (Tautology - violates Maxim of Quantity)
        if candidate.strip() == prompt.strip():
            return 0.1
            
        # Penalty for zero overlap (Irrelevance)
        if overlap == 0 and len(c_set) > 0:
            # Check if it's a simple yes/no which might naturally have low overlap
            if not any(x in candidate.lower() for x in ['yes', 'no', 'true', 'false', '0', '1']):
                return 0.2
                
        return 0.5 + (overlap * 0.5)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Free Energy: Prediction Error weighted by Plasticity.
        F = Sum(w_i * error_i) - Utility
        """
        # 1. Prediction Error (NCD)
        # We invert NCD because high similarity = low error. 
        # But for Free Energy, we want a cost function (higher is worse).
        prediction_error = self._ncd(prompt, candidate)
        
        # 2. Feature-based Error Modulation
        # If the prompt has specific features, the error is modulated by synaptic weights
        p_features = self._extract_features(prompt)
        c_features = self._extract_features(candidate)
        
        # Feature mismatch penalty (weighted by plasticity)
        feature_mismatch = np.sum(self.synaptic_weights * np.abs(p_features - c_features))
        
        # Total Energy (Error + Mismatch)
        total_error = prediction_error + (0.2 * feature_mismatch)
        
        # 3. Pragmatic Prior (Utility)
        utility = self._pragmatic_utility(prompt, candidate)
        
        # Free Energy = Error - Utility (Minimizing F means minimizing error, maximizing utility)
        free_energy = total_error - utility
        
        return free_energy

    def _update_plasticity(self, prompt: str, best_candidate: str):
        """Hebbian update: Strengthen weights that contributed to low error."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(best_candidate)
        
        # If features matched and reduced error, strengthen (simplified STDP)
        # Correlation between prompt and candidate features
        correlation = p_feat * c_feat
        self.synaptic_weights += self.learning_rate * correlation
        # Normalize weights to prevent explosion
        self.synaptic_weights = np.clip(self.synaptic_weights, 0.1, 2.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        scores = []
        best_energy = float('inf')
        best_candidate = ""

        # Phase 1: Evaluate all candidates
        for cand in candidates:
            energy = self._compute_free_energy(prompt, cand)
            # Convert energy to score (lower energy = higher score)
            # Shift to positive domain for readability
            score = 1.0 / (1.0 + energy + self.epsilon)
            scores.append({
                "candidate": cand,
                "score": score,
                "energy": energy, # Internal metric
                "reasoning": f"Free Energy: {energy:.4f}, Pragmatic Utility applied."
            })
            if energy < best_energy:
                best_energy = energy
                best_candidate = cand

        # Phase 2: Plasticity Update (Learning from the best hypothesis)
        if best_candidate:
            self._update_plasticity(prompt, best_candidate)

        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Clean up internal keys for output
        return [{
            "candidate": s["candidate"], 
            "score": s["score"], 
            "reasoning": s["reasoning"]
        } for s in scores]

    def confidence(self, prompt: str, answer: str) -> float:
        # Re-use evaluate logic for a single pair
        # We simulate a binary choice context to derive confidence
        # by comparing the answer against a 'null' hypothesis or just using the raw score
        
        # Calculate energy for the specific pair
        energy = self._compute_free_energy(prompt, answer)
        base_score = 1.0 / (1.0 + energy + self.epsilon)
        
        # Heuristic adjustment: If the answer is extremely short and prompt is long, 
        # unless it's a specific token, confidence drops (Pragmatic check)
        if len(answer) < 3 and len(prompt) > 20:
             if not any(x in answer.lower() for x in ['yes', 'no', 'true', 'false', '0', '1', '-']):
                 base_score *= 0.8
                 
        return float(np.clip(base_score, 0.0, 1.0))