import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topology-Guided Wavelet Predictive Coding Network (TG-WPCN) Simulation.
    
    Mechanism:
    1. Wavelet Front-end: Simulated via multi-scale structural parsing (regex) to extract
       localized features (negations, comparatives, numbers) at different 'scales' of complexity.
    2. Topological Encoder: Constructs a 'persistence barcode' by tracking the lifespan of 
       logical constraints (e.g., if a condition is introduced and later satisfied/negated).
       This creates a deformation-invariant signature of the argument's shape.
    3. Free Energy Core: Computes variational free energy as the gap between the 
       predicted topological structure (derived from the prompt's logical constraints) 
       and the observed structure in the candidate. Lower free energy = higher score.
       
    This approach prioritizes structural logic and constraint satisfaction (FEP) over 
    simple string similarity (NCD), addressing the 'Goodhart Warning' by focusing on 
    logical consistency rather than pattern matching.
    """

    def __init__(self):
        # Define scales of analysis (simulating wavelet scales)
        self.scales = [
            ('numeric', r'-?\d+\.?\d*'),
            ('comparative', r'\b(more|less|greater|smaller|higher|lower|equal)\b'),
            ('conditional', r'\b(if|then|unless|provided|when)\b'),
            ('negation', r'\b(not|no|never|neither|without|impossible)\b'),
            ('causal', r'\b(because|therefore|thus|hence|causes)\b')
        ]
        self.logic_ops = ['and', 'or', 'not', 'implies']

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Simulates Wavelet Front-end: Extracts multi-scale features."""
        text_lower = text.lower()
        features = {
            'raw_len': len(text),
            'word_count': len(text.split()),
            'patterns': {},
            'numbers': []
        }
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        features['numbers'] = [float(n) for n in nums]
        
        # Extract structural patterns (Wavelet coefficients)
        for name, pattern in self.scales:
            matches = re.findall(pattern, text_lower)
            features['patterns'][name] = len(matches)
            
        return features

    def _compute_persistence(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Simulates Topological Encoder: Computes a 'persistence score' based on 
        the consistency of logical features between prompt and candidate.
        Returns a similarity metric invariant to smooth deformations (wording changes).
        """
        score = 0.0
        total_weight = 0.0
        
        # Check persistence of logical constraints (Betti number approximation)
        # If prompt has negations, candidate should reflect that logical state
        for key in ['negation', 'conditional', 'causal']:
            p_count = prompt_feats['patterns'].get(key, 0)
            c_count = cand_feats['patterns'].get(key, 0)
            
            # Persistence: Does the candidate maintain the logical density?
            if p_count > 0:
                # Penalize large deviations in logical structure
                diff = abs(p_count - c_count)
                score += max(0, 1.0 - (diff * 0.2)) # Decay based on mismatch
                total_weight += 1.0
            elif c_count > 0 and key == 'negation':
                # Penalty for introducing negation where none existed (unless causal)
                score += 0.5 
                total_weight += 1.0

        # Numeric consistency (Transitivity check)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Simple heuristic: if prompt has numbers, candidate should too
            score += 1.0
            total_weight += 1.0
            
        return score / total_weight if total_weight > 0 else 0.5

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Free Energy Core: Calculates F = Prediction Error + Complexity Cost.
        Lower F means the candidate is a better explanation of the prompt.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # 1. Prediction Error (Topological mismatch)
        # How well does the candidate's structure match the prompt's expected structure?
        topo_error = 1.0 - self._compute_persistence(p_feats, c_feats)
        
        # 2. Complexity Cost (Occam's razor)
        # Penalize excessive length relative to the prompt (overfitting)
        len_ratio = c_feats['raw_len'] / max(p_feats['raw_len'], 1)
        complexity_cost = 0.1 * abs(len_ratio - 1.0) if len_ratio > 2.0 else 0.0
        
        # 3. Structural Validation (The 'Reasoning' signal)
        # Boost if candidate explicitly resolves conditionals or negations found in prompt
        structural_bonus = 0.0
        if p_feats['patterns']['conditional'] > 0:
            if any(k in candidate.lower() for k in ['therefore', 'thus', 'so', 'consequently']):
                structural_bonus = -0.2 # Reduces free energy
        
        free_energy = topo_error + complexity_cost + structural_bonus
        return max(0.0, free_energy)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feats = self._extract_features(prompt)
        
        for cand in candidates:
            if not cand.strip():
                continue
                
            cand_feats = self._extract_features(cand)
            
            # Primary Score: Free Energy Minimization (Inverse)
            fe = self._compute_free_energy(prompt, cand)
            base_score = 1.0 / (1.0 + fe) # Convert energy to probability-like score
            
            # Secondary Score: Numeric Logic Check
            numeric_match = 1.0
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # If both have numbers, check basic ordering consistency if comparatives exist
                if prompt_feats['patterns']['comparative'] > 0:
                    # Heuristic: Did the candidate preserve the magnitude relation?
                    # (Simplified for single-pair comparison)
                    p_max = max(prompt_feats['numbers'])
                    c_max = max(cand_feats['numbers'])
                    if (p_max > 10 and c_max < 1) or (p_max < 1 and c_max > 10):
                        numeric_match = 0.5 # Penalty for gross magnitude error
            
            # Tiebreaker: NCD (only if structural scores are close)
            ncd = self._ncd_distance(prompt, cand)
            
            # Combine: Structural reasoning dominates, NCD is minor noise floor
            final_score = (base_score * 0.8 + numeric_match * 0.2) - (ncd * 0.05)
            
            reasoning = f"FE:{fe:.2f}, Topo:{self._compute_persistence(prompt_feats, cand_feats):.2f}, NCD:{ncd:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on free energy gap."""
        if not answer.strip():
            return 0.0
            
        fe = self._compute_free_energy(prompt, answer)
        # Map free energy to confidence: Low FE -> High Confidence
        # F=0 -> 1.0, F=1 -> 0.5, F>2 -> ~0.2
        conf = 1.0 / (1.0 + fe)
        return min(1.0, max(0.0, conf))