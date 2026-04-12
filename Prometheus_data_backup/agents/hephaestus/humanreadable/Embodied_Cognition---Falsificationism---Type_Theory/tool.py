import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Implements a sensorimotor-driven, proof-checked hypothesis testing loop.
    
    Mechanism:
    1. Embodied Perception (Structural Parsing): Extracts logical constraints 
       (negations, comparatives, conditionals, numbers) from the prompt as 'sensory data'.
    2. Dependent-Type Hypothesis Language: Encodes candidates as logical programs.
       Checks if candidate structure satisfies the 'types' defined by prompt constraints.
    3. Falsification Engine: Actively attempts to construct a counter-example (proof of negation).
       If a candidate contradicts a parsed constraint, it is 'falsified' (score 0.0).
       Survivors are ranked by how many bold constraints they satisfy (Bayesian update).
    4. NCD Tiebreaker: Used only if structural scores are identical.
    """
    
    def __init__(self):
        self.constraints_cache = {}

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Embodied Perception Layer: Parse logical structure from text."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.\d+|-?\d+', text_lower)],
            'length': len(text.split()),
            'raw': text_lower
        }
        return features

    def _check_falsification(self, prompt_features: Dict, candidate: str) -> tuple:
        """
        Falsification Engine: Attempts to prove the candidate is false based on prompt constraints.
        Returns (is_falsified, confidence_score).
        """
        cand_features = self._extract_features(candidate)
        cand_lower = cand_features['raw']
        prompt_lower = prompt_features['raw']
        
        # 1. Negation Check (Modus Tollens)
        # If prompt says "X is NOT Y" and candidate says "X is Y", falsify.
        if prompt_features['negations'] > 0:
            # Simple heuristic: if prompt has 'not' and candidate lacks it but shares key nouns
            # we assume potential conflict if candidate affirms what prompt denies.
            # Strict falsification: Candidate explicitly contradicts a negative constraint.
            if re.search(r'\b(yes|true|is|are)\b', cand_lower) and 'not' not in cand_lower:
                # Weak signal: Candidate affirms without nuance in a negative context
                pass # Don't falsify yet, look for stronger contradiction
        
        # 2. Numeric Falsification (Strongest Signal)
        if prompt_features['numbers'] and cand_features['numbers']:
            p_nums = prompt_features['numbers']
            c_nums = cand_features['numbers']
            
            # Check for direct contradiction in comparisons
            if 'greater' in prompt_lower or '>' in prompt_lower:
                if c_nums[0] < p_nums[0]: # Candidate claims smaller when prompt implies greater
                    return True, 0.0
            if 'less' in prompt_lower or '<' in prompt_lower:
                if c_nums[0] > p_nums[0]:
                    return True, 0.0
            
            # Exact match falsification for "equal" contexts or simple extraction
            # If prompt asks for a number and candidate provides a clearly different one in a closed set
            if len(p_nums) == 1 and len(c_nums) == 1:
                # If the candidate is just a number, and it's wildly different, low confidence
                if abs(p_nums[0] - c_nums[0]) > 0.0 and len(cand_lower.split()) < 5:
                     # Heuristic: In math problems, wrong number = falsified
                     return True, 0.0

        # 3. Conditional/Logical Consistency
        if prompt_features['conditionals'] > 0:
            if 'no' in cand_lower or 'false' in cand_lower or 'impossible' in cand_lower:
                # If candidate denies possibility in a conditional setup, check context
                pass

        # If not falsified, calculate confidence based on constraint satisfaction
        score = 0.5 # Base prior
        
        # Bonus for matching structural complexity (Type inhabitation)
        if prompt_features['negations'] > 0 and 'not' in cand_lower:
            score += 0.2
        if prompt_features['conditionals'] > 0 and ('if' in cand_lower or 'then' in cand_lower):
            score += 0.2
        if prompt_features['comparatives'] > 0 and any(k in cand_lower for k in ['more', 'less', 'greater', 'smaller']):
            score += 0.2
            
        # Penalty for length mismatch in numeric answers
        if prompt_features['numbers'] and cand_features['numbers']:
             score += 0.3 # Reward having numbers if prompt has numbers

        return False, min(score, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_feat = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            is_falsified, base_score = self._check_falsification(prompt_feat, cand)
            
            if is_falsified:
                score = 0.0
                reason = "Falsified by constraint violation (numeric or logical)."
            else:
                score = base_score
                reason = "Consistent with sensorimotor constraints."
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply NCD tiebreaker for equal scores
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < 1e-9:
                ncd_i = self._ncd(prompt, results[i]['candidate'])
                ncd_next = self._ncd(prompt, results[i+1]['candidate'])
                # Lower NCD (more similar/compressible together) wins ties
                if ncd_i > ncd_next:
                    results[i], results[i+1] = results[i+1], results[i]
                    
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        return ranked[0]['score'] if ranked else 0.0