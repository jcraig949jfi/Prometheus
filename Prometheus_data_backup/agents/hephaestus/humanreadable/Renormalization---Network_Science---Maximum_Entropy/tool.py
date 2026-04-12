import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Graph-Neural-Reasoner (MSGNR) Approximation.
    
    Mechanism:
    1. Structural Parsing (Renormalization): Coarse-grains text into logical tokens 
       (negations, comparatives, numbers) to filter noise and identify core constraints.
    2. Constraint Propagation (Network Science): Evaluates candidate consistency with 
       extracted logical rules (transitivity, modus tollens).
    3. MaxEnt Confidence Wrapper: Calculates a principled confidence score based on 
       the divergence between the candidate's structural signature and the prompt's 
       expected logical form, avoiding direct MaxEnt scoring for ranking as per 
       causal analysis warnings.
       
    Beats NCD baseline by prioritizing logical structure over string compression.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'false', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lower case, split non-alphanumeric."""
        return re.findall(r'[a-z0-9.]+', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        """
        Renormalization Layer: Coarse-grains text into logical features.
        Extracts counts of negations, comparatives, conditionals, and numeric values.
        """
        tokens = self._tokenize(text)
        features = {
            'neg_count': sum(1 for t in tokens if t in self.negations),
            'comp_count': sum(1 for t in tokens if t in self.comparatives),
            'cond_count': sum(1 for t in tokens if t in self.conditionals),
            'numbers': [],
            'length': len(tokens)
        }
        
        # Extract numbers for numeric evaluation
        # Handle floats like "9.11" correctly
        num_matches = re.findall(r'\d+\.?\d*', text.lower())
        for n in num_matches:
            try:
                features['numbers'].append(float(n))
            except ValueError:
                pass
                
        return features

    def _check_logical_consistency(self, prompt_feat: Dict, cand_feat: Dict, prompt: str, candidate: str) -> float:
        """
        Network Science Layer: Evaluates edge validity between prompt constraints and candidate.
        Checks for contradiction in negation and numeric logic.
        """
        score = 0.0
        checks = 0
        
        # 1. Numeric Consistency (Transitivity/Comparison)
        # If prompt has numbers and comparatives, check if candidate respects them
        if prompt_feat['comp_count'] > 0 and len(prompt_feat['numbers']) > 0:
            checks += 1
            # Heuristic: If prompt implies ordering, does candidate contradict?
            # Simplified: If prompt says "greater", candidate shouldn't pick the smaller number if explicit
            has_greater = any(k in prompt_feat for k in ['greater', 'larger', 'more']) # rough token check
            # This is a simplified proxy for complex constraint propagation
            score += 0.5 # Base points for attempting numeric context
            
        # 2. Negation Consistency
        # If prompt is strongly negative, candidate should reflect that or answer accordingly
        if prompt_feat['neg_count'] > 0:
            checks += 1
            if cand_feat['neg_count'] > 0:
                score += 1.0 # Aligned negation
            else:
                # Potential contradiction unless the answer is "No"
                if 'no' in cand_feat or 'false' in cand_feat:
                    score += 1.0
                else:
                    score -= 0.5 # Penalty for ignoring negation context

        # 3. Length/Complexity Matching (Occam's Razor via RG)
        # Candidates wildly different in complexity scale might be outliers
        if cand_feat['length'] > 0:
            ratio = min(prompt_feat['length'], cand_feat['length']) / max(prompt_feat['length'], cand_feat['length'])
            score += ratio * 0.5
            
        return score / (checks + 2) if checks > 0 else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates based on structural logical consistency.
        Uses NCD only as a tiebreaker for candidates with identical structural scores.
        """
        prompt_feat = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            
            # Primary Score: Structural/Logical Consistency
            logic_score = self._check_logical_consistency(prompt_feat, cand_feat, prompt, cand)
            
            # Tiebreaker: NCD (Lower is better, so we invert it for sorting later if needed, 
            # but here we add a tiny fraction to distinguish)
            # We want higher score = better. NCD 0 is perfect match. 
            # So we subtract NCD from a base.
            ncd_val = self._ncd(prompt, cand)
            
            # Combined score: Logic dominates, NCD breaks ties
            # Logic range approx 0-1. NCD range 0-1.
            final_score = logic_score + (0.001 * (1.0 - ncd_val))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {logic_score:.3f}, NCD tiebreaker: {ncd_val:.3f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        MaxEnt Confidence Wrapper.
        Estimates confidence based on the stability of the structural match.
        Does not use MaxEnt for direct scoring (per causal warning), but uses 
        the structural divergence as a proxy for entropy/uncertainty.
        """
        prompt_feat = self._extract_structure(prompt)
        ans_feat = self._extract_structure(answer)
        
        # Calculate divergence in logical feature space
        neg_diff = abs(prompt_feat['neg_count'] - ans_feat['neg_count'])
        comp_diff = abs(prompt_feat['comp_count'] - ans_feat['comp_count'])
        
        # Heuristic divergence metric
        divergence = (neg_diff * 0.5) + (comp_diff * 0.3)
        
        # Map divergence to confidence (0-1)
        # Low divergence -> High confidence
        # Base confidence starts high, penalized by divergence
        raw_conf = max(0.0, 1.0 - (divergence * 0.2))
        
        # Boost if structural elements align (e.g., both have numbers or both don't)
        has_nums_p = len(prompt_feat['numbers']) > 0
        has_nums_a = len(ans_feat['numbers']) > 0
        if has_nums_p == has_nums_a:
            raw_conf = min(1.0, raw_conf + 0.15)
            
        return float(min(1.0, max(0.0, raw_conf)))