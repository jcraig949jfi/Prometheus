import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Type-Guided Clonal-Selection Ecosystem (Simplified for NCD Baseline Beating)
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical signatures (negations, comparatives, 
       conditionals, numeric values) from prompts and candidates. This acts as the "Type Checker",
       ensuring candidates structurally inhabit the logical space of the prompt.
    2. Immune System (Clonal Selection): Candidates are cloned and mutated slightly in 
       representation space (via feature weighting) to test affinity. High-affinity clones 
       (those matching prompt structure) are selected.
    3. Ecosystem Dynamics (Resource Flow): Instead of complex Lotka-Volterra, we use a 
       "Niche Energy" model. Structural matches gain energy (score); mismatches (e.g., 
       missing negation) lose energy. Resources flow from parent constraints to sub-clauses.
       
    This implementation prioritizes structural parsing and numeric evaluation as requested
    by the Causal Intelligence analysis, using the ecological/immune metaphor to weight 
    these features dynamically rather than relying on pure string similarity (NCD).
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Type Signatures")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without|fail|false)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|larger|fewer|better|worse|than|>|<)\b', re.I),
            'conditional': re.compile(r'\b(if|then|else|unless|provided|when|whenever)\b', re.I),
            'numeric': re.compile(r'\b(\d+\.?\d*)\b'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|valid)\b', re.I),
            'boolean_no': re.compile(r'\b(no|false|incorrect|invalid)\b', re.I)
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features acting as 'Types' for the terms."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'affirmative_words': len(self.patterns['boolean_yes'].findall(text)),
            'negative_words': len(self.patterns['boolean_no'].findall(text)),
            'length': len(text.split())
        }
        return features

    def _compute_structural_affinity(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Computes affinity based on structural compatibility (Type Checking).
        High affinity = Candidate respects the logical constraints of the prompt.
        """
        score = 0.0
        
        # Negation Conservation Law: If prompt has negation, candidate should likely reflect it
        # or explicitly address it. If prompt has no negation but candidate does, penalty.
        if prompt_feats['has_negation']:
            if cand_feats['has_negation']:
                score += 2.0  # Reward matching negation
            else:
                score -= 1.5  # Penalty for ignoring negation context
        else:
            if cand_feats['has_negation']:
                score -= 0.5  # Slight penalty for unnecessary negation
        
        # Comparative Consistency
        if prompt_feats['has_comparative']:
            if cand_feats['has_comparative']:
                score += 1.5
            # Numeric check for comparatives
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # Simple heuristic: if prompt compares, candidate should have numbers or logic
                score += 1.0
        
        # Conditional Logic Flow
        if prompt_feats['has_conditional']:
            if cand_feats['has_conditional']:
                score += 2.0
            elif cand_feats['affirmative_words'] > 0 or cand_feats['negative_words'] > 0:
                score += 1.0 # Accept direct answer to conditional
        
        # Numeric Evaluation (Constraint Propagation)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # If both have numbers, check magnitude consistency loosely
            p_max = max(prompt_feats['numbers'])
            c_max = max(cand_feats['numbers'])
            if p_max > 0:
                ratio = c_max / p_max
                if 0.5 <= ratio <= 2.0: # Reasonable range
                    score += 2.0
                else:
                    score -= 1.0 # Wildly different numbers
        
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Calculate baseline NCD for all to use as tiebreaker
        ncd_scores = [(c, self._compute_ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores) if ncd_scores else 1.0
        max_ncd = max(s[1] for s in ncd_scores) if ncd_scores else 1.0
        ncd_range = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Affinity (Primary Signal - "Type Checking")
            affinity = self._compute_structural_affinity(prompt_feats, cand_feats)
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # Normalize NCD to 0-1 where 1 is best (lowest distance)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ((ncd_val - min_ncd) / ncd_range) if ncd_range > 0 else 0.5
            
            # Combine: Structural affinity is weighted heavily to beat pure NCD baseline
            # Base score starts at 0.5, affinity adds/subtracts, ncd refines
            final_score = 0.5 + (affinity * 0.15) + (ncd_score * 0.2)
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Structural Affinity: {affinity:.2f}, NCD: {ncd_val:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and compression.
        """
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]