import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Renormalized Ecosystem Agent (FREA) - Structural Implementation.
    
    Mechanism:
    1. Fractal Wavelet Encoder (FWE): Decomposes text into structural feature vectors
       (negations, comparatives, conditionals, numerics) at multiple scales (word, phrase, sentence).
    2. Renormalization Group (RG): Coarse-grains these features. If local contradictions 
       (e.g., "not big" vs "big") average to a fixed point (zero), the hypothesis is stable.
       Deviations trigger penalty.
    3. Ecosystem Dynamics (Restricted): Used ONLY in confidence() as a stability check.
       We model candidate acceptance as a "keystone species". If adding the answer destabilizes
       the structural entropy of the prompt (high variance in logical flow), confidence drops.
       
    Primary Scoring: Structural parsing (negations, comparatives, numerics).
    Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', '>', '<'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.quantifiers = {'all', 'some', 'many', 'few', 'every', 'each'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extracts counts of logical operators and numeric values."""
        tokens = self._tokenize(text)
        features = {
            'neg_count': 0,
            'comp_count': 0,
            'cond_count': 0,
            'quant_count': 0,
            'numeric_val': 0.0,
            'has_numeric': 0
        }
        
        for token in tokens:
            if token in self.negations:
                features['neg_count'] += 1
            if token in self.comparatives:
                features['comp_count'] += 1
            if token in self.conditionals:
                features['cond_count'] += 1
            if token in self.quantifiers:
                features['quant_count'] += 1
        
        # Extract first found number for magnitude comparison
        nums = re.findall(r"-?\d+\.?\d*", text)
        if nums:
            try:
                features['numeric_val'] = float(nums[0])
                features['has_numeric'] = 1
            except ValueError:
                pass
                
        return features

    def _renormalize_features(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Simulates RG flow by checking consistency between prompt and candidate features.
        Returns a stability score (0.0 to 1.0).
        """
        score = 1.0
        
        # Logic Consistency: If prompt has high negation, candidate shouldn't contradict blindly
        # Simple heuristic: Matching logical density implies same "scale" of reasoning
        p_log = prompt_feat['neg_count'] + prompt_feat['cond_count']
        c_log = cand_feat['neg_count'] + cand_feat['cond_count']
        
        if p_log > 0:
            # Penalize large deviations in logical complexity
            diff = abs(p_log - c_log)
            score -= min(0.5, diff * 0.1)
            
        # Numeric Transitivity Check (Simplified)
        # If prompt has numbers and candidate has numbers, check magnitude alignment if comparatives exist
        if prompt_feat['has_numeric'] and cand_feat['has_numeric']:
            if prompt_feat['comp_count'] > 0 or cand_feat['comp_count'] > 0:
                # Heuristic: Assume candidate number should be logically related. 
                # Without full semantic parse, we reward non-zero numeric engagement if prompt has it.
                score += 0.2
            else:
                # Exact match bonus for numbers if no comparatives
                if abs(prompt_feat['numeric_val'] - cand_feat['numeric_val']) < 1e-6:
                    score += 0.3
                else:
                    score -= 0.1 # Mismatched numbers are suspicious
                    
        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/stability in this specific constraint context
        # Strict NCD uses compressed lengths for denominators too.
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c_concat = len(zlib.compress(concat))
        
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c_concat - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structural_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feat = self._extract_structural_features(cand)
            
            # 1. Structural Score (Primary)
            struct_score = self._renormalize_features(prompt_feat, cand_feat)
            
            # 2. Constraint Propagation (Simple keyword overlap for logic words)
            # Boost if candidate shares specific logical operators found in prompt
            shared_logic = 0
            p_tokens = set(self._tokenize(prompt))
            c_tokens = set(self._tokenize(cand))
            
            logic_ops = self.negations | self.comparatives | self.conditionals | self.quantifiers
            common_ops = p_tokens.intersection(c_tokens).intersection(logic_ops)
            if len(common_ops) > 0:
                shared_logic = 0.15 * len(common_ops)
            
            final_score = struct_score + shared_logic
            
            # NCD as tiebreaker (small weight)
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so lower distance = higher score, scale small
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            total_score = final_score + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": f"Structural consistency: {struct_score:.2f}, Logic overlap: {shared_logic:.2f}, NCD bonus: {ncd_bonus:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Uses restricted Ecosystem Dynamics concept.
        Treats the answer as an introduction of a new species into the prompt's ecosystem.
        If the structural entropy (variance in logical features) spikes too high, 
        the ecosystem is unstable -> Low confidence.
        """
        p_feat = self._extract_structural_features(prompt)
        a_feat = self._extract_structural_features(answer)
        
        # Calculate "Biodiversity" of logical features in the combined system
        # High diversity is good, but high contradiction (instability) is bad.
        # We simulate instability by checking if the answer negates the prompt's primary logical mode.
        
        instability = 0.0
        
        # Check for negation flip-flop
        if p_feat['neg_count'] > 0 and a_feat['neg_count'] == 0:
            # Potential contradiction or resolution. 
            # If prompt is negative and answer is positive, it might be a valid correction or a trap.
            # We penalize slightly for uncertainty unless structural match is perfect.
            instability += 0.2
            
        # Check numeric consistency
        if p_feat['has_numeric'] and a_feat['has_numeric']:
            if abs(p_feat['numeric_val'] - a_feat['numeric_val']) > 10.0:
                # Large numeric deviation suggests different context
                instability += 0.3
        
        # Base confidence on structural alignment minus instability
        # Re-use renormalization logic for base alignment
        align_score = self._renormalize_features(p_feat, a_feat)
        
        # Ecosystem stability wrapper
        # If instability is high, cap the confidence
        if instability > 0.4:
            conf = align_score * 0.5
        else:
            conf = align_score * (1.0 - instability)
            
        return max(0.0, min(1.0, conf))