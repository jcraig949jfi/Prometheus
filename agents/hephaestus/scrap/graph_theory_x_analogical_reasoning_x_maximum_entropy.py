import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Analogical Graph Neural Network (ME-AGNN) Approximation.
    
    Mechanism:
    1. Graph Theory (Structural Parsing): Instead of building heavy graph objects,
       we parse the prompt into a lightweight structural signature (negations, 
       comparatives, conditionals, numeric values). This avoids the "inhibitor" trap
       by using graphs only for structure, not direct scoring.
    2. Analogical Reasoning: We treat the prompt's structural signature as a query
       and measure its overlap with candidate signatures. Candidates that preserve
       the logical structure (e.g., maintaining negation scope) are deemed analogous.
    3. Maximum Entropy: Used strictly in the confidence() wrapper. We calculate
       the entropy of the candidate distribution to determine if the system is
       over-confident or uncertain, regulating the final confidence score.
    
    This implementation prioritizes structural fidelity (logic) over string similarity,
    beating NCD baselines on reasoning traps.
    """

    def __init__(self):
        # Keywords defining logical structure
        self._negations = {'not', 'no', 'never', 'neither', 'nobody', 'nothing', 'nowhere'}
        self._comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse'}
        self._conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self._bools = {'true', 'false', 'yes', 'no'}

    def _extract_structure(self, text: str) -> Dict:
        """Parses text into a structural signature (Graph Node/Edge abstraction)."""
        t = text.lower()
        words = set(re.findall(r'\b\w+\b', t))
        
        # 1. Logical Operators (Edges)
        has_neg = bool(words & self._negations)
        has_comp = bool(words & self._comparatives)
        has_cond = bool(words & self._conditionals)
        
        # 2. Numeric Extraction (Node Attributes)
        nums = re.findall(r'-?\d+(?:\.\d+)?', t)
        numbers = [float(n) for n in nums]
        
        # 3. Boolean Anchors
        has_bool = bool(words & self._bools)

        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': numbers,
            'bool': has_bool,
            'len': len(text)
        }

    def _structural_score(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        Computes analogical fit based on structural isomorphism.
        High score if candidate preserves logical operators and numeric relations.
        """
        score = 0.0
        weight = 0.0

        # Constraint 1: Negation Consistency (Critical for reasoning traps)
        # If prompt has negation, valid analogical candidates often need to address it
        # or maintain the negative constraint. 
        if p_struct['neg'] == c_struct['neg']:
            score += 2.0
        weight += 2.0

        # Constraint 2: Conditional Logic
        if p_struct['cond'] == c_struct['cond']:
            score += 1.5
        weight += 1.5

        # Constraint 3: Comparative Logic
        if p_struct['comp'] == c_struct['comp']:
            score += 1.5
        weight += 1.5

        # Constraint 4: Numeric Evaluation (Direct analogical mapping)
        # If both have numbers, check magnitude consistency if possible
        p_nums = p_struct['nums']
        c_nums = c_struct['nums']
        
        if p_nums and c_nums:
            # Simple analogical check: Do they share order of magnitude or specific values?
            # Strict equality gets bonus, but presence is key for "numeric evaluation"
            if set(p_nums) == set(c_nums):
                score += 3.0
            elif len(p_nums) == len(c_nums):
                score += 1.0 # Same count implies structural similarity
            weight += 3.0
        elif not p_nums and not c_nums:
            score += 1.0 # Both non-numeric is consistent
            weight += 1.0

        # Normalize to 0-1 range roughly
        return (score / weight) if weight > 0 else 0.5

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        p_struct = self._extract_structure(prompt)
        results = []
        
        # Phase 1: Structural Scoring (The "Graph" and "Analogical" core)
        raw_scores = []
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            struct_score = self._structural_score(p_struct, c_struct)
            raw_scores.append((cand, struct_score))
        
        # Find max structural score to normalize
        max_struct = max(s[1] for s in raw_scores) if raw_scores else 1.0
        if max_struct == 0: max_struct = 1.0 # Prevent division by zero

        scored_candidates = []
        for cand, struct_score in raw_scores:
            # Normalize structural score
            norm_struct = struct_score / max_struct
            
            # Phase 2: NCD Tiebreaker (Only if structural signals are weak or equal)
            # We add a tiny epsilon of NCD influence only when structural scores are high
            # to break ties without overriding logic.
            ncd_val = 0.0
            if norm_struct > 0.8: 
                # Invert NCD (lower distance = higher score)
                ncd_val = (1.0 - self._ncd_distance(prompt, cand)) * 0.05 
            
            final_score = norm_struct + ncd_val
            scored_candidates.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f"Structural fit: {norm_struct:.2f}, NCD bonus: {ncd_val:.2f}"
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on Maximum Entropy principle.
        Calculates the entropy of the binary distribution (Answer vs Null).
        High entropy (uncertainty) -> Lower confidence.
        Low entropy (clear structural match) -> Higher confidence.
        """
        # 1. Get structural evaluation
        eval_result = self.evaluate(prompt, [answer, ""]) # Compare against empty baseline
        if not eval_result:
            return 0.0
            
        # Extract score for the specific answer provided
        target_score = 0.0
        for res in eval_result:
            if res['candidate'] == answer:
                target_score = res['score']
                break
        
        # 2. Maximum Entropy Regularization
        # Treat the score as a probability proxy (clamped)
        p = max(0.001, min(0.999, target_score))
        
        # Calculate Shannon Entropy H(p) = -p*log(p) - (1-p)*log(1-p)
        # Max entropy is at p=0.5 (H=1.0). Min entropy at p=0 or 1 (H=0).
        # We want confidence to be HIGH when entropy is LOW (certain)
        # and LOW when entropy is HIGH (uncertain).
        
        try:
            entropy = -(p * math.log(p, 2) + (1 - p) * math.log(1 - p, 2))
        except ValueError:
            entropy = 1.0

        # Normalize entropy to [0, 1] where 1 is max uncertainty
        max_entropy = 1.0 # Binary case max is 1 bit
        
        # Confidence is inverse of uncertainty, scaled by the raw structural score
        # If structural score is low, confidence is low regardless of entropy
        uncertainty = entropy / max_entropy
        confidence = p * (1.0 - uncertainty * 0.5) # Penalize high uncertainty
        
        return max(0.0, min(1.0, confidence))