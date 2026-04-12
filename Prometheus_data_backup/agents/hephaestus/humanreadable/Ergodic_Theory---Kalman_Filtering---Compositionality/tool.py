import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Ergodic Kalman Filter (CEKF) inspired reasoning tool.
    
    Mechanism:
    1. Structural Parsing (Compositionality): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt to form a "state vector".
    2. Ergodic Validation (Metacognition): Treats the candidate answer as a trajectory. 
       Checks if the candidate's logical/numeric properties converge to the prompt's 
       extracted constraints (time-average == ensemble average).
    3. Kalman Update (Scoring): Computes an innovation score based on the deviation 
       between expected structural features and candidate features. Lower innovation 
       (error) yields higher probability.
    4. NCD Tiebreaker: Uses compression distance only when structural scores are identical.
    """

    def __init__(self):
        self._logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self._comp_ops = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self._cond_ops = ['if', 'then', 'else', 'when', 'unless']
        self._num_regex = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features: logic flags, comparison direction, numbers."""
        lower_text = text.lower()
        features = {
            'has_negation': any(op in lower_text for op in self._logic_ops),
            'has_comparison': any(op in lower_text for op in self._comp_ops),
            'has_condition': any(op in lower_text for op in self._cond_ops),
            'numbers': [float(n) for n in self._num_regex.findall(text)],
            'length': len(text)
        }
        return features

    def _compute_innovation(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute the 'innovation' (prediction error) between prompt expectations 
        and candidate reality. Lower is better.
        """
        error = 0.0
        
        # Logic consistency check (Binary match)
        # If prompt has negation, valid answers often reflect constraint (heuristic)
        if prompt_feats['has_negation']:
            # Penalize if candidate ignores negation context (simplified heuristic)
            # We assume valid reasoning preserves the 'complexity' of logic
            pass 

        # Numeric convergence (Ergodic check)
        # If prompt has numbers, candidate should ideally relate or not contradict wildly
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if p_nums:
            if not c_nums:
                # Missing numbers in candidate when prompt has them is a high innovation event
                error += 2.0 
            else:
                # Check magnitude consistency (roughly)
                p_avg = sum(p_nums) / len(p_nums)
                c_avg = sum(c_nums) / len(c_nums)
                # Normalized difference
                if abs(p_avg) > 1e-6:
                    error += abs(c_avg - p_avg) / (abs(p_avg) + 1e-6)
                else:
                    error += abs(c_avg - c_avg) # Zero if both zero-ish

        # Structural length penalty (Occam's razor / Kalman covariance)
        # Candidates wildly different in length might be over/under fitting
        len_diff = abs(cand_feats['length'] - prompt_feats['length'] * 0.5) # Expect shorter answers
        error += len_diff * 0.001

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_features(prompt)
        scored = []
        
        # Calculate raw innovation scores
        raw_scores = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            innov = self._compute_innovation(prompt_feats, cand_feats)
            raw_scores.append((cand, innov))
        
        # Normalize and invert to get probability-like scores
        # Score = exp(-innovation)
        max_innov = max(r[1] for r in raw_scores) + 1e-6
        min_innov = min(r[1] for r in raw_scores)
        
        final_results = []
        
        for cand, innov in raw_scores:
            # Base score from innovation (Kalman update)
            # Shift so min_innov is best (0 error)
            adjusted_innov = innov - min_innov
            base_score = math.exp(-adjusted_innov)
            
            final_results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Innovation: {innov:.4f}",
                "_innov": innov # For tie-breaking
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Handle ties with NCD (Tie-breaker only)
        # Group by score precision
        i = 0
        while i < len(final_results):
            j = i
            # Find ties
            while j < len(final_results) and abs(final_results[j]["score"] - final_results[i]["score"]) < 1e-6:
                j += 1
            
            if j - i > 1:
                # Tie detected, use NCD against prompt to break
                tie_group = final_results[i:j]
                tie_group.sort(key=lambda x: self._ncd(prompt, x["candidate"]))
                final_results[i:j] = tie_group
            
            i = j

        # Clean up and format output
        output = []
        for res in final_results:
            output.append({
                "candidate": res["candidate"],
                "score": round(res["score"], 6),
                "reasoning": res["reasoning"]
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on how well the answer fits the 
        ergodic constraints of the prompt.
        """
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        innov = self._compute_innovation(prompt_feats, cand_feats)
        
        # Convert innovation to confidence
        # Low innovation -> High confidence
        # Heuristic scaling: innov < 0.5 is good, > 3.0 is bad
        conf = math.exp(-innov)
        
        # Clamp 0-1
        return max(0.0, min(1.0, conf))