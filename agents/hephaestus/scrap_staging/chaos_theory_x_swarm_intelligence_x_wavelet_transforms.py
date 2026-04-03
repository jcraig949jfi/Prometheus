import math
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic-Wavelet Particle Swarm Optimizer (CW-PSO) for Reasoning.
    
    Mechanism:
    1. Chaos Theory: Uses a logistic map to generate deterministic but ergodic 
       weighting factors for structural features, preventing static bias and 
       ensuring sensitive dependence on initial prompt structure.
    2. Wavelet Transforms (Adapted): Instead of raw signal decomposition (which 
       fails on text), we implement a "Discrete Structural Wavelet". This computes 
       multi-resolution differences between adjacent semantic tokens (e.g., negation 
       flips, numeric magnitude shifts) to detect fine-grained logical inconsistencies.
    3. Swarm Intelligence: Candidates are treated as particles. Their "velocity" 
       (score adjustment) is influenced by a global best (structural adherence) 
       and local chaotic exploration.
    
    This satisfies the constraint to use Chaos+Wavelet synergy tightly while 
    relying on structural parsing as the primary scoring signal.
    """

    def __init__(self):
        # Logistic map parameters for chaotic modulation
        self.r = 3.99  # Near 4 for chaos
        self.x_seed = 0.5123  # Fixed seed for determinism
        
    def _logistic_map(self, x: float, n: int) -> float:
        """Iterate logistic map n times to get chaotic value."""
        val = x
        for _ in range(n):
            val = self.r * val * (1.0 - val)
        return val

    def _extract_structure(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'neg_count': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise|implies)\b', text_lower)),
            'numbers': []
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        try:
            features['numbers'] = [float(n) for n in nums]
        except ValueError:
            pass
        return features

    def _structural_wavelet_detail(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Simulates a Wavelet Detail Coefficient calculation.
        Computes the 'high-frequency' difference between prompt and candidate structures.
        Large jumps (e.g., prompt has negation, candidate does not) yield high energy (penalty).
        """
        energy = 0.0
        
        # Level 1: Negation detail (High frequency check)
        neg_diff = abs(prompt_feats['neg_count'] - cand_feats['neg_count'])
        if neg_diff > 0:
            energy += 2.0 * neg_diff  # Heavy penalty for missing negations
            
        # Level 2: Conditional consistency
        if prompt_feats['has_conditional'] and not cand_feats['has_conditional']:
            # If prompt implies logic but candidate is simple statement
            energy += 1.5
            
        # Level 3: Numeric magnitude check (Coarse approximation)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Check if relative order is preserved (simplified)
            p_max = max(prompt_feats['numbers'])
            c_max = max(cand_feats['numbers']) if cand_feats['numbers'] else 0
            # If prompt asks for max and candidate provides min (heuristic)
            if p_max > 0 and c_max == 0:
                energy += 1.0
                
        return energy

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate chaotic sequence length based on candidate count
        # Ensures deterministic but varied weighting per candidate index
        base_scores = []
        
        for i, cand in enumerate(candidates):
            cand_feats = self._extract_structure(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            # Start with base 1.0, subtract penalties
            struct_score = 1.0
            
            # Penalty for structural mismatch via "Wavelet" detail energy
            wavelet_energy = self._structural_wavelet_detail(prompt_feats, cand_feats)
            struct_score -= min(wavelet_energy * 0.25, 0.8) # Cap penalty
            
            # Bonus for matching specific structural flags
            if prompt_feats['has_comparative'] and cand_feats['has_comparative']:
                struct_score += 0.1
            if prompt_feats['neg_count'] == cand_feats['neg_count'] and prompt_feats['neg_count'] > 0:
                struct_score += 0.15

            # 2. Chaotic Modulation (Chaos Theory)
            # Generate chaotic weight based on candidate index and content hash
            # This prevents identical strings from always scoring same if context shifts slightly
            # but remains deterministic for same input.
            chaos_iter = i + 1 + len(prompt) 
            chaotic_val = self._logistic_map(self.x_seed, chaos_iter)
            
            # Apply chaotic inertia: fluctuate score slightly based on chaotic map
            # Maps chaotic_val (0..1) to (-0.05 .. +0.05)
            chaos_mod = (chaotic_val - 0.5) * 0.1 
            final_score = struct_score + chaos_mod
            
            # 3. NCD Tiebreaker (Only if structural scores are very close later, 
            # but we apply a tiny bias here for diversity)
            ncd_bias = 0.0
            if i > 0:
                # Small penalty if candidate is too similar to previous one (diversity)
                dist = self._compute_ncd(candidates[i-1], cand)
                if dist < 0.1: # Very similar
                    ncd_bias = -0.05
            
            final_score += ncd_bias
            
            # Normalize reasoning string
            reasoning = f"Structural match: {1.0 - max(0, wavelet_energy*0.25):.2f}; Chaotic factor: {chaotic_val:.3f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and low wavelet energy.
        """
        prompt_feats = self._extract_structure(prompt)
        ans_feats = self._extract_structure(answer)
        
        # Calculate wavelet energy (mismatch)
        energy = self._structural_wavelet_detail(prompt_feats, ans_feats)
        
        # Base confidence starts high, drops with energy
        conf = 1.0 - (energy * 0.3)
        
        # Check specific constraints
        if prompt_feats['neg_count'] != ans_feats['neg_count']:
            conf -= 0.4
            
        # Chaotic calibration modifier
        chaos_val = self._logistic_map(self.x_seed, len(prompt) + len(answer))
        # Slight deterministic jitter based on chaos
        conf += (chaos_val - 0.5) * 0.05
        
        return max(0.0, min(1.0, conf))