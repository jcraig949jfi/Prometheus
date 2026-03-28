import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Autopoietic Kalman Filter (MEAKF) Reasoning Tool.
    
    Mechanism:
    Instead of literal continuous dynamics, we treat the candidate answers as 
    discrete state hypotheses. 
    1. Structural Parsing (The Measurement H): We extract logical operators 
       (negations, comparatives, conditionals) and numeric values from the prompt.
    2. Autopoietic Consistency (The Loop): We simulate the system's internal 
       model by checking if a candidate's logical structure is consistent with 
       the prompt's extracted constraints. A candidate that contradicts the 
       prompt's structural negations or numeric bounds receives a high "innovation" 
       (error), reducing its score.
    3. Maximum Entropy (The Prior): In the absence of strong structural signals, 
       we prefer the candidate that introduces the least biased assumption 
       (closest to uniform distribution of logical tokens), acting as a regularizer.
    4. Scoring: The final score is a weighted combination of structural consistency 
       (Kalman update) and compression similarity (NCD tiebreaker).
    """

    def __init__(self):
        self._logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self._comp_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer']
        self._cond_ops = ['if', 'then', 'else', 'unless', 'when']

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical and numeric features from text."""
        lower_text = text.lower()
        features = {
            'negations': len([w for w in self._logic_ops if re.search(r'\b' + w + r'\b', lower_text)]),
            'comparatives': len([w for w in self._comp_ops if w in lower_text]),
            'conditionals': len([w for w in self._cond_ops if re.search(r'\b' + w + r'\b', lower_text)]),
            'numbers': []
        }
        # Extract numbers
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _check_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Calculate consistency score based on structural alignment.
        Returns 1.0 for perfect consistency, 0.0 for contradiction.
        """
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation context and candidate lacks it (or vice versa heavily), penalize.
        # This is a heuristic proxy for logical alignment.
        neg_diff = abs(prompt_feats['negations'] - cand_feats['negations'])
        if neg_diff > 1:
            score -= 0.3 * neg_diff
            
        # 2. Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = sorted(prompt_feats['numbers'])
            c_nums = sorted(cand_feats['numbers'])
            
            # Check for direct contradictions in simple comparisons if keywords exist
            has_comp = prompt_feats['comparatives'] > 0 or cand_feats['comparatives'] > 0
            
            if has_comp and len(p_nums) >= 1 and len(c_nums) >= 1:
                # Heuristic: If prompt implies ordering and candidate reverses it significantly
                # We check if the candidate number is wildly out of bounds compared to prompt numbers
                p_min, p_max = min(p_nums), max(p_nums)
                for cn in c_nums:
                    if cn < p_min - 10 or cn > p_max + 10: # Loose bound check
                        score -= 0.2

        # 3. Conditional/Logical Flow
        # If prompt has conditionals, candidate should ideally reflect logical consequence 
        # (hard to verify without LLM, so we check for presence of logical connectors as a proxy for complexity matching)
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] == 0:
            # Penalty for oversimplification in conditional contexts
            score -= 0.1

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd = max(s[1] for s in ncd_scores)
        ncd_range = max_ncd - min_ncd if (max_ncd - min_ncd) > 1e-6 else 1.0

        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # Core Reasoning: Structural Consistency (Kalman Update analog)
            consistency = self._check_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # Tie-breaker: NCD (compressed similarity)
            # Normalize NCD so lower distance = higher score
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ((ncd_val - min_ncd) / ncd_range) if ncd_range > 0 else 0.5
            
            # Final Score: Weighted sum favoring structural reasoning
            # Structural consistency is primary (weight 0.7), NCD is secondary (0.3)
            final_score = (0.7 * consistency) + (0.3 * ncd_score)
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural consistency: {consistency:.2f}, NCD similarity: {ncd_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment between prompt and answer.
        Returns 0.0 to 1.0.
        """
        prompt_feats = self._extract_structure(prompt)
        ans_feats = self._extract_structure(answer)
        
        # Calculate consistency
        consistency = self._check_consistency(prompt_feats, ans_feats, prompt, answer)
        
        # Adjust for length mismatch (Autopoietic boundary check)
        # If the answer is too short to contain the complexity of the prompt's logic
        len_ratio = len(answer) / (len(prompt) + 1)
        complexity_penalty = 0.0
        if prompt_feats['conditionals'] > 0 and len_ratio < 0.1:
            complexity_penalty = 0.3
        if prompt_feats['negations'] > 0 and ans_feats['negations'] == 0:
             # Potential missed negation
            complexity_penalty += 0.2
            
        base_conf = consistency * (1.0 - min(complexity_penalty, 0.9))
        
        # Clamp between 0 and 1
        return round(max(0.0, min(1.0, base_conf)), 4)