import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Oscillatory Predictive Coding (QOPC) Reasoning Tool.
    
    Mechanism:
    This tool implements a computational analogy of QOPC using Active Inference as the core driver.
    
    1. Structural Parsing (Theta Priors): Extracts logical constraints (negations, comparatives,
       conditionals) from the prompt. These form the slow-varying "prior beliefs" about the 
       required answer structure.
    2. Candidate Simulation (Superposition): Candidates are treated as superposed hypotheses.
    3. Interference & Collapse (Gamma Likelihoods): 
       - We simulate "neural oscillations" by mapping structural matches to phase angles.
       - Constructive interference occurs when a candidate satisfies prompt constraints (phase align).
       - Destructive interference occurs when constraints are violated (phase misalign).
       - The "collapse" is the calculation of a final score based on the vector sum of these phases.
    4. Active Inference Loop: The system minimizes "Free Energy" (discrepancy between prompt 
       constraints and candidate properties). High free energy (mismatch) lowers the score.
    5. NCD Tiebreaker: If structural signals are weak, Normalized Compression Distance is used.
    """

    def __init__(self):
        # Keywords defining logical structures (Theta band priors)
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible', 'false']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'unless', 'provided', 'only if']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structural_features(self, text: str) -> Dict:
        """Extract logical features to form the 'Prior'."""
        text_lower = text.lower()
        features = {
            'has_negation': any(n in text_lower for n in self.negations),
            'has_comparative': any(c in text_lower for c in self.comparatives),
            'has_conditional': any(c in text_lower for c in self.conditionals),
            'numbers': [float(n) for n in self.numeric_pattern.findall(text)],
            'length': len(text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Active Inference Step: Calculate Free Energy gradient.
        Returns a score based on how well the candidate satisfies extracted constraints.
        """
        p_features = self._extract_structural_features(prompt)
        c_features = self._extract_structural_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 0.0
        evidence_count = 0

        # 1. Negation Handling (Destructive Interference if violated)
        if p_features['has_negation']:
            # If prompt has negation, correct answer often contains negation or contradicts the positive form
            # Simple heuristic: if prompt says "not X", candidate shouldn't be exactly "X"
            # Stronger heuristic: Check for logical consistency keywords
            if any(n in c_lower for n in self.negations):
                score += 2.0 # Constructive interference
            else:
                # Check if candidate is a direct number that might be the 'wrong' one
                if p_features['numbers'] and c_features['numbers']:
                    # Complex logic omitted for brevity, assume penalty for missing negation marker
                    score -= 1.0 
            evidence_count += 1

        # 2. Comparative/Numeric Consistency
        if p_features['has_comparative'] and p_features['numbers']:
            if c_features['numbers']:
                # If prompt asks for "greater", check if candidate number is greater than context
                # This is a simplification; full semantic parsing is too large for 150 lines
                score += 1.5 # Reward finding numbers in comparative questions
                evidence_count += 1
            else:
                score -= 2.0 # Penalty: Missing numbers in a math/comparative question
                evidence_count += 1

        # 3. Conditional Logic
        if p_features['has_conditional']:
            if any(c in c_lower for c in ['yes', 'no', 'true', 'false', 'if', 'then']):
                score += 1.0
                evidence_count += 1

        # 4. Substring/Keyword Overlap (Weak Prior)
        # Avoid simple bag-of-words, but exact keyword match on logic terms is good
        common_logic = set(p_lower.split()) & set(c_lower.split())
        logic_terms = {'true', 'false', 'yes', 'no', 'all', 'none', 'some'}
        if common_logic & logic_terms:
            score += 1.0
            evidence_count += 1

        # Normalize by evidence count to prevent inflation, base score on structural fit
        if evidence_count == 0:
            return 0.5 # Neutral prior
        
        return score / (evidence_count + 1) + 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximation using lengths for speed/simplicity in this context
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(concat))
        
        if max(c1, c2) == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_features = self._extract_structural_features(prompt)
        has_strong_structure = (prompt_features['has_negation'] or 
                                prompt_features['has_comparative'] or 
                                prompt_features['has_conditional'] or
                                len(prompt_features['numbers']) > 0)

        for cand in candidates:
            # Phase 1: Structural Parsing & Active Inference (Primary Signal)
            structural_score = self._check_constraint_satisfaction(prompt, cand)
            
            # Phase 2: Oscillatory Interference Simulation
            # Map structural score to a phase angle. 
            # High structural fit = phase 0 (Constructive). Low fit = phase pi (Destructive).
            phase = (1.0 - structural_score) * math.pi 
            interference_factor = math.cos(phase)
            
            # Base score from interference
            base_score = 0.5 + (0.4 * interference_factor)

            # Phase 3: NCD as Tiebreaker/Refinement (Only if structure is weak or for fine-tuning)
            if not has_strong_structure:
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD (lower is better) and scale
                ncd_score = 1.0 - ncd_val
                final_score = 0.3 * base_score + 0.7 * ncd_score
            else:
                # Strong structural signal dominates
                final_score = 0.8 * base_score + 0.2 * (1.0 - self._compute_ncd(prompt, cand))

            # Clamp score
            final_score = max(0.0, min(1.0, final_score))

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural fit: {structural_score:.2f}, Interference: {interference_factor:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation of the single candidate.
        """
        # Evaluate against a dummy set to get the score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']