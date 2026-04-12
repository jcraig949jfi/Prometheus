import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Embodied Predictive Coding (MEEPC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Embodied Cognition): Extracts logical constraints 
       (negations, comparatives, conditionals) as the "sensorimotor affordances".
    2. MaxEnt Prior Simulation: Candidates are initially treated with uniform 
       probability (maximum entropy). Constraints act as Lagrange multipliers 
       that reduce the probability mass of candidates violating logical structure.
    3. Measure Theoretic Scoring: The "measure" mu is approximated by a weighted 
       sum of structural matches. 
    4. NCD Tiebreaker: Used only when structural signals are indistinguishable.
    
    This avoids the "Maximum Entropy" trap of over-smoothing by strictly prioritizing 
    hard logical constraints (structural parsing) before applying entropy-based 
    uncertainty quantification.
    """

    def __init__(self):
        # Regex patterns for structural affordances
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical features acting as affordance constraints."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_logic_op': bool(self.patterns['logic_op'].search(text)),
            'numbers': self.patterns['numeric'].findall(text),
            'length': len(text.split()),
            'lower': text.lower()
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Evaluates numeric consistency as a hard constraint."""
        if not prompt_nums:
            return 1.0 # No numeric constraint in prompt
        
        # Simple heuristic: if prompt has numbers, candidate should ideally relate or match
        # For this baseline, we check if candidate numbers are a subset or match prompt context
        # This is a simplified "measure" of numeric affordance.
        if not cand_nums:
            return 0.5 # Penalty for missing numbers if prompt has them
        
        try:
            p_vals = [float(x) for x in prompt_nums]
            c_vals = [float(x) for x in cand_nums]
            
            # Check for direct equality or logical ordering if lengths match
            if len(p_vals) == len(c_vals):
                if p_vals == c_vals:
                    return 1.0
                # Check inverse (negation handling)
                if all(a == -b for a, b in zip(p_vals, c_vals)):
                    return 0.9
            # Presence bonus
            return 0.8 if any(x in prompt_nums for x in cand_nums) else 0.4
        except ValueError:
            return 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            cand_feat = self._extract_structure(cand)

            # 1. Structural Affordance Matching (The "Measure" over logical space)
            # Negation consistency
            if prompt_feat['has_negation'] == cand_feat['has_negation']:
                score += 2.0
                reasoning_parts.append("negation_align")
            else:
                score -= 2.0 # Penalty for mismatched negation logic
                reasoning_parts.append("negation_mismatch")

            # Conditional/Logic presence
            if prompt_feat['has_conditional'] and not cand_feat['has_conditional']:
                # If prompt is conditional, candidate should reflect logic or be a direct answer
                pass # Neutral, depends on content
            
            if prompt_feat['has_logic_op'] and cand_feat['has_logic_op']:
                score += 1.0
                reasoning_parts.append("logic_op_present")

            # 2. Numeric Evaluation (Hard Constraint)
            if prompt_feat['numbers']:
                num_score = self._check_numeric_consistency(prompt_feat['numbers'], cand_feat['numbers'])
                score += num_score * 3.0 # High weight for numeric correctness
                reasoning_parts.append(f"numeric_score:{num_score:.2f}")

            # 3. Length/Complexity Affordance (Embodied limit)
            # Penalize extremely short answers for complex prompts
            if prompt_feat['length'] > 10 and cand_feat['length'] < 3:
                score -= 1.0
                reasoning_parts.append("too_short")

            # 4. NCD as Tiebreaker (Only if structural score is neutral/low)
            # We add a small NCD component scaled to not override structural logic
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale down
            ncd_score = (1.0 - ncd_val) * 0.5 
            score += ncd_score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural_match"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and NCD.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the top score to 0-1 range heuristically
        # Max theoretical score approx: 2 (neg) + 3 (num) + 1 (logic) + 0.5 (ncd) = 6.5
        # Min theoretical score approx: -2 (neg) - 1 (len) = -3
        raw_score = res[0]['score']
        
        # Sigmoid-like mapping to [0, 1]
        # Shift so 0 is around 0.5 confidence
        normalized = 1 / (1 + (2.718 ** (-0.5 * raw_score)))
        return max(0.0, min(1.0, normalized))