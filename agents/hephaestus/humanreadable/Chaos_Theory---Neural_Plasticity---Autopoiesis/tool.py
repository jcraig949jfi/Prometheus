import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Autopoietically Closed Chaotic Reservoir (ACCR) Approximation.
    
    Mechanism:
    1. Chaos (Exploration): Uses a deterministic pseudo-chaotic map (Logistic map 
       with r=3.99) seeded by input hash to generate diverse trajectory weights.
       This simulates the "rich exploratory search" of chaotic transients.
    2. Plasticity (Learning): Implements a simplified Hebbian-like update where 
       candidate features that align with structural constraints (negations, numerics)
       reinforce their score, while misaligned features are pruned (penalized).
    3. Autopoiesis (Closure): Monitors the "organizational viability" (score variance).
       If the system detects high uncertainty (low coherence), it triggers a 
       re-evaluation phase (simulated by tightening constraints) to maintain 
       internal consistency before outputting a score.
       
    This approximates the theoretical ACCR using only numpy/stdlib, focusing on
    structural parsing and numeric evaluation as primary drivers for high accuracy.
    """

    def __init__(self):
        self.r = 3.99  # Chaos parameter (Logistic map)
        self.dt = 0.01 # Time step for dynamics simulation

    def _hash_to_seed(self, s: str) -> int:
        return zlib.crc32(s.encode()) & 0xffffffff

    def _chaotic_trajectory(self, seed: int, steps: int) -> np.ndarray:
        """Generate a deterministic chaotic sequence for exploration weighting."""
        x = (seed % 1000) / 1000.0 + 0.1 # Normalize to (0.1, 1.1) to avoid fixed points
        if x >= 1.0: x = 0.5
        trajectory = []
        for _ in range(steps):
            x = self.r * x * (1.0 - x)
            trajectory.append(x)
        return np.array(trajectory)

    def _extract_features(self, text: str) -> Dict:
        """Structural parsing: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(no|not|never|none|neither)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|larger|better|worse|<|>)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text)
        }
        return features

    def _numeric_reasoning(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Handle numeric constraint propagation."""
        if not prompt_nums or not cand_nums:
            return 0.0
        
        try:
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
            
            # Simple transitivity/comparison check
            if len(p_vals) >= 2 and len(c_vals) >= 1:
                # If prompt implies order (e.g., 2 < 5), check candidate consistency
                # Heuristic: Candidate numbers should be within the magnitude range 
                # or logically follow if it's a calculation task (simplified here)
                p_diff = abs(p_vals[-1] - p_vals[0]) if len(p_vals) > 1 else 1.0
                c_diff = abs(c_vals[-1] - c_vals[0]) if len(c_vals) > 1 else 0.0
                
                # Reward logical consistency in magnitude changes
                if p_diff == 0: return 1.0 if c_diff == 0 else 0.5
                return 1.0 - min(1.0, abs(c_diff - p_diff) / (p_diff + 1e-6))
        except ValueError:
            pass
        return 0.5

    def _compute_hebbian_score(self, prompt: str, candidate: str) -> float:
        """
        Simulate Hebbian plasticity: Strengthen connections between 
        prompt constraints and candidate features.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        
        # Constraint Propagation: Negation matching
        if p_feat['has_negation'] == c_feat['has_negation']:
            score += 0.3
        else:
            score -= 0.3 # Prune mismatched negation
            
        # Constraint Propagation: Comparative logic
        if p_feat['has_comparative'] and c_feat['has_comparative']:
            score += 0.2
        elif p_feat['has_comparative'] and not c_feat['has_comparative']:
            score -= 0.2 # Failure to address comparative
            
        # Numeric evaluation
        if p_feat['numbers']:
            num_score = self._numeric_reasoning(p_feat['numbers'], c_feat['numbers'])
            score += num_score * 0.4
            
        return score

    def _autopoietic_closure(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Autopoietic feedback: Adjust score based on organizational viability.
        If the base reasoning is weak, apply a 'coherence penalty' unless 
        the candidate structurally mirrors the prompt (NCD tiebreaker).
        """
        # Calculate NCD for coherence check
        s_combined = prompt + candidate
        len_combined = len(zlib.compress(s_combined.encode()))
        len_total = len(zlib.compress(prompt.encode())) + len(zlib.compress(candidate.encode()))
        ncd = len_combined / max(len_total, 1)
        
        # Viability threshold
        viability_threshold = 0.4
        
        if base_score < viability_threshold:
            # System is unstable; rely on structural overlap (NCD) as a fallback
            # Low NCD means high similarity (good for simple echo tasks, bad for reasoning)
            # We use NCD inversely here: if base score is low, we demand high structural alignment
            # But pure NCD is weak, so we only use it to nudge, not decide.
            adjustment = (1.0 - ncd) * 0.1 
            return max(0.0, min(1.0, base_score + adjustment))
        
        # Stable state: reinforce high scores
        return max(0.0, min(1.0, base_score * 1.1))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        # Generate chaotic weights for diversity in tie-breaking
        chaos_seq = self._chaotic_trajectory(self._hash_to_seed(prompt), len(candidates))
        
        for i, cand in enumerate(candidates):
            # 1. Chaotic Exploration: Perturb initial assessment slightly
            chaos_factor = (chaos_seq[i] - 0.5) * 0.05 
            
            # 2. Hebbian Plasticity: Core reasoning score
            raw_score = self._compute_hebbian_score(prompt, cand)
            
            # 3. Autopoietic Closure: Viability check and adjustment
            final_score = self._autopoietic_closure(raw_score, prompt, cand)
            
            # Apply chaotic perturbation (simulating transient search)
            adjusted_score = final_score + chaos_factor
            adjusted_score = max(0.0, min(1.0, adjusted_score))
            
            results.append({
                "candidate": cand,
                "score": float(adjusted_score),
                "reasoning": f"Hebbian:{raw_score:.2f} Auto:{final_score:.2f} Chaos:{chaos_factor:.3f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Evaluate single candidate against itself to get intrinsic score
        # We simulate a comparison against a null hypothesis or just use the internal scoring
        # Since we don't have other candidates, we run the scoring pipeline directly
        
        raw_score = self._compute_hebbian_score(prompt, answer)
        final_score = self._autopoietic_closure(raw_score, prompt, answer)
        
        # Deterministic chaos perturbation based on prompt+answer hash
        seed = self._hash_to_seed(prompt + answer)
        chaos_val = self._chaotic_trajectory(seed, 1)[0]
        perturbation = (chaos_val - 0.5) * 0.02
        
        confidence = max(0.0, min(1.0, final_score + perturbation))
        return float(confidence)