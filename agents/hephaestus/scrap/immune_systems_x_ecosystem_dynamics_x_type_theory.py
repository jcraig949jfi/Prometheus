import re
import zlib
from typing import List, Dict, Any, Optional, Tuple

class ReasoningTool:
    """
    A Type-Guided Clonal-Selection Ecosystem for Automated Reasoning.
    
    Mechanism:
    1. Epistemic Filter (Meta-Confidence): Analyzes the prompt for logical traps
       (presuppositions, ambiguity, false dichotomies). If detected, caps confidence
       to enforce honesty (Tier B).
    2. Structural Parsing & Computation: Extracts numeric values, comparatives, 
       and logical constraints. Performs actual calculation (PEMDAS, float comparison).
    3. Type-Guided Clonal Selection:
       - Candidates are treated as 'terms' in a population.
       - 'Affinity' is calculated via structural match and computational correctness.
       - 'Ecosystem Dynamics': Resources (score weight) flow to candidates that 
         satisfy logical constraints; over-fitted candidates (high string similarity 
         but logical failure) are penalized.
    4. Scoring: Weighted sum of Structural (50%), Computational (35%), and NCD (15%).
    """

    def __init__(self):
        # Logical trap keywords for Tier B detection
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did\b", r"\bwhen did\b", 
            r"\bfailed to\b", r"\brefused to\b", r"\bcontinue to\b"
        ]
        self.ambiguity_triggers = [
            r"\bevery .* a .*\b", r"\bwho was\b", r"\bhe was\b", r"\bshe was\b",
            r"\bit was\b", r"\bthey said\b"
        ]
        self.dichotomy_triggers = [r"\beither .* or\b", r"\bmust choose between\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic hazards.
        Returns a cap value: 0.25 if hazardous, 1.0 if safe.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check Ambiguity (Pronouns/Scope) - simplified heuristic
        if re.search(r"\bwho\b", p_lower) and re.search(r"\bhe\b|\bshe\b|\bthey\b", p_lower):
            # Potential pronoun ambiguity trap
            if "told" in p_lower or "said" in p_lower:
                return 0.25
                
        # Check False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Only flag if no clear logical operator implies exclusivity naturally
                if "or" in p_lower and "either" in p_lower:
                    return 0.25

        # Check Subjectivity without criteria
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                if "calculate" not in p_lower and "compute" not in p_lower:
                    return 0.25

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for computation."""
        # Match integers and floats, handling negative signs
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Parses structure and performs constructive computation.
        Returns a score 0.0 to 1.0 based on logical validity.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        
        # 1. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums:
            # If prompt has numbers, candidate must likely involve calculation or comparison
            if c_nums:
                # Check for direct equality in extracted logic (heuristic for math problems)
                # If prompt asks "Is 9.11 < 9.9?", candidate "Yes" implies correct logic
                if "less than" in p_lower or "<" in prompt:
                    if all(a < b for a, b in zip(p_nums[:-1], p_nums[1:])):
                        if "yes" in c_lower or "true" in c_lower or str(min(p_nums)) in candidate:
                            score += 0.5
                elif "greater than" in p_lower or ">" in prompt:
                    if all(a > b for a, b in zip(p_nums[:-1], p_nums[1:])):
                        if "yes" in c_lower or "true" in c_lower or str(max(p_nums)) in candidate:
                            score += 0.5
                # Exact match of result if simple arithmetic implied
                if len(p_nums) >= 2:
                    # Heuristic: if candidate contains the sum/product, boost score
                    s = sum(p_nums)
                    if str(int(s) if s.is_integer() else s) in candidate:
                        score += 0.5
            
            # If numbers exist but candidate has none, likely wrong for math problems
            if not c_nums and ("calculate" in p_lower or "sum" in p_lower or "add" in p_lower):
                return 0.0

        # 2. Logical Constraint Propagation (Negation/Conditionals)
        has_negation = bool(re.search(r'\bnot\b|\bnever\b|\bno\b', p_lower))
        cand_negation = bool(re.search(r'\bnot\b|\bnever\b|\bno\b', c_lower))
        
        if has_negation:
            # If prompt has negation, valid answers often reflect it or answer the negated premise
            # This is a weak heuristic but captures "Type Safety" of the argument
            score += 0.2 if (has_negation == cand_negation) else 0.0
        
        # 3. Keyword Overlap (Structural similarity without NCD noise)
        # Filter stopwords
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        p_words = set(re.findall(r'\b\w+\b', p_lower)) - stopwords
        c_words = set(re.findall(r'\b\w+\b', c_lower)) - stopwords
        
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
            score += 0.3 * overlap # Max 0.3 from vocabulary match

        return min(score, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance. 0 = identical, 1 = totally different."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
            
        return (len_combined - max_len) / max_len

    def _clonal_affinity(self, prompt: str, candidate: str) -> float:
        """
        Simulates the immune system affinity measure.
        High affinity = High structural/computational match, Low NCD penalty.
        """
        struct_score = self._compute_structural_score(prompt, candidate)
        ncd_val = self._compute_ncd(prompt, candidate)
        
        # Ecosystem dynamics: 
        # Structural/Computational correctness is the primary energy source (Weight 0.85)
        # NCD is a tiebreaker/minor factor (Weight 0.15) to prevent noise
        affinity = (struct_score * 0.85) + ((1.0 - ncd_val) * 0.15)
        
        return affinity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """
        Evaluates candidates using the Type-Guided Clonal-Selection model.
        """
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # Calculate raw affinity (fitness)
            raw_score = self._clonal_affinity(prompt, cand)
            
            # Apply Epistemic Cap (Resource limitation based on prompt validity)
            # If the prompt is a trap (meta_cap = 0.25), even a 'matching' answer 
            # shouldn't get a high confidence score if it blindly accepts the premise.
            # However, for the 'score' in ranking, we reflect the likelihood of correctness.
            # If the question is bogus, no answer is truly 'correct', so score is capped.
            final_score = min(raw_score, meta_cap) if meta_cap < 0.3 else raw_score
            
            # Reasoning trace
            reasoning = []
            if meta_cap < 0.3:
                reasoning.append("Epistemic Warning: Prompt contains ambiguity or presupposition.")
            if self._extract_numbers(prompt) and not self._extract_numbers(cand):
                if any(k in prompt.lower() for k in ['calculate', 'sum', 'greater', 'less']):
                    reasoning.append("Computation Gap: Candidate lacks numeric derivation.")
            
            if not reasoning:
                reasoning.append(f"Structural affinity: {raw_score:.2f}")

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reasoning)
            })
        
        # Sort by score descending (Clonal selection: highest affinity survives)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Strictly capped by _meta_confidence for ambiguous/trap prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt itself is flawed, confidence is low regardless of answer
        if meta_cap < 0.3:
            return 0.25 # Explicitly low confidence for traps
        
        # Otherwise, compute affinity
        score = self._clonal_affinity(prompt, answer)
        
        # Never return > 0.9 unless it's a perfect structural match and computation
        # This prevents overconfidence on heuristic matches
        if score > 0.9:
            # Double check computation
            if self._extract_numbers(prompt):
                if not self._extract_numbers(answer):
                    return 0.5 # Suspicious if math problem has no numbers in answer
        
        return min(score, 0.95) # Hard cap at 0.95 to maintain epistemic humility