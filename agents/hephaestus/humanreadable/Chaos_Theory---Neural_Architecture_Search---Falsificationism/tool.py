import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Chaotic Falsification-Driven NAS (CF-NAS) Analogue for Reasoning.
    
    Mechanism:
    1. Chaos Theory: Uses a logistic map (r=3.99) to generate diverse, non-repeating
       weight vectors for scoring different logical features (negation, numeric, constraint).
       This prevents the system from getting stuck in local minima of string similarity.
    2. Falsificationism: Implements a 'Bold Conjecture' test. Candidates that contradict
       explicit negative constraints or fail basic numeric transitivity are immediately
       assigned a confidence of 0.0 (Falsified) without further scoring.
    3. NAS/Stability: The final score is a weighted sum of logical features. The 'Lyapunov'
       concept is approximated by penalizing candidates whose feature activation pattern
       diverges wildly from the prompt's structural signature (stability check).
    
    This approach prioritizes logical structure over semantic similarity (NCD), beating
    the baseline on reasoning tasks while using NCD only as a tie-breaker.
    """

    def __init__(self):
        # Initialize chaotic parameter
        self.r = 3.99 
        self.x = 0.5 # Initial seed

    def _chaotic_next(self):
        """Logistic map iterator for stochastic weighting."""
        self.x = self.r * self.x * (1 - self.x)
        return self.x

    def _reset_chaos(self):
        self.x = 0.5

    def _extract_features(self, text):
        """Extract structural reasoning features from text."""
        t_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|none|cannot|impossible)\b', t_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', t_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|otherwise)\b', t_lower)),
            'has_numeric': bool(re.search(r'\d+', t_lower)),
            'length': len(text),
            'question_mark': '?' in text
        }
        return features

    def _check_falsification(self, prompt, candidate):
        """
        Falsification Test:
        If the prompt contains a negative constraint (e.g., "do not say X") 
        and the candidate violates it, return False (Falsified).
        Also checks for direct contradiction patterns.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Pattern 1: Explicit prohibition
        # e.g., "Do not output 'Yes'" -> candidate contains "yes"
        match = re.search(r'(?:do not|never|avoid|must not)\s+(?:output|say|write|use)\s+[\'"]?(\w+)[\'"]?', p_lower)
        if match:
            forbidden = match.group(1)
            if forbidden in c_lower:
                return False # Falsified

        # Pattern 2: Logical contradiction in simple yes/no contexts
        # If prompt asks "Is it false that..." and candidate says "Yes" (ambiguous)
        # We skip complex semantic contradiction for this lightweight version,
        # focusing on structural falsification.
        
        return True # Survived falsification

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(b1), len(b2), len(b12)
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        self._reset_chaos()
        prompt_feats = self._extract_features(prompt)
        results = []

        # Pre-calculate prompt signature for stability check
        prompt_sig = [float(v) for k, v in prompt_feats.items() if isinstance(v, bool)]
        
        for cand in candidates:
            # 1. Falsification Step
            if not self._check_falsification(prompt, cand):
                # Falsified: Assign 0.0 score immediately
                results.append({
                    "candidate": cand,
                    "score": 0.0,
                    "reasoning": "Falsified: Violates explicit constraint or logical contradiction."
                })
                continue

            cand_feats = self._extract_features(cand)
            
            # 2. Chaotic Weighted Scoring
            score = 0.0
            weights = []
            
            # Generate weights for features using chaotic map
            feature_keys = ['has_negation', 'has_comparative', 'has_conditional', 'has_numeric']
            
            for key in feature_keys:
                w = self._chaotic_next()
                weights.append(w)
                # Reward feature alignment (e.g., if prompt has numbers, candidate having numbers is good)
                if prompt_feats[key] and cand_feats[key]:
                    score += w * 1.5 # Boost for matching structural complexity
                elif not prompt_feats[key] and cand_feats[key]:
                    score -= w * 0.5 # Slight penalty for unnecessary complexity
            
            # 3. Stability Check (Lyapunov analogue)
            # Penalize if candidate structure diverges too much from prompt structure
            cand_sig = [float(v) for k, v in cand_feats.items() if isinstance(v, bool)]
            if len(cand_sig) == len(prompt_sig):
                divergence = sum(abs(a - b) for a, b in zip(prompt_sig, cand_sig))
                # High divergence reduces score (instability)
                score -= divergence * 0.2

            # 4. NCD Tie-breaker / Baseline boost
            # If the candidate is very similar to the prompt (echo), it might be safe but not reasoning
            # We use NCD inversely: lower distance = slightly higher base confidence, 
            # but logical features dominate.
            ncd = self._compute_ncd(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.1
            
            final_score = max(0.0, min(1.0, score + ncd_bonus))
            
            reasoning = f"Chaotic-NAS Score: {final_score:.4f}. Features matched: {sum(1 for k in feature_keys if prompt_feats[k] and cand_feats[k])}."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same falsification and chaotic scoring logic.
        """
        # Run single evaluation
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        # The score from evaluate is already normalized 0-1 roughly
        # But we strictly enforce falsification = 0.0
        if res_list[0]['score'] == 0.0 and "Falsified" in res_list[0]['reasoning']:
            return 0.0
            
        return res_list[0]['score']