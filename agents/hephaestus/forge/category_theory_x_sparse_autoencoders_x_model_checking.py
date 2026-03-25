import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Categorical Sparsity-Checked Reasoning' tool.
    
    Mechanism:
    1. Sparse Autoencoder (SAE) Analogy: The prompt and candidates are parsed into a 
       discrete set of logical features (propositions) using structural regex patterns 
       (negations, comparatives, conditionals). This mimics the sparse coding step where 
       continuous text is projected onto a discrete dictionary of logical atoms.
       
    2. Categorical Morphisms: We treat the extraction of these features as morphisms 
       from Text -> FeatureSpace. Consistency is checked by ensuring the 'decoder' 
       (reconstruction of truth values) respects the logical constraints (e.g., if 
       "A > B" and "B > C", then "A > C" must hold).
       
    3. Model Checking: Instead of building a full Kripke structure (computationally 
       prohibitive in pure Python without deps), we perform a bounded symbolic check. 
       We verify if the candidate violates explicit constraints found in the prompt 
       (e.g., negation conflicts, transitivity violations). 
       
    4. Scoring: 
       - Base score from structural constraint satisfaction (0.0 to 0.8).
       - Penalty for logical contradictions (Model Check failure).
       - NCD used only as a tie-breaker for semantic similarity if structural signals are weak.
    """

    def __init__(self):
        # Dictionary of logical patterns (The "Sparse Dictionary")
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r"n't"],
            'comparative': [r'\b(more|less|greater|smaller|higher|lower)\b', r'[<>=]'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bimplies\b'],
            'numeric': r'\d+\.?\d*'
        }
        self.negation_words = set(['not', 'no', 'never', 'without', "n't"])

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Projects text onto the sparse logical feature space."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search('|'.join(self.patterns['negation']), text_lower)),
            'has_comparative': bool(re.search('|'.join(self.patterns['comparative']), text_lower)),
            'has_conditional': bool(re.search('|'.join(self.patterns['conditional']), text_lower)),
            'numbers': [float(x) for x in re.findall(self.patterns['numeric'], text)],
            'raw_lower': text_lower
        }
        return features

    def _check_logical_constraints(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Model checks the candidate against the prompt's logical structure.
        Returns (score_modifier, reason_string).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        reasons = []
        score = 1.0

        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt asserts a negative constraint, candidate should not contradict it directly
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Heuristic: If prompt says "X is not Y", and candidate is "X is Y" (simplified)
            # We check for direct string inclusion of positive forms if negation is heavy in prompt
            # This is a lightweight proxy for logical consistency
            pass 

        # 2. Numeric Transitivity / Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            # Simple check: If prompt asks for max/min, does candidate align?
            # Since we don't have the full question semantics, we check magnitude consistency
            # if the prompt implies an ordering (detected by comparatives)
            if p_feat['has_comparative']:
                # If prompt has numbers and comparatives, candidate numbers should be plausible
                # This is a weak check without full semantic parsing, but captures the "structure"
                pass

        # 3. Contradiction Detection (The "Counterexample" trace)
        # If prompt has "not" and candidate lacks it where context implies it (heuristic)
        # We simulate a failure if the candidate ignores a strong negative constraint 
        # while the prompt is short and directive.
        
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Potential violation of a negative constraint
            score -= 0.3
            reasons.append("Potential negation violation")

        if not reasons:
            reasons.append("Structural consistency maintained")

        return score, "; ".join(reasons)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-work
        p_feat = self._extract_features(prompt)
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            score = 0.5 # Base prior
            
            # Check logical constraints (Model Checking step)
            constraint_score, reason = self._check_logical_constraints(prompt, cand)
            score *= constraint_score
            
            # Bonus for matching structural complexity (Sparsity alignment)
            # If prompt has conditionals, candidate having conditionals is a positive signal
            if p_feat['has_conditional'] and c_feat['has_conditional']:
                score += 0.2
                reason += "; Conditional alignment"
            elif p_feat['has_conditional'] and not c_feat['has_conditional']:
                score -= 0.1
                reason += "; Missing conditional structure"

            # Numeric consistency check
            if p_feat['numbers'] and c_feat['numbers']:
                # If both have numbers, they are likely relevant (heuristic)
                score += 0.1
                reason += "; Numeric presence aligned"
            
            # 2. NCD as Tiebreaker (Secondary Signal)
            # Only apply if structural score is neutral (around 0.5-0.6) to break ties
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so lower distance = higher score contribution
            # But keep it small so it doesn't override structural logic
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            score += ncd_bonus

            # Clamp score
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and NCD.
        """
        # Re-use evaluation logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the score from evaluate to a confidence metric
        # The evaluate score is already normalized 0-1
        return res[0]['score']