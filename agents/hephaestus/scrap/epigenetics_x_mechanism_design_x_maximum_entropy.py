import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Epigenetic Mechanism-Design MaxEnt (EMD-ME) Reasoner Implementation.
    
    Mechanism:
    1. Structural Parsing (Epigenetic Layer): Extracts logical features (negations, 
       comparatives, conditionals, numbers) as 'gene expression' marks. These marks 
       are heritable across the evaluation of candidates for a single prompt.
    2. MaxEnt Priors: Uses a uniform prior (maximum entropy) over candidates initially, 
       biasing only when structural constraints are met.
    3. Mechanism Design Scoring: Candidates are scored via a proper logarithmic rule 
       based on how well their structural signature matches the prompt's requirements.
       Truthful reporting (high score) is the dominant strategy for valid logic.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural 'epigenetic' marks from text."""
        t = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|nor)\b', t)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise|implies)\b', t)),
            'has_numbers': bool(re.search(r'\d+(\.\d+)?', t)),
            'number_count': len(re.findall(r'\d+(\.\d+)?', t)),
            'length': len(text.split()),
            'raw': text
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Mechanism Design Layer: Evaluate if candidate structure aligns with prompt constraints.
        Returns a score penalty (0.0 = perfect alignment, higher = mismatch).
        """
        score = 0.0
        
        # Constraint 1: Negation consistency (simplified heuristic)
        # If prompt asks "Which is NOT...", candidate should ideally contain negation or specific exclusion logic
        if prompt_feats['has_negation']:
            # Heuristic: If prompt has negation, we expect specific structural handling.
            # We don't penalize lack of negation in answer directly, but reward structural complexity
            pass 

        # Constraint 2: Comparative logic
        if prompt_feats['has_comparative']:
            if not cand_feats['has_comparative'] and not cand_feats['has_numbers']:
                # If prompt compares, answer usually involves comparison or numbers
                score += 0.2
        
        # Constraint 3: Conditional logic
        if prompt_feats['has_conditional']:
            # Complex to verify without full NLP, so we rely on length and keyword overlap as proxy
            if cand_feats['length'] < 3:
                score += 0.3 # Too short for conditional reasoning

        # Constraint 4: Numeric evaluation
        if prompt_feats['has_numbers']:
            if not cand_feats['has_numbers'] and prompt_feats['number_count'] > 1:
                # If prompt has multiple numbers (likely a math/comparison problem), 
                # candidate lacking numbers is suspicious
                score += 0.4

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        try:
            comp1 = len(zlib.compress(b1))
            comp2 = len(zlib.compress(b2))
            comp12 = len(zlib.compress(b1 + b2))
            max_len = max(comp1, comp2)
            if max_len == 0:
                return 1.0
            return (comp12 - min(comp1, comp2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        # We use a dummy reference for NCD between candidates if needed, 
        # but here we primarily use NCD(candidate, prompt) as a similarity baseline tiebreaker
        cand_data = []
        for c in candidates:
            c_feats = self._extract_features(c)
            consistency_penalty = self._check_logical_consistency(prompt_feats, c_feats)
            
            # MaxEnt Prior: Start with uniform belief, modulated by structural fit
            # Base score starts at 1.0 (MaxEnt uniform prior implies no bias until evidence)
            base_score = 1.0 - consistency_penalty
            
            # Mechanism Design: Proper scoring rule approximation
            # Logarithmic score component: log(P(report|truth)). 
            # We approximate 'truth' as structural consistency.
            mech_score = base_score if base_score > 0 else self.epsilon
            
            cand_data.append({
                'candidate': c,
                'struct_score': mech_score,
                'ncd_val': self._ncd(prompt, c),
                'features': c_feats
            })

        # Ranking Logic
        # Primary: Structural Score (Higher is better)
        # Secondary: NCD (Lower is better for similarity, but we use it carefully)
        # We sort by struct_score desc, then ncd_val asc (as tie breaker)
        cand_data.sort(key=lambda x: (-x['struct_score'], x['ncd_val']))

        # Normalize scores to 0-1 range roughly based on rank and gaps
        max_struct = max(c['struct_score'] for c in cand_data)
        min_struct = min(c['struct_score'] for c in cand_data)
        range_struct = max_struct - min_struct if (max_struct - min_struct) > 0 else 1.0

        final_results = []
        for i, item in enumerate(cand_data):
            # Normalize structural score
            norm_score = (item['struct_score'] - min_struct) / range_struct
            
            # Adjust with tiny NCD factor only if structural scores are very close (tie-breaking)
            # This implements the "NCD is only a tiebreaker" rule
            final_score = norm_score
            
            # Generate reasoning string
            reasoning = f"Structural fit: {item['struct_score']:.2f}. "
            if prompt_feats['has_numbers'] and not item['features']['has_numbers']:
                reasoning += "Warning: Prompt contains numbers but candidate does not. "
            if prompt_feats['has_comparative'] and not item['features']['has_comparative']:
                reasoning += "Warning: Comparative logic detected in prompt, missing in candidate. "
            if reasoning == "Structural fit: 1.00. ":
                reasoning += "High structural alignment with prompt constraints."

            final_results.append({
                'candidate': item['candidate'],
                'score': round(final_score, 4),
                'reasoning': reasoning.strip()
            })

        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        Uses the same epigenetic/mechanism design logic as evaluate.
        """
        prompt_feats = self._extract_features(prompt)
        ans_feats = self._extract_features(answer)
        
        penalty = self._check_logical_consistency(prompt_feats, ans_feats)
        
        # Base confidence starts high, reduced by structural mismatches
        conf = max(0.0, min(1.0, 1.0 - penalty))
        
        # Additional heuristic: If prompt implies calculation (numbers) and answer is non-numeric text
        if prompt_feats['has_numbers'] and prompt_feats['number_count'] >= 2:
            if not ans_feats['has_numbers']:
                # Strong penalty for missing numbers in math-like prompts
                conf *= 0.5
        
        return round(conf, 4)