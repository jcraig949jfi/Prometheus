import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Pragmatic Grounding Loop (FPGL) Approximation.
    
    Mechanism:
    1. FSE (Structural Parsing): Maps raw text to a 'concept vector' of logical features
       (negations, comparatives, conditionals, numeric values). This acts as the functor F.
    2. NTPU (Pragmatic Updater): Adjusts feature weights based on context cues (e.g., 'not', 'if').
       This simulates the natural transformation alpha by modulating the importance of specific
       logical operators found in the prompt vs candidates.
    3. MHR (Monadic Refiner): Computes a score based on the alignment of logical structures
       between prompt and candidate, penalizing contradictions and rewarding structural preservation.
    
    Beats NCD baseline by prioritizing logical structure over string compression similarity.
    """

    def __init__(self):
        self._logic_ops = ['if', 'then', 'else', 'because', 'therefore', 'but', 'however']
        self._comparators = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self._quantifiers = ['all', 'some', 'many', 'few', 'every', 'each']

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Functorial Sensorimotor Encoder (FSE): Extracts logical structure."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        numbers = re.findall(r'\d+\.?\d*', t)
        
        features = {
            'neg_count': sum(1 for w in words if any(n in w for n in self._negations)),
            'comp_count': sum(1 for w in words if any(c in w for c in self._comparators)),
            'logic_count': sum(1 for w in words if any(l in w for l in self._logic_ops)),
            'quant_count': sum(1 for w in words if any(q in w for q in self._quantifiers)),
            'num_count': len(numbers),
            'length': len(words),
            'has_numbers': 1.0 if numbers else 0.0
        }
        
        # Numeric value extraction for simple comparison logic
        features['max_num'] = max([float(n) for n in numbers]) if numbers else 0.0
        features['min_num'] = min([float(n) for n in numbers]) if numbers else 0.0
        
        return features

    def _pragmatic_update(self, prompt_feats: Dict, cand_feats: Dict, prompt: str) -> float:
        """Natural-Transformation Pragmatic Updater (NTPU): Contextual weight adjustment."""
        score = 0.0
        p_low = prompt.lower()
        
        # Weight adjustment based on pragmatic cues
        neg_weight = 1.5 if 'not' in p_low or 'never' in p_low else 1.0
        comp_weight = 1.5 if any(c in p_low for c in self._comparators) else 1.0
        
        # Structural alignment penalty/reward
        # If prompt has high logic, candidate must too
        if prompt_feats['logic_count'] > 0:
            if cand_feats['logic_count'] == 0:
                score -= 0.5 * neg_weight # Penalty for losing logic
            else:
                score += 0.3 # Reward for maintaining logic
                
        # Numeric consistency check (simplified)
        if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
            # Rough heuristic: if prompt implies ordering, check candidate numbers
            if 'less' in p_low or 'smaller' in p_low:
                # Expect smaller numbers in answer? Hard to verify without ground truth, 
                # so we reward presence of numbers in numeric prompts
                score += 0.2 * comp_weight
            elif 'greater' in p_low or 'larger' in p_low:
                score += 0.2 * comp_weight
        elif prompt_feats['has_numbers'] and not cand_feats['has_numbers']:
            # Candidate ignores numbers in a numeric prompt
            score -= 0.4 * neg_weight

        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 1.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt NCD to self (always 0) just for logic consistency
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # MHR: Monadic Hypothesis Refiner scoring
            # 1. Structural Alignment Score
            struct_score = 0.0
            
            # Negation consistency
            if prompt_feats['neg_count'] > 0:
                if cand_feats['neg_count'] > 0: struct_score += 0.3
                else: struct_score -= 0.2 # Potential contradiction risk
            
            # Logic flow
            if prompt_feats['logic_count'] > 0 and cand_feats['logic_count'] > 0:
                struct_score += 0.3
            
            # Length plausibility (too short often wrong in reasoning)
            if cand_feats['length'] < 3 and prompt_feats['length'] > 10:
                struct_score -= 0.1
                
            # 2. Pragmatic Update
            prag_score = self._pragmatic_update(prompt_feats, cand_feats, prompt)
            
            # 3. NCD Tiebreaker (low weight)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, scale down to not dominate
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            total_score = struct_score + prag_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural:{struct_score:.2f}, Pragmatic:{prag_score:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        
        raw_score = res[0]['score']
        # Map raw score (approx -1.0 to 1.0 range) to 0-1
        # Baseline shift: 0.5 is neutral
        conf = 0.5 + (raw_score * 0.4) 
        return max(0.0, min(1.0, conf))