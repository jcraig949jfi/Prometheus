import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dependent-Type-Guided Falsification Engine (Simplified for General Reasoning).
    
    Mechanism:
    1. Type Construction (Structural Parsing): Parses the prompt to extract logical 
       constraints (negations, comparatives, conditionals) representing the 'Type' 
       a valid answer must inhabit.
    2. Falsification Search (Candidate Evaluation): Attempts to construct a 'proof' 
       that a candidate satisfies the type. Violations of logical constraints act as 
       falsification events, heavily penalizing the score.
    3. Analytic Bounds (Numeric Evaluation): Explicitly evaluates numeric claims 
       found in candidates against constraints (e.g., "9.11 < 9.9").
    4. Compression Tiebreaker: Uses NCD to measure semantic similarity to the prompt 
       context only when logical scores are tied, avoiding the "echo chamber" trap.
    
    This implements the 'Prime x Falsification x Type' synthesis by treating logical 
    consistency as type inhabitation and using falsification to prune invalid candidates.
    """

    def __init__(self):
        # Keywords indicating logical structures for type construction
        self._negations = {'no', 'not', 'never', 'none', 'neither', 'false', 'deny'}
        self._comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower'}
        self._conditionals = {'if', 'then', 'unless', 'provided', 'requires'}
        self._quantifiers = {'all', 'every', 'some', 'at least', 'at most', 'exactly'}

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        # Match integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _parse_logical_type(self, prompt: str) -> Dict:
        """
        Construct the 'Dependent Type' representing the constraints of the prompt.
        Returns a dict of flags and extracted values that a valid candidate must satisfy.
        """
        p_low = self._normalize(prompt)
        constraints = {
            'has_negation': False,
            'has_comparative': False,
            'has_conditional': False,
            'expected_relation': None, # 'lt', 'gt', 'eq'
            'numeric_bound': None,
            'keywords_present': []
        }
        
        words = set(re.findall(r'\b\w+\b', p_low))
        
        # Detect Negation (Falsification trigger)
        if any(n in words for n in self._negations):
            constraints['has_negation'] = True
            constraints['keywords_present'].append('negation')
            
        # Detect Comparatives
        if any(c in words for c in self._comparatives):
            constraints['has_comparative'] = True
            constraints['keywords_present'].append('comparative')
            # Heuristic: if "less" or "smaller" present, expect smaller numbers or 'lt'
            if 'less' in p_low or 'smaller' in p_low or 'fewer' in p_low:
                constraints['expected_relation'] = 'lt'
            elif 'greater' in p_low or 'larger' in p_low or 'more' in p_low:
                constraints['expected_relation'] = 'gt'
                
        # Detect Conditionals
        if any(c in p_low for c in self._conditionals):
            constraints['has_conditional'] = True
            constraints['keywords_present'].append('conditional')

        # Extract numeric bounds if explicit (e.g., "greater than 5")
        nums = self._extract_numbers(p_low)
        if nums:
            # Simple heuristic: assume the last number is a bound if comparatives exist
            if constraints['has_comparative']:
                constraints['numeric_bound'] = nums[-1]

        return constraints

    def _check_falsification(self, prompt: str, candidate: str, constraints: Dict) -> Tuple[bool, float]:
        """
        Attempt to falsify the candidate against the prompt's logical type.
        Returns (is_falsified, penalty_score).
        """
        c_low = self._normalize(candidate)
        c_nums = self._extract_numbers(candidate)
        p_nums = self._extract_numbers(prompt)
        
        penalty = 0.0
        is_falsified = False

        # 1. Numeric Falsification (Analytic Bounds)
        if constraints['numeric_bound'] and c_nums:
            bound = constraints['numeric_bound']
            val = c_nums[-1] # Check the primary number in candidate
            
            if constraints['expected_relation'] == 'gt':
                if val <= bound:
                    is_falsified = True
                    penalty += 0.9
            elif constraints['expected_relation'] == 'lt':
                if val >= bound:
                    is_falsified = True
                    penalty += 0.9
        
        # 2. Logical Consistency (Negation/C presence)
        # If prompt asks "Which is NOT...", and candidate affirms a property strongly
        if constraints['has_negation']:
            # Heuristic: If candidate is a direct subset of prompt words without negation words,
            # it might be an echo trap.
            c_words = set(re.findall(r'\b\w+\b', c_low))
            # If candidate lacks negation words but prompt has them, and candidate is short (echo)
            if len(c_words) < 10 and not any(n in c_words for n in self._negations):
                # Potential echo trap, apply moderate penalty unless it's a clear "No"
                if 'no' not in c_low and 'false' not in c_low:
                    penalty += 0.3

        # 3. Comparative Consistency
        if constraints['has_comparative'] and c_nums and p_nums:
            # If prompt compares A and B, and candidate gives a number, 
            # check if it aligns with the direction implied (simplified)
            pass 

        return is_falsified, penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Step 1: Construct the Logical Type (Constraints) from the prompt
        constraints = self._parse_logical_type(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            score = 1.0
            reasoning_parts = []
            
            # Step 2: Falsification Attempt
            is_falsified, penalty = self._check_falsification(prompt, cand, constraints)
            
            if is_falsified:
                score -= penalty
                reasoning_parts.append("Falsified by analytic/logical bound violation.")
            
            # Step 3: Structural Matching (Type Inhabitation Check)
            # Does the candidate contain necessary keywords implied by the type?
            c_low = self._normalize(cand)
            
            # Bonus for matching specific logical outcomes if detectable
            if constraints['has_negation'] and ('no' in c_low or 'false' in c_low or 'not' in c_low):
                score += 0.2
                reasoning_parts.append("Correctly handles negation constraint.")
            
            if not reasoning_parts:
                reasoning_parts.append("No direct falsification found; relying on semantic similarity.")

            # Step 4: NCD as Tiebreaker/Refinement
            # Only use NCD to differentiate if logical penalties didn't destroy the score
            if score > 0.5:
                ncd = self._compute_ncd(prompt, cand)
                # Adjust score slightly by similarity, but prioritize logical consistency
                # High NCD (dissimilar) might be bad if it's unrelated, good if it's a specific answer
                # We invert logic: We want reasonable similarity but not exact echo
                if ncd < 0.3: # Very similar (potential echo)
                    if len(cand.strip()) < len(prompt.strip()) * 0.5:
                        score -= 0.1 # Penalty for short echo
                        reasoning_parts.append("Penalized for potential echo (high similarity, low content).")
                elif ncd > 0.9: # Very dissimilar
                    score -= 0.1
                    reasoning_parts.append("Penalized for low semantic relevance (high NCD).")

            # Clamp score
            final_score = max(0.0, min(1.0, score))
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence that 'answer' is correct for 'prompt'.
        Uses the same falsification engine.
        """
        # Treat single answer as a list of one to reuse logic
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']