import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Gene-Regulatory Program Synthesizer (TGRPS) Approximation.
    
    Mechanism:
    1. Structural Parsing (Type Constraints): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. These act as 'hard constraints' 
       similar to dependent types in the theoretical model.
    2. GRN Dynamics (Scoring): Candidates are evaluated against these constraints.
       - Matching a constraint reinforces the candidate (activation).
       - Violating a constraint (e.g., wrong direction in a comparative) inhibits it.
       - Numeric consistency is checked via float conversion.
    3. Attractor Selection: The final score is a weighted sum of structural adherence 
       (primary) and NCD similarity to the prompt context (tiebreaker), simulating 
       the system settling into a stable, well-typed state.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Type System")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }
        self.comparative_ops = ['>', '<', '>=', '<=', 'more', 'less', 'greater', 'smaller', 'higher', 'lower']

    def _extract_features(self, text: str) -> dict:
        """Extract structural features acting as type constraints."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(n) for n in self.patterns['numbers']..findall(text)],
            'text_lower': text.lower()
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float], prompt_text: str) -> float:
        """Evaluate numeric logic (Constraint Propagation)."""
        if not prompt_nums or not cand_nums:
            return 0.0
        
        score = 0.0
        # Simple heuristic: If prompt implies ordering, check candidate ordering
        if len(prompt_nums) >= 2 and len(cand_nums) >= 2:
            p_diff = prompt_nums[-1] - prompt_nums[-2]
            c_diff = cand_nums[-1] - cand_nums[-2]
            
            if p_diff != 0 and c_diff != 0:
                # Check if direction matches (positive/negative correlation)
                if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0):
                    score += 0.5
                else:
                    score -= 0.5 # Inhibition
        
        # Exact match bonus
        if set(prompt_nums) == set(cand_nums):
            score += 0.5
            
        return score

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (Tiebreaker)."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_features(prompt)
        results = []

        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            cand_feat = self._extract_features(cand)

            # 1. Structural Constraint Checking (GRN Activation/Inhibition)
            
            # Negation Consistency
            if prompt_feat['has_negation'] == cand_feat['has_negation']:
                score += 0.3
                reasoning_parts.append("Negation structure aligned")
            else:
                score -= 0.3
                reasoning_parts.append("Negation mismatch")

            # Comparative Logic
            if prompt_feat['has_comparative']:
                if cand_feat['has_comparative']:
                    score += 0.3
                    reasoning_parts.append("Comparative logic present")
                    # Numeric consistency check
                    num_score = self._check_numeric_consistency(
                        prompt_feat['numbers'], cand_feat['numbers'], prompt
                    )
                    score += num_score
                    if num_score > 0:
                        reasoning_parts.append("Numeric trend consistent")
                    elif num_score < 0:
                        reasoning_parts.append("Numeric trend violated")
                else:
                    score -= 0.2
                    reasoning_parts.append("Missing comparative logic")

            # Conditional Logic
            if prompt_feat['has_conditional'] and cand_feat['has_conditional']:
                score += 0.2
                reasoning_parts.append("Conditional structure matched")

            # 2. NCD as Tiebreaker (Attractor Basin Depth)
            # Only applies if structural score is neutral or to break ties
            ncd_val = self._calculate_ncd(prompt_feat['text_lower'], cand_feat['text_lower'])
            # Invert NCD (lower distance = higher score) and scale lightly
            ncd_score = (1.0 - ncd_val) * 0.1 
            score += ncd_score

            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No structural features detected"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural alignment score."""
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        raw_score = res_list[0]['score']
        
        # Map raw score (approx -1.0 to 1.5) to 0.0 - 1.0
        # Baseline 0.5, +0.5 for strong match, -0.5 for strong mismatch
        conf = 0.5 + (raw_score * 0.4)
        return max(0.0, min(1.0, conf))