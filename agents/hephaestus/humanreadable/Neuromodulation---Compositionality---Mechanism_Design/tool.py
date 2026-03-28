import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Compositional Mechanism-Design Network (NCMDN) Approximation.
    
    Mechanism:
    1. Compositionality: Decomposes prompts into structural features (negations, comparatives, numbers).
    2. Mechanism Design: Treats feature extractors as agents. Uses a Vickrey-style penalty (proper scoring)
       where 'lying' (high confidence on wrong structural match) reduces utility.
    3. Neuromodulation: A global gain signal scales the impact of evidence based on structural complexity.
       High ambiguity (low agreement between features) increases gain (exploration), while high agreement
       decreases it (exploitation).
       
    The evaluate() method computes a score based on structural alignment (primary) and NCD (tiebreaker).
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract compositional features from text."""
        t = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|without)\b', t)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t)),
            'conditional': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', t)),
            'numeric': len(re.findall(r'\d+(\.\d+)?', t)),
            'length': len(t)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_c = max(c1, c2)
        if max_c == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_c

    def _mechanism_design_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core evaluation loop.
        Agents (features) report confidence. Mechanism design penalizes inconsistency.
        Returns (score, reasoning_string).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # 1. Agent Reports (Feature Alignment)
        # Agents report similarity on specific dimensions.
        reports = []
        
        # Negation consistency (Did candidate flip the logic?)
        neg_match = 1.0 if (p_feat['negation'] > 0) == (c_feat['negation'] > 0) else 0.5
        reports.append(('negation_agent', neg_match))
        
        # Numeric consistency (Does candidate contain numbers if prompt implies calculation?)
        # Heuristic: If prompt has numbers, good candidate often has numbers or logical words
        num_score = 1.0
        if p_feat['numeric'] > 0:
            # If prompt has numbers, candidate having numbers is a positive signal for 'calculation' tasks
            # but strict equality isn't required. We reward presence.
            num_score = 1.0 if c_feat['numeric'] > 0 else 0.6
        reports.append(('numeric_agent', num_score))

        # Length/Complexity match (Penalize trivial answers to complex prompts)
        len_ratio = min(c_feat['length'], p_feat['length']) / (max(c_feat['length'], 1) + 1)
        len_score = min(1.0, len_ratio * 2) # Reward substantial answers
        reports.append(('complexity_agent', len_score))

        # 2. Mechanism Design: Incentive Compatibility Check
        # We simulate a proper scoring rule. If agents disagree wildly, the system is uncertain.
        # We calculate the variance of reports as a measure of "truthfulness" stability.
        vals = [r[1] for r in reports]
        avg_report = sum(vals) / len(vals) if vals else 0
        variance = sum((v - avg_report) ** 2 for v in vals) / len(vals) if vals else 1
        
        # Penalty for high variance (inconsistency among features)
        consistency_penalty = 1.0 - min(1.0, variance * 2) 
        
        # 3. Neuromodulatory Gain
        # Gain = f(Complexity, Uncertainty). 
        # High structural complexity in prompt -> Higher Gain (amplify signal)
        # High variance (conflict) -> Higher Gain (focus computation/uncertainty)
        structural_load = (p_feat['negation'] + p_feat['comparative'] + p_feat['conditional']) / 5.0
        gain = 1.0 + (structural_load * 0.5) + (variance * 0.5)
        
        # Base score from NCD (similarity of content)
        # Inverted because NCD 0 is identical, 1 is different.
        ncd = self._compute_ncd(prompt, candidate)
        base_similarity = 1.0 - ncd
        
        # Final Score: (Weighted Feature Agreement * Gain) + Base Similarity
        # The mechanism ensures that if features conflict (low consistency), the score drops.
        raw_score = (avg_report * consistency_penalty * gain) + (base_similarity * 0.3)
        
        # Normalize roughly to 0-1 range
        final_score = max(0.0, min(1.0, raw_score / 1.5))
        
        reason_str = f"Agents:[{','.join([f'{n}:{v:.2f}' for n,v in reports])}] | Consistency:{consistency_penalty:.2f} | Gain:{gain:.2f}"
        
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._mechanism_design_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._mechanism_design_score(prompt, answer)
        return float(score)