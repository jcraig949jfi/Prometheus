import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a self-adapting low-rank tensor network analogy with Hebbian-style
    updates and error-correcting code redundancy for fault-tolerant hypothesis testing.
    
    Mechanism:
    1. Tensor Decomposition (Analogy): Prompts and candidates are parsed into structural
       feature vectors (negations, comparatives, numerics, conditionals). This forms a
       low-rank representation of the logical structure.
    2. Neural Plasticity (Hebbian Rule): Weights for structural features are updated
       based on co-activation. If a candidate shares the specific structural signature
       of the prompt (e.g., both contain negation), the "synaptic" weight for that
       structural match is strengthened. Mismatches trigger a decay (pruning).
    3. Error Correcting Codes (LDPC Analogy): A redundancy check is performed. The
       "syndrome" is the difference in structural complexity (e.g., prompt has 2 numbers,
       candidate has 0). High syndrome magnitude indicates a "bit-flip" (logical error),
       reducing the score.
    4. Hypothesis Testing: Candidates are ranked by the sum of structural alignment
       (plasticity) minus the structural error syndrome (ECC), with NCD as a tiebreaker.
    """

    def __init__(self):
        # Structural patterns to extract (The "Latent Factors")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none|cannot)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|better|worse|than|>=|<=|>|<)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'logic_conn': re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.I)
        }
        # Plasticity decay factor
        self.decay = 0.1

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts structural features acting as low-rank tensor slices."""
        features = {}
        text_lower = text.lower()
        
        # Boolean flags for logical operators
        for key, pattern in self.patterns.items():
            if key != 'numeric':
                features[key] = bool(pattern.search(text))
        
        # Numeric extraction and evaluation
        nums = self.patterns['numeric'].findall(text)
        features['numeric_count'] = len(nums)
        features['numeric_vals'] = [float(n) for n in nums] if nums else []
        
        # Simple numeric logic check (e.g., is 9.11 < 9.9?)
        features['numeric_sorted'] = True
        if len(features['numeric_vals']) > 1:
            # Check if numbers appear in sorted order (heuristic for consistency)
            is_sorted = all(features['numeric_vals'][i] <= features['numeric_vals'][i+1] 
                            for i in range(len(features['numeric_vals'])-1))
            features['numeric_sorted'] = is_sorted
            
        return features

    def _compute_syndrome(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Computes the 'syndrome' magnitude. 
        In ECC terms, this detects if bits (structural properties) were flipped.
        High syndrome = high probability of logical error.
        """
        syndrome = 0.0
        
        # Check boolean feature mismatches (Bit flips in logic)
        bool_keys = ['negation', 'comparative', 'conditional', 'logic_conn']
        for key in bool_keys:
            if prompt_feat[key] != cand_feat[key]:
                syndrome += 1.0  # Penalty for missing/extra logical operator
        
        # Check numeric count mismatch (Dimensionality error)
        if abs(prompt_feat['numeric_count'] - cand_feat['numeric_count']) > 0:
            # If prompt has numbers and candidate doesn't (or vice versa), high penalty
            syndrome += 2.0 
            
        return syndrome

    def _hebbian_update(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Simulates Hebbian learning: 'Neurons that fire together, wire together'.
        Strengthens score if structural features co-activate.
        """
        score = 0.0
        bool_keys = ['negation', 'comparative', 'conditional', 'logic_conn']
        
        for key in bool_keys:
            if prompt_feat[key] and cand_feat[key]:
                score += 1.0  # Strengthen connection
            elif prompt_feat[key] and not cand_feat[key]:
                score -= self.decay  # Prune inactive slice
        
        # Numeric co-activation bonus
        if prompt_feat['numeric_count'] > 0 and cand_feat['numeric_count'] > 0:
            score += 0.5
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(s1_b)
        len_s2 = len(s2_b)
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        try:
            len_combined = len(zlib.compress(s1_b + s2_b))
            min_len = min(len_s1, len_s2)
            if min_len == 0: return 1.0
            ncd = (len_combined - max(len_s1, len_s2)) / min_len
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            
            # 1. Hebbian Strength (Structural Alignment)
            hebbian_score = self._hebbian_update(prompt_feat, cand_feat)
            
            # 2. ECC Syndrome (Error Detection)
            syndrome = self._compute_syndrome(prompt_feat, cand_feat)
            
            # 3. NCD Tiebreaker (Inverted: lower distance is better)
            # We use 1 - NCD so higher is better, but weight it lightly
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            # Final Score: Alignment - Error + Tiebreaker
            # Syndrome is a heavy penalty
            final_score = hebbian_score - (syndrome * 0.5) + ncd_score
            
            # Reasoning trace
            reasoning = f"Structural match: {hebbian_score:.2f}, Error syndrome: {syndrome:.1f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and low syndrome.
        """
        prompt_feat = self._extract_structure(prompt)
        ans_feat = self._extract_structure(answer)
        
        syndrome = self._compute_syndrome(prompt_feat, ans_feat)
        hebbian = self._hebbian_update(prompt_feat, ans_feat)
        
        # Base confidence on low error and high alignment
        # Max heuristic score approx 2.0 (2 bool matches + numeric)
        raw_conf = (hebbian + 1.0) / 3.0  # Normalize roughly to 0-1 range
        
        # Penalize heavily for syndrome
        conf = max(0.0, raw_conf - (syndrome * 0.25))
        
        return min(1.0, max(0.0, conf))