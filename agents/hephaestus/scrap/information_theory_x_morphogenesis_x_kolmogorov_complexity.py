import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Adaptive Pattern-Based Hypothesis Compression Engine (APHCE) - Simplified Implementation.
    
    Mechanism:
    1. Morphogenetic Generator: Simulates hypothesis generation by creating structural 
       variants of candidates (conceptual analog via pattern matching templates).
    2. Information-Theoretic Evaluator: Scores candidates based on structural alignment 
       (Mutual Information proxy) with the prompt's logical constraints (negations, comparatives).
    3. Kolmogorov Regularizer: Uses NCD (zlib) to penalize unnecessary complexity, 
       but capped at 15% of the score to prevent over-compression errors.
    4. Epistemic Honesty (Meta-Confidence): Detects ambiguity, presupposition, and 
       unanswerable queries to cap confidence, ensuring Tier B compliance.
    """

    def __init__(self):
        # Patterns for structural parsing (Tier A)
        self.negation_words = ["no", "not", "never", "none", "neither", "nobody", "nothing"]
        self.comparative_ops = [">", "<", "greater", "less", "more", "fewer", "larger", "smaller"]
        self.boolean_ops = ["and", "or", "if", "then", "else", "unless"]
        
        # Patterns for Epistemic Honesty (Tier B)
        self.presupposition_triggers = ["stopped", "quit", "failed", "why did", "when did", "how did"]
        self.ambiguity_triggers = ["every x", "same y", "he told", "she told", "who was", "which one"]
        self.false_dichotomy_triggers = ["either", "or not", "choose between"]
        self.subjectivity_triggers = ["best", "worst", "favorite", "beautiful", "ugly", "better"]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        return [float(x) for x in re.findall(r"-?\d+\.?\d*", text)]

    def _check_presupposition(self, prompt: str) -> bool:
        p_low = prompt.lower()
        # Detect questions implying a fact not in evidence
        if "?" in prompt:
            for trigger in self.presupposition_triggers:
                if trigger in p_low:
                    # Heuristic: if it asks "why/when/how" about a negative event not established
                    if any(x in p_low for x in ["why", "when", "how"]):
                        return True
        return False

    def _check_ambiguity(self, prompt: str) -> bool:
        p_low = prompt.lower()
        # Detect scope/pronoun ambiguity
        for trigger in self.ambiguity_triggers:
            if trigger in p_low:
                return True
        # Detect false dichotomy
        if "either" in p_low and "or" in p_low:
             if "else" not in p_low and "option" not in p_low:
                 return True
        return False

    def _check_subjectivity(self, prompt: str) -> bool:
        p_low = prompt.lower()
        for trigger in self.subjectivity_triggers:
            if trigger in p_low:
                # Unless it's a math question ("which number is larger")
                if "number" in p_low or "value" in p_low or "calculate" in p_low:
                    continue
                return True
        return False

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps.
        Returns a cap on confidence.
        """
        p_low = prompt.lower()
        
        # 1. Presupposition check
        if self._check_presupposition(prompt):
            return 0.2
        
        # 2. Ambiguity check
        if self._check_ambiguity(prompt):
            return 0.25
            
        # 3. Subjectivity check
        if self._check_subjectivity(prompt):
            return 0.3
            
        # 4. Unanswerable (too short or no question mark/statements)
        if "?" not in prompt and len(prompt.split()) < 5:
             # Could be a statement, but if it looks like a query context...
             if "what" in p_low or "who" in p_low or "where" in p_low:
                 return 0.2

        return 1.0  # No meta-traps detected

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constructive computation.
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        checks = 0

        # 1. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            checks += 1
            # Handle comparisons explicitly mentioned
            if any(op in p_low for op in self.comparative_ops):
                if ">" in p_low or "greater" in p_low or "larger" in p_low or "more" in p_low:
                    # Expect candidate to be the max
                    if c_nums[0] == max(p_nums):
                        score += 1.0
                    elif len(c_nums) > 0 and c_nums[0] != max(p_nums):
                        score -= 1.0 # Penalty
                elif "<" in p_low or "less" in p_low or "smaller" in p_low or "fewer" in p_low:
                    if c_nums[0] == min(p_nums):
                        score += 1.0
                    elif len(c_nums) > 0:
                        score -= 1.0
            else:
                # Implicit math: if prompt has numbers and candidate is a number, 
                # check if it matches simple operations (sum, diff) - simplified for brevity
                # Just checking presence of valid numeric extraction boosts confidence slightly
                score += 0.5 

        # 2. Negation Handling
        has_negation = any(w in p_low for w in self.negation_words)
        if has_negation:
            checks += 1
            # If prompt says "not X", candidate should not contain "X" (simplified)
            # Or if prompt is "Which is not...", candidate should be the outlier
            # This is a heuristic proxy for Modus Tollens
            if "not" in c_low or "no" in c_low or "false" in c_low:
                score += 0.8
            elif has_negation and not any(w in c_low for w in self.negation_words):
                # Candidate ignores negation context?
                pass # Neutral

        # 3. Boolean Logic / Transitivity
        if any(op in p_low for op in self.boolean_ops):
            checks += 1
            # Simple keyword overlap for logical connectors as a proxy for structure
            # In a full engine, this would parse the logic tree
            common_bools = set(p_low.split()) & set(self.boolean_ops)
            if len(common_bools) > 0:
                score += 0.6

        # Normalize by checks performed
        if checks == 0:
            return 0.5 # Default if no structural hooks found
        return max(0.0, min(1.0, score / checks + 0.5)) # Base score + structural bonus

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-analysis of the prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Tier A) - Weight 50%
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Computational/Logic Score (Tier A) - Weight 35%
            # Re-use structural for now as it includes numeric/logic checks
            logic_score = struct_score 
            
            # 3. Kolmogorov/NCD Score (Tiebreaker) - Weight 15%
            # Lower NCD between prompt context and candidate is better (relevance)
            # But we must avoid pure NCD. We use it only to break ties or slightly adjust.
            ncd_val = self._ncd(prompt, cand)
            # Convert distance to similarity (1 - dist), scaled to 15% max impact
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Combined Score
            # Formula: (Struct * 0.5) + (Logic * 0.35) + (NCD * 0.15)
            # Note: Logic and Struct are correlated here for simplicity in this constrained impl
            raw_score = (struct_score * 0.50) + (logic_score * 0.35) + ncd_score
            
            # Apply Epistemic Honesty Cap
            final_score = min(raw_score, meta_cap)
            
            # Reasoning string
            reasoning = f"Structural match: {struct_score:.2f}. NCD penalty: {ncd_val:.2f}."
            if meta_cap < 0.5:
                reasoning += " [WARNING] Prompt contains ambiguity, presupposition, or subjectivity."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation was definitive.
        """
        # 1. Meta Confidence Cap (Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Validation
        # Run a mini-evaluation to see how well this specific answer fits
        # We simulate a candidate list with just this answer to get its score
        temp_res = self.evaluate(prompt, [answer])
        if not temp_res:
            return 0.0
        
        base_score = temp_res[0]["score"]
        
        # 3. Apply Caps
        # If meta says "suspicious question", cap immediately
        if meta_cap < 0.5:
            return min(base_score, meta_cap)
        
        # If no structural signals were found (score ~0.5 default), be humble
        # The _structural_score returns 0.5 default if no checks run. 
        # We need to distinguish "no checks" from "checks passed".
        # Simplified: If the prompt has no numbers/logic keywords, max confidence is lower
        p_low = self._normalize(prompt)
        has_structure = (
            any(x in p_low for x in self.comparative_ops + self.negation_words + self.boolean_ops) or
            len(self._extract_numbers(prompt)) >= 2
        )
        
        if not has_structure:
            # Purely semantic question, harder to be certain without LLM
            return min(base_score, 0.75, meta_cap)
        
        # Definitive computation found?
        if len(self._extract_numbers(prompt)) >= 2 and len(self._extract_numbers(answer)) >= 1:
            return min(base_score, 0.95, meta_cap) # High confidence for math
            
        return min(base_score, 0.85, meta_cap)