import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Equilibrium Model-Checking Loop Implementation.
    
    Mechanism:
    1. Structural Parsing (Model Checking): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt.
    2. Equilibrium Solver (Nash): Evaluates candidates against these constraints. 
       Candidates violating hard logical constraints (e.g., negation flips) are 
       assigned low probability (destabilized).
    3. Phase Transition Detection: Monitors the 'order parameter' (constraint satisfaction ratio).
       If a candidate barely satisfies constraints (high susceptibility), it is flagged.
       The scoring function applies a non-linear penalty near the critical threshold 
       to simulate the 'jump' in strategic landscape, prioritizing robust answers.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.negation_patterns = [
            r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bunless\b', r'\bcannot\b'
        ]
        self.comparative_ops = [r'>', r'<', r'more than', r'less than', r'greater', r'smaller']
        self.conditional_keywords = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', r'\bprovided\b']
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical components: negations, numbers, conditionals."""
        text_lower = text.lower()
        
        # Count negations
        neg_count = sum(len(re.findall(p, text_lower)) for p in self.negation_patterns)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(self.number_pattern, text)]
        
        # Detect conditionals
        has_conditional = any(re.search(p, text_lower) for p in self.conditional_keywords)
        
        # Detect comparatives
        has_comparative = any(re.search(p, text_lower) for p in self.comparative_ops)
        
        return {
            'neg_count': neg_count,
            'numbers': numbers,
            'has_conditional': has_conditional,
            'has_comparative': has_comparative,
            'length': len(text)
        }

    def _check_constraint_violation(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Nash Equilibrium Check: 
        Determine if the candidate strategy is stable against the prompt's logical constraints.
        Returns a penalty score (0.0 = perfect equilibrium, 1.0 = total violation).
        """
        candidate_lower = candidate.lower()
        penalty = 0.0
        
        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt has high negation density, candidate should ideally reflect nuance or specific denial
        # Simple heuristic: If prompt says "not", and candidate is a bare "Yes", slight penalty
        if prompt_struct['neg_count'] > 0:
            if re.search(r'\byes\b', candidate_lower) and not re.search(r'\bno\b|\bnot\b', candidate_lower):
                # Potential trap: answering yes to a negative question without qualification
                penalty += 0.2
        
        # 2. Numeric Consistency
        cand_numbers = [float(n) for n in re.findall(self.number_pattern, candidate)]
        if cand_numbers and prompt_struct['numbers']:
            # If both have numbers, check for gross contradictions (e.g. prompt max is 5, candidate says 100)
            # This is a simplified transitivity check
            p_max = max(prompt_struct['numbers']) if prompt_struct['numbers'] else 0
            c_max = max(cand_numbers)
            if p_max > 0 and c_max > (p_max * 10): # Heuristic outlier detection
                penalty += 0.5
                
        # 3. Structural Match (Length/Complexity as proxy for conditional handling)
        # Complex prompts (conditionals) usually require complex answers
        if prompt_struct['has_conditional']:
            if len(candidate.split()) < 3: # Too short to handle an if-then
                penalty += 0.3
                
        return min(penalty, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _phase_transition_score(self, base_score: float, violation: float, threshold: float = 0.25) -> float:
        """
        Phase Transition Analysis:
        Apply a non-linear modifier based on the 'order parameter' (violation level).
        If violation is near the critical threshold, the system is unstable.
        We penalize candidates that are close to failing (high susceptibility).
        """
        # Order parameter: distance from critical violation threshold
        delta = violation - threshold
        
        if delta < 0:
            # Stable regime: Below critical threshold. 
            # Small bonus for being safely within equilibrium
            modifier = 1.0 + (0.1 * (threshold - violation) / threshold)
        else:
            # Unstable regime: Above critical threshold.
            # Sharp drop-off (phase transition) in score
            modifier = 1.0 - (0.5 * min(delta, 1.0))
            
        return base_score * modifier

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        # We use a reference string (prompt itself or empty) to gauge compression
        ref = prompt 
        
        for cand in candidates:
            # 1. Structural Parsing & Constraint Propagation
            violation = self._check_constraint_violation(prompt_struct, cand)
            
            # 2. Base Score (Inverse of violation)
            base_score = 1.0 - violation
            
            # 3. Phase Transition Adjustment (Critical-Equilibrium Loop)
            final_score = self._phase_transition_score(base_score, violation)
            
            # 4. NCD Tiebreaker (stored for later)
            ncd_val = self._compute_ncd(prompt, cand)
            
            scored_candidates.append({
                'candidate': cand,
                'score': final_score,
                'ncd': ncd_val,
                'reasoning': f"Violation penalty: {violation:.2f}, Phase-adjusted score applied."
            })
        
        # Sort: Primary by score (desc), Secondary by NCD (asc - closer is often better contextually)
        # Note: In some reasoning tasks, lower NCD to prompt isn't always better, 
        # but for "answering", relevance (similarity) is a safe tie-breaker.
        scored_candidates.sort(key=lambda x: (x['score'], -x['ncd']), reverse=True)
        
        # Clean up and format output
        result = []
        for item in scored_candidates:
            result.append({
                'candidate': item['candidate'],
                'score': item['score'],
                'reasoning': item['reasoning']
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on equilibrium stability.
        """
        struct = self._extract_structure(prompt)
        violation = self._check_constraint_violation(struct, answer)
        base_conf = 1.0 - violation
        conf = self._phase_transition_score(base_conf, violation)
        return max(0.0, min(1.0, conf))