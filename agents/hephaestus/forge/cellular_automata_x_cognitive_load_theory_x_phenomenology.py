import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenal Cellular Automaton with Adaptive Chunking (PCA-AC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Phenomenological Layer): Extracts logical operators, negations,
       comparatives, and numeric values from the prompt. This forms the "intentionality" 
       and "bracketing" flags.
    2. Cognitive Load Scheduler: Limits the depth of logical traversal based on a fixed 
       working memory capacity (chunking). Prevents overload by prioritizing high-salience 
       tokens (numbers, booleans).
    3. Cellular Automata Lattice: Maps parsed tokens to a 1D lattice (simplified from 2D 
       for efficiency). Update rules propagate truth values based on local consistency 
       (Moore neighborhood analog). Contradictions (e.g., "True" next to "False" without 
       a negation operator) reduce confidence.
    4. Scoring: Candidates are evaluated by simulating their integration into the lattice.
       The score reflects the stability (low contradiction) and structural alignment.
    5. NCD Tiebreaker: Used only when structural signals are ambiguous.
    """

    def __init__(self):
        self.capacity_threshold = 7  # Cognitive load limit (Miller's 7±2)
        self.grid_size = 20
        self.base_confidence = 0.5

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical structure, numbers, and negations."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|>\|<)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'boolean_literals': re.findall(r'\b(true|false)\b', text_lower),
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _simulate_ca_lattice(self, prompt_features: Dict, candidate_features: Dict) -> float:
        """
        Simulate the PCA-AC lattice.
        - Cells represent logical tokens.
        - Update rules check consistency between prompt and candidate.
        - Returns a stability score (0.0 to 1.0).
        """
        # Initialize lattice with prompt features (simplified as active cells)
        # We map features to a numeric representation for the CA
        prompt_load = (
            prompt_features['negations'] * 2 +
            prompt_features['conditionals'] * 2 +
            len(prompt_features['numbers']) +
            len(prompt_features['boolean_literals'])
        )
        
        # Cognitive Load Throttling: If complexity exceeds capacity, we penalize deep reasoning
        # and rely more on direct matching.
        load_factor = 1.0 if prompt_load <= self.capacity_threshold else 0.6
        
        # Consistency Check (The "Phenomenological" contradiction detection)
        contradictions = 0
        matches = 0
        
        # Check boolean consistency
        p_bools = set(prompt_features['boolean_literals'])
        c_bools = set(candidate_features['boolean_literals'])
        
        if p_bools and c_bools:
            if p_bools != c_bools:
                contradictions += 2
            else:
                matches += 2
                
        # Check numeric consistency (simplified: presence of same numbers)
        if prompt_features['numbers'] and candidate_features['numbers']:
            # Do they share numbers?
            common_nums = set(prompt_features['numbers']) & set(candidate_features['numbers'])
            if common_nums:
                matches += len(common_nums)
            else:
                # Candidate introduces new numbers not in prompt? Potential hallucination or calculation.
                # In a reasoning task, if prompt has numbers, candidate usually needs them.
                contradictions += 1 
        elif not prompt_features['numbers'] and candidate_features['numbers']:
            # Candidate adds numbers where none existed (risky)
            contradictions += 1

        # Logical Operator Alignment
        if prompt_features['negations'] > 0:
            if candidate_features['negations'] == 0 and prompt_features['negations'] > 1:
                # Missing necessary negation depth
                contradictions += 1
            else:
                matches += 1

        # Base score from matches vs contradictions
        raw_score = (matches + 1) / (matches + contradictions + 2)
        
        # Apply cognitive load penalty
        final_score = raw_score * load_factor
        
        return min(1.0, max(0.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._parse_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = [(c, self._compute_ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd = max(s[1] for s in ncd_scores)
        ncd_range = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for cand in candidates:
            cand_feat = self._parse_structure(cand)
            
            # Primary Score: Structural/CA Simulation
            ca_score = self._simulate_ca_lattice(prompt_feat, cand_feat)
            
            # Secondary Score: NCD Tiebreaker (normalized)
            # Lower NCD is better. We invert it so higher is better.
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_normalized = 1.0 - ((ncd_val - min_ncd) / ncd_range) if ncd_range > 0 else 0.5
            
            # Weighted combination: Structural is dominant (90%), NCD is tiebreaker (10%)
            # But if structural signal is weak (all candidates look same structurally), NCD weight increases
            structural_signal_strength = abs(ca_score - 0.5) 
            # If signal is weak (close to 0.5), rely more on NCD
            ncd_weight = 0.4 if structural_signal_strength < 0.1 else 0.1
            
            final_score = (ca_score * (1 - ncd_weight)) + (ncd_normalized * ncd_weight)
            
            reasoning = f"CA_Stability:{ca_score:.2f}; Load:{prompt_feat['length']}; NCD:{ncd_val:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        # The score itself represents the likelihood/correctness probability
        return ranked[0]["score"]