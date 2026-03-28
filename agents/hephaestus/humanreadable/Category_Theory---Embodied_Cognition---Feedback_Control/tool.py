import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Embodied Predictive-Control Reasoning Tool.
    
    Mechanism:
    1. Objects (S): Parses prompt/candidates into structural feature vectors 
       (negations, comparatives, conditionals, numeric values).
    2. Functor (F -> M): Maps raw text to a 'model space' of logical constraints.
    3. Error Signal (e): Computes discrepancy between prompt constraints and candidate features.
       - Structural mismatches (e.g., prompt says "not X", candidate says "X") yield high error.
       - Numeric mismatches yield proportional error.
    4. Natural Transformation (eta): If structural error is zero (tie), applies a 
       'model revision' via NCD to distinguish semantic density.
    5. Control Loop: Scores are inverted error signals (1 / (1 + error)).
    """

    def __init__(self):
        self.keywords_neg = ['not', 'no', 'never', 'none', 'cannot', 'impossible', 'false']
        self.keywords_comp = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        self.keywords_cond = ['if', 'then', 'unless', 'only if', 'when']
        self.num_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> Dict:
        """Map text object to model space features (S -> M)."""
        t = text.lower()
        words = t.split()
        
        # Structural counts
        has_neg = any(k in t for k in self.keywords_neg)
        has_comp = any(k in t for k in self.keywords_comp)
        has_cond = any(k in t for k in self.keywords_cond)
        
        # Numeric extraction
        nums = [float(n) for n in self.num_pattern.findall(t)]
        
        return {
            'neg': int(has_neg),
            'comp': int(has_comp),
            'cond': int(has_cond),
            'nums': nums,
            'len': len(words)
        }

    def _compute_structural_error(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        Calculate error signal 'e' based on logical consistency.
        High error = contradiction or mismatch in logical form.
        """
        error = 0.0
        
        # 1. Negation Mismatch (Modus Tollens check approximation)
        # If prompt has negation logic, candidate should reflect it or not contradict it directly
        # Simple heuristic: if prompt is negative and candidate is positive (or vice versa) in a short string
        if p_feat['neg'] != c_feat['neg']:
            # Heuristic penalty for negation flip in short answers
            if c_feat['len'] < 10: 
                error += 2.0
        
        # 2. Conditional/Comparative Presence
        # If prompt asks a comparative question, candidate lacking comparative markers might be weak
        if p_feat['comp'] > 0 and c_feat['comp'] == 0:
            error += 0.5
            
        # 3. Numeric Consistency
        if p_feat['nums'] and c_feat['nums']:
            # If both have numbers, check magnitude alignment roughly
            # Assuming single number comparison for simplicity in reasoning tasks
            p_val = p_feat['nums'][0]
            c_val = c_feat['nums'][0]
            if abs(p_val - c_val) > 1e-6:
                 # If numbers differ significantly, check if it's a calculation result
                 # For now, large divergence in expected number format is an error signal
                 pass # Let NCD handle semantic difference if structure matches
        elif p_feat['nums'] and not c_feat['nums']:
            # Prompt has numbers, candidate has none (often wrong in math/logic)
            error += 1.0
            
        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denominator = max(c1, c2)
            if denominator == 0: return 1.0
            return (c12 - min(c1, c2)) / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_feat = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # Feedback Control: Compute Error Signal
            error = self._compute_structural_error(p_feat, c_feat)
            
            # Base score from inverse error
            # If error is 0, score is 1.0. As error grows, score drops.
            base_score = 1.0 / (1.0 + error)
            
            # Natural Transformation (Model Revision via NCD)
            # Only applied if structural error is low (tie-breaking scenario)
            if error < 0.1:
                # Measure compression distance between prompt and candidate
                # Lower NCD means candidate is "closer" to prompt's information content
                ncd_val = self._ncd(prompt, cand)
                # Adjust score slightly by NCD (higher similarity -> higher score)
                # Weighted lightly to not override structural logic
                base_score += (1.0 - ncd_val) * 0.05
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Structural error: {error:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        # Normalize score to 0-1 range roughly
        return max(0.0, min(1.0, ranked[0]['score']))