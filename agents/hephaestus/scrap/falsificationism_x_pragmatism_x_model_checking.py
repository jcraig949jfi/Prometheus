import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adversarial Counterexample-Guided Policy Refinement Tool.
    
    Mechanism:
    1. Hypothesis Formulation (Pragmatism): Extracts structural constraints (negations, 
       comparatives, conditionals, numeric bounds) from the prompt as formal specifications.
    2. Falsification (Model Checking): Treats each candidate answer as a state to be verified.
       The tool attempts to construct a "counterexample" by checking if the candidate 
       violates any extracted logical constraint.
    3. Policy Refinement: Candidates surviving without violations receive high scores.
       Violations act as penalizing signals. NCD is used only as a tie-breaking heuristic
       for semantic similarity when structural signals are ambiguous.
    """
    
    def __init__(self):
        # Patterns for structural parsing (The "Formal Specification")
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|only if|provided that)\b', re.IGNORECASE)
        self.numeric_pattern = re.compile(r'\d+\.?\d*')
        
    def _extract_constraints(self, text: str) -> dict:
        """Parses text to identify logical constraints (The Model)."""
        constraints = {
            'has_negation': bool(self.negation_pattern.search(text)),
            'has_comparative': bool(self.comparative_pattern.search(text)),
            'has_conditional': bool(self.conditional_pattern.search(text)),
            'numbers': [float(x) for x in self.numeric_pattern.findall(text)],
            'length': len(text.split())
        }
        return constraints

    def _check_violation(self, prompt_constraints: dict, candidate: str) -> Tuple[bool, str]:
        """
        Attempts to falsify the candidate against prompt constraints.
        Returns (is_falsified, reason).
        """
        cand_text = candidate.lower()
        cand_constraints = self._extract_constraints(candidate)
        
        # Falsification Rule 1: Negation Consistency
        # If prompt strongly implies a negative constraint, and candidate asserts positive without qualification
        if prompt_constraints['has_negation']:
            # Heuristic: If prompt has "not" and candidate is a direct contradiction pattern
            # This is a simplified logical check for demonstration
            if re.search(r'\b(always|every|all|must)\b', cand_text) and not re.search(r'\b(not|no|except)\b', cand_text):
                return True, "Violates negation constraint (Universal claim vs Negative context)"

        # Falsification Rule 2: Numeric Consistency
        # If prompt defines a bound, check if candidate violates it explicitly
        if len(prompt_constraints['numbers']) >= 2:
            # Simple transitivity check: If prompt implies A > B, and candidate says B > A
            # Since we don't have full semantic parse, we check for direct numeric contradiction patterns
            p_nums = sorted(prompt_constraints['numbers'])
            c_nums = cand_constraints['numbers']
            if c_nums:
                # If candidate reverses the sorted order of the only two numbers in a specific way
                # This is a proxy for logical consistency in numeric reasoning
                if len(p_nums) == 2 and len(c_nums) == 2:
                    if (p_nums[0] < p_nums[1]) and (c_nums[0] > c_nums[1]):
                         # Potential falsification if context suggests ordering
                         if re.search(r'\b(less|smaller|before)\b', cand_text):
                             return True, "Violates numeric ordering constraint"

        # Falsification Rule 3: Structural Mismatch (Conditional)
        if prompt_constraints['has_conditional']:
            if not cand_constraints['has_conditional'] and len(cand_text.split()) < 5:
                # Short answers to conditional prompts often fail to address the condition
                # This is a pragmatic heuristic, not a hard logical falsification
                pass # Soft penalty in scoring, not hard falsification here

        return False, ""

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_constraints = self._extract_constraints(prompt)
        results = []
        
        for cand in candidates:
            score = 1.0
            reasoning_parts = []
            
            # Step 1: Falsification (Model Checking)
            is_falsified, reason = self._check_violation(prompt_constraints, cand)
            if is_falsified:
                score -= 0.6  # Heavy penalty for logical violation
                reasoning_parts.append(f"Falsified: {reason}")
            
            # Step 2: Pragmatic Scoring (Structural Alignment)
            cand_constraints = self._extract_constraints(cand)
            
            # Reward matching structural complexity (Pragmatism: useful answers mirror prompt depth)
            if prompt_constraints['has_conditional'] and cand_constraints['has_conditional']:
                score += 0.2
                reasoning_parts.append("Matches conditional structure")
            
            if prompt_constraints['has_negation'] and cand_constraints['has_negation']:
                score += 0.15
                reasoning_parts.append("Preserves negation context")
                
            # Numeric consistency bonus
            if len(prompt_constraints['numbers']) > 0 and len(cand_constraints['numbers']) > 0:
                # If both have numbers, assume higher relevance than random text
                score += 0.1
                reasoning_parts.append("Numeric alignment detected")

            # Step 3: NCD as Tiebreaker/Refinement
            # Only applied if no strong structural signal found (score still near 1.0 or slightly modified)
            if len(reasoning_parts) == 0:
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD is better (more similar). Convert to score boost.
                # We invert NCD: 0 distance -> 1.0 boost, 1.0 distance -> 0 boost
                ncd_score = (1.0 - ncd_val) * 0.1 
                score += ncd_score
                if ncd_score > 0.05:
                    reasoning_parts.append(f"Semantic proximity (NCD): {1.0-ncd_val:.2f}")
            
            # Clamp score
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No structural violations found; baseline similarity applied."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on lack of falsification and structural alignment."""
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # The score from evaluate is essentially our confidence metric here
        # Map the internal score to a 0-1 confidence where 1 is "Survived rigorous checking"
        return res[0]['score']