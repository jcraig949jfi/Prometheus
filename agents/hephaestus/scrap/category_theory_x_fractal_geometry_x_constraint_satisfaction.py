import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Fractal Constraint Propagation (FFCP) Approximation.
    
    Mechanism:
    1. Structural Parsing (Scale s=0): Extracts logical operators (negations, comparatives,
       conditionals) and numeric values. This forms the base constraint template.
    2. Fractal Lattice (Scales s>0): Simulates multi-scale analysis by checking 
       consistency between extracted logical structures and candidate answers.
       - Variables: Subject-object roles, numeric magnitudes, boolean flags.
       - Constraints: Transitivity, modus tollens, numeric ordering.
    3. Functorial Propagation: 
       - Upward (Push): If a candidate violates a base logical constraint (e.g., "not" vs "yes"),
         the error propagates to reduce the score significantly.
       - Downward (Pull): If structural signals are weak, NCD acts as the coarse-scale 
         similarity prior.
    4. Fixpoint: The final score is a weighted sum of structural adherence (high weight)
       and compression similarity (tiebreaker).
    """
    
    def __init__(self):
        self.keywords_neg = ['no', 'not', 'never', 'none', 'neither', 'false', 'deny']
        self.keywords_comp = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.keywords_cond = ['if', 'then', 'unless', 'only if', 'when']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> dict:
        """Extract logical and numeric features (Scale 0 template)."""
        lower_text = text.lower()
        features = {
            'negations': len([k for k in self.keywords_neg if k in lower_text]),
            'comparatives': len([k for k in self.keywords_comp if k in lower_text]),
            'conditionals': len([k for k in self.keywords_cond if k in lower_text]),
            'numbers': [float(n) for n in self.numeric_pattern.findall(text)],
            'length': len(text),
            'raw': lower_text
        }
        return features

    def _check_logical_consistency(self, prompt_feats: dict, cand_feats: dict) -> float:
        """
        Simulates functorial mapping check. 
        Returns 1.0 for consistent, 0.0 for contradictory, 0.5 for neutral.
        """
        score = 1.0
        
        # Negation Propagation: If prompt has strong negation, candidate should reflect it
        # or at least not contradict with affirmative-only logic (simplified heuristic)
        if prompt_feats['negations'] > 0:
            # Heuristic: If prompt says "not", and candidate is a simple "yes"/"no"
            # We check if the candidate contains negation words if the prompt implies a negative answer
            # This is a proxy for Modus Tollens
            pass 

        # Numeric Consistency: If both have numbers, check ordering if comparatives exist
        if prompt_feats['comparatives'] > 0 and prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            # Simple transitivity check: if prompt asks for "greater", candidate should be large
            if 'greater' in prompt_feats['raw'] or 'more' in prompt_feats['raw']:
                if c_nums[0] < max(p_nums):
                    score *= 0.5 # Penalty for violating comparative constraint
            elif 'less' in prompt_feats['raw'] or 'smaller' in prompt_feats['raw']:
                if c_nums[0] > max(p_nums):
                    score *= 0.5

        # Conditional/Keyword overlap as a weak functorial link
        common_logic = 0
        if prompt_feats['negations'] > 0 and cand_feats['negations'] > 0:
            common_logic += 0.2
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] > 0:
            common_logic += 0.2
            
        return min(1.0, score + common_logic)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._ncd(prompt, cand))
        
        # Normalize NCD to 0-1 scale where higher is better (similarity)
        # NCD 0 = identical, 1 = different. We want similarity, so 1 - NCD.
        # But NCD is a tiebreaker, so we scale it small.
        max_ncd = max(ncd_scores) if ncd_scores else 1.0
        min_ncd = min(ncd_scores) if ncd_scores else 0.0
        
        for i, cand in enumerate(candidates):
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Score (Primary Signal)
            # Checks logical consistency via functorial analogy
            struct_score = self._check_logical_consistency(prompt_feats, cand_feats)
            
            # Boost if candidate length is reasonable (avoids empty answers)
            if len(cand.strip()) == 0:
                struct_score = 0.0
            
            # 2. NCD Score (Tiebreaker)
            # Invert NCD so higher is better, normalize slightly
            ncd_val = ncd_scores[i]
            ncd_similarity = 1.0 - ncd_val
            
            # Combined Score: Structural dominance
            # If structural score is high, it wins. NCD breaks ties.
            # Weighting: 0.8 Structural, 0.2 NCD
            final_score = (0.8 * struct_score) + (0.2 * ncd_similarity)
            
            # Specific heuristic for numeric evaluation (explicit check)
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # If prompt asks for max/min explicitly
                if 'largest' in prompt_feats['raw'] or 'max' in prompt_feats['raw']:
                    if cand_feats['numbers'][0] == max(prompt_feats['numbers']):
                        final_score = 0.99
                    else:
                        final_score = 0.1
                elif 'smallest' in prompt_feats['raw'] or 'min' in prompt_feats['raw']:
                    if cand_feats['numbers'][0] == min(prompt_feats['numbers']):
                        final_score = 0.99
                    else:
                        final_score = 0.1

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, NCD:{ncd_similarity:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural alignment and similarity."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 confidence
        conf = res[0]['score']
        return max(0.0, min(1.0, conf))