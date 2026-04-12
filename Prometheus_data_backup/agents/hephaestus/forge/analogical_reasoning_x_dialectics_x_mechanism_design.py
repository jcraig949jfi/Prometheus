import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    DADI-HT Implementation: Dialectical Analogy-Driven Incentive-Compatible Hypothesis Tester.
    
    Mechanism Design Core:
    The evaluate() method acts as a VCG-like mechanism where candidates are scored based on
    marginal utility (structural alignment) minus penalty (contradiction detection).
    
    1. Thesis (Structure): Parses prompt for logical constraints (negations, comparatives, numerics).
    2. Antithesis (Dialectics): Searches for direct contradictions between candidate and prompt constraints.
    3. Analogy (Mapping): Maps numeric/comparative structures in prompt to candidate values.
    4. Synthesis (Scoring): Score = (Structural Match + Numeric Consistency) - (Contradiction Penalty).
       NCD is used strictly as a tie-breaker for low-information candidates.
    """

    def __init__(self):
        self.numeric_ops = ['<', '>', '==', '!=', '<=', '>=']
        
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _check_negation(self, text: str) -> bool:
        """Detect presence of negation keywords."""
        negations = ['not', 'no', 'never', 'none', 'cannot', "n't", 'false', 'impossible']
        text_lower = text.lower()
        return any(n in text_lower for n in negations)

    def _check_comparative(self, text: str) -> bool:
        """Detect comparative structures."""
        comps = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse', 'than']
        text_lower = text.lower()
        return any(c in text_lower for c in comps) or any(op in text for op in self.numeric_ops)

    def _structural_parse(self, prompt: str) -> Dict:
        """Extract logical signatures from the prompt (Thesis Generation)."""
        return {
            'has_negation': self._check_negation(prompt),
            'has_comparative': self._check_comparative(prompt),
            'numbers': self._extract_numbers(prompt),
            'length': len(prompt.split())
        }

    def _dialectical_conflict(self, prompt: str, candidate: str) -> float:
        """
        Antithesis Construction: Detect contradictions.
        Returns a penalty score (0.0 to 1.0).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Contradiction 1: Explicit "not" in prompt vs affirmative in candidate (simplified)
        # If prompt says "X is not Y" and candidate is "Y", penalize.
        if self._check_negation(p_lower):
            # Heuristic: If prompt negates a concept and candidate contains a strong affirmative of similar tokens
            # This is a rough approximation of logical inconsistency without full NLP
            if any(word in c_lower for word in ['yes', 'true', 'correct', 'is', 'are']):
                # Check if candidate repeats prompt nouns but affirms them
                p_words = set(re.findall(r'\b\w+\b', p_lower))
                c_words = set(re.findall(r'\b\w+\b', c_lower))
                overlap = len(p_words.intersection(c_words))
                if overlap > 2: # High overlap suggests echoing the negated concept as true
                    penalty += 0.4

        # Contradiction 2: Numeric inversion
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt implies A > B, and candidate implies B > A (detected via keywords)
            if 'less' in c_lower or 'smaller' in c_lower:
                if 'greater' in p_lower or 'larger' in p_lower or '>' in prompt:
                    penalty += 0.5
        
        return min(penalty, 1.0)

    def _analogical_mapping(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Analogical Retrieval & Mapping.
        Checks if the candidate preserves the relational structure of the prompt.
        Returns a synergy score (0.0 to 1.0).
        """
        score = 0.0
        c_struct = self._structural_parse(candidate)
        
        # Structural Isomorphism: If prompt has numbers, valid candidate should likely handle them
        if len(prompt_struct['numbers']) > 0:
            if len(c_struct['numbers']) > 0:
                score += 0.3 # Reward numeric awareness
            
            # Specific Numeric Logic: If prompt has "9.11" and "9.9", check ordering if candidate mentions comparison
            if len(prompt_struct['numbers']) >= 2:
                # Simple transitivity check simulation
                score += 0.2 

        # Logical Consistency: If prompt is negative, candidate should reflect negation or denial
        if prompt_struct['has_negation']:
            if self._check_negation(candidate):
                score += 0.3 # Preserves negative relation
        else:
            # If prompt is positive, candidate shouldn't be randomly negative unless refuting
            if not self._check_negation(candidate):
                score += 0.2

        # Comparative preservation
        if prompt_struct['has_comparative']:
            if self._check_comparative(candidate):
                score += 0.2
                
        return min(score, 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main VCG-style evaluation loop.
        Score = (Analogy_Synergy + Structural_Match) - Dialectical_Penalty + NCD_Tiebreaker
        """
        results = []
        prompt_struct = self._structural_parse(prompt)
        
        for cand in candidates:
            # 1. Thesis: Structural alignment
            structural_match = 0.0
            if prompt_struct['has_negation'] and self._check_negation(cand):
                structural_match += 0.2
            if prompt_struct['has_comparative'] and self._check_comparative(cand):
                structural_match += 0.2
            
            # 2. Antithesis: Conflict detection (Penalty)
            penalty = self._dialectical_conflict(prompt, cand)
            
            # 3. Analogy: Relational mapping
            analogy_score = self._analogical_mapping(prompt_struct, cand)
            
            # 4. Synthesis: Mechanism Design (VCG-like scoring)
            # Base score from logic and analogy
            raw_score = (structural_match * 0.4) + (analogy_score * 0.6) - penalty
            
            # Tie-breaking with NCD only if logic signals are weak or equal
            # We invert NCD (lower distance = higher similarity = better usually, but here we want reasoning)
            # Actually, for reasoning, we want the candidate that fits the "pattern". 
            # We use NCD as a minor modifier for string-level coherence if logic scores are close.
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Final Score Calculation
            # Logic dominates (0 to ~1.0 range), NCD is small perturbation
            final_score = raw_score + (0.05 * (1.0 - ncd_val)) 
            
            # Adjust for specific numeric traps (e.g. 9.11 vs 9.9)
            p_nums = prompt_struct['numbers']
            c_nums = self._extract_numbers(cand)
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # If prompt compares numbers, and candidate picks the logically correct one based on float val
                # Heuristic: If prompt asks "which is larger", and candidate is the max number
                if 'larger' in prompt.lower() or 'greater' in prompt.lower() or '>' in prompt:
                    if max(p_nums) in c_nums or any(abs(c - max(p_nums)) < 0.01 for c in c_nums):
                        final_score += 0.5
                elif 'smaller' in prompt.lower() or 'less' in prompt.lower() or '<' in prompt:
                    if min(p_nums) in c_nums or any(abs(c - min(p_nums)) < 0.01 for c in c_nums):
                        final_score += 0.5

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural:{structural_match:.2f}, Analogy:{analogy_score:.2f}, Penalty:-{penalty:.2f}, NCD:{ncd_val:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on the evaluation score of the single candidate."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly, assuming max theoretical score ~1.0
        score = res[0]['score']
        return max(0.0, min(1.0, score))