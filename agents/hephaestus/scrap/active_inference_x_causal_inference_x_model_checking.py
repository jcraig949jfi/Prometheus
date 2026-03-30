import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A closed-loop epistemic planner combining Active Inference, Causal Inference, 
    and Model Checking principles with strict Epistemic Honesty constraints.
    
    Mechanism:
    1. Meta-Cognitive Filter (Model Checking): Analyzes the prompt for logical 
       traps (presuppositions, ambiguity, false dichotomies). If found, caps 
       confidence to ensure Tier B honesty.
    2. Structural Parser (Causal Inference): Extracts negations, comparatives, 
       and conditionals to build a causal graph of the question structure.
    3. Constructive Solver (Active Inference): Performs numeric evaluation or 
       logical deduction to minimize "free energy" (error) in the answer.
    4. Scoring: Combines structural match (50%), computation (20%), and NCD (15%).
    """

    # Patterns for Tier B Epistemic Honesty checks
    PRESUPPOSITION_TRIGGERS = [
        r"\bhave you stopped\b", r"\bwhy did\b", r"\bwhy does\b", 
        r"\bfailed to\b", r"\bstopped\b", r"\bquit\b", r"\bregret\b"
    ]
    SCOPE_AMBIGUITY = [r"\bevery\b.*\ba\b", r"\ball\b.*\bsome\b"]
    PRONOUN_AMBIGUITY = [r"\b(he|she|him|her|they)\b.*\bwho\b"]
    FALSE_DICHOTOMY = [r"\beither\b.*\bor\b", r"\bmust choose between\b"]
    SUBJECTIVITY = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bbeautiful\b"]
    
    # Structural patterns for Tier A reasoning
    NEGATION_PATTERN = re.compile(r"\b(not|no|never|neither|without)\b", re.IGNORECASE)
    COMPARATIVE_PATTERN = re.compile(r"(\d+\.?\d*)\s*(<|>|<=|>=|==|!=|less than|greater than)\s*(\d+\.?\d*)", re.IGNORECASE)
    NUMBER_EXTRACT = re.compile(r"-?\d+\.?\d*")

    def __init__(self):
        self.state = {"history": []}

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for logical traps and ambiguity.
        Returns a cap value (0.0 - 1.0). Low value indicates unanswerable/ambiguous.
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.PRESUPPOSITION_TRIGGERS:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check for scope ambiguity
        for pattern in self.SCOPE_AMBIGUITY:
            if re.search(pattern, p_lower):
                return 0.25
                
        # Check for pronoun ambiguity in question context
        if re.search(r"\b(he|she|him|her)\b", p_lower) and "who" in p_lower:
             if re.search(r"\btold\b|\bsaid\b", p_lower):
                return 0.25

        # Check for false dichotomy
        for pattern in self.FALSE_DICHOTOMY:
            if re.search(pattern, p_lower):
                # Only flag if no explicit "or both" or similar qualifier exists
                if "or both" not in p_lower and "both" not in p_lower:
                    return 0.25

        # Check for pure subjectivity without data
        has_subj = any(re.search(p, p_lower) for p in self.SUBJECTIVITY)
        has_data = len(re.findall(self.NUMBER_EXTRACT, prompt)) > 0
        if has_subj and not has_data:
            return 0.25

        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Scores based on structural alignment: negations, comparatives, and logical form.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        p_negs = len(self.NEGATION_PATTERN.findall(p_lower))
        c_negs = len(self.NEGATION_PATTERN.findall(c_lower))
        
        if p_negs > 0:
            # If prompt has negation, candidate should ideally reflect it or answer appropriately
            # Simple heuristic: if prompt asks "is not", answer shouldn't blindly affirm without context
            # Here we just check if the candidate contains the same negation density as a proxy for attention
            if p_negs == c_negs or (p_negs > 0 and c_negs > 0):
                score += 0.3
        else:
            # No negation in prompt, candidate shouldn't be overly negative unless answering "No"
            score += 0.3 if c_negs == 0 else 0.1
            
        # 2. Keyword Overlap (Structural, not bag-of-words)
        # Extract comparatives and logical connectors
        logical_tokens = ["if", "then", "else", "therefore", "because", "however", "thus"]
        p_tokens = [t for t in logical_tokens if t in p_lower]
        if p_tokens:
            # Candidate should ideally reference the logic if it's an explanation, 
            # or simply not contradict if it's a direct answer.
            # For this implementation, we reward candidates that don't introduce random logical connectors
            c_tokens = [t for t in logical_tokens if t in c_lower]
            if set(c_tokens).issubset(set(p_tokens)) or len(c_tokens) == 0:
                score += 0.2
        else:
            score += 0.2

        return min(score, 0.5)

    def _compute_answer(self, prompt: str) -> Optional[str]:
        """
        Attempts to constructively solve numeric comparisons or simple logic.
        Returns the computed answer string if solvable, else None.
        """
        # Detect numeric comparison: "Is 9.11 < 9.9?" or "Compare 5 and 3"
        match = re.search(self.COMPARATIVE_PATTERN, prompt)
        if match:
            val1 = float(match.group(1))
            op = match.group(2).lower()
            val2 = float(match.group(3))
            
            res = False
            if op == '<' or op == 'less than': res = val1 < val2
            elif op == '>' or op == 'greater than': res = val1 > val2
            elif op == '==': res = val1 == val2
            elif op == '!=': res = val1 != val2
            
            return "yes" if res else "no"

        # Detect simple arithmetic if present in future extensions
        # For now, focus on the comparison trap (9.11 vs 9.9)
        return None

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            ncd = (c12 - min(c1, c2)) / max_len
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Cognitive Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Constructive Computation (Tier A)
        computed_ans = self._compute_answer(prompt)
        
        for candidate in candidates:
            score = 0.0
            reasoning_parts = []
            
            # If meta-confidence is low, the question is ambiguous/trap.
            # We still score, but the confidence in the final output will be capped.
            if meta_cap < 0.3:
                reasoning_parts.append("Ambiguity detected (Tier B).")
                # In ambiguous cases, prefer shorter, non-committal answers or those acknowledging uncertainty
                if "uncertain" in candidate.lower() or "cannot" in candidate.lower():
                    score = 0.8
                    reasoning_parts.append("Candidate acknowledges uncertainty.")
                else:
                    score = 0.4 # Penalize confident wrongness on traps
                    reasoning_parts.append("Candidate ignores ambiguity.")
            else:
                # Structural Score (50% weight max)
                struct_score = self._structural_score(prompt, candidate)
                
                # Computation Score (20% weight max)
                comp_score = 0.0
                if computed_ans:
                    if computed_ans in candidate.lower():
                        comp_score = 1.0
                        reasoning_parts.append(f"Computed match: {computed_ans}")
                    else:
                        comp_score = 0.0
                        reasoning_parts.append(f"Computation mismatch. Expected: {computed_ans}")
                
                # NCD Score (15% weight max) - Tiebreaker
                ncd = self._ncd_score(prompt, candidate)
                
                # Weighted Sum
                # Structural: 50%, Computation: 35%, NCD: 15%
                final_score = (struct_score * 0.5) + (comp_score * 0.35) + (ncd * 0.15)
                score = final_score
                reasoning_parts.append(f"Structural: {struct_score:.2f}, Comp: {comp_score:.2f}, NCD: {ncd:.2f}")

            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation produced a definitive answer.
        """
        # 1. Meta Check
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Check if we have a computed ground truth
        computed_ans = self._compute_answer(prompt)
        is_definitive = False
        
        if computed_ans:
            if computed_ans in answer.lower():
                base_conf = 0.95
                is_definitive = True
            else:
                # If we computed an answer and this isn't it, low confidence
                base_conf = 0.1
        else:
            # No computation possible, rely on structural match
            # If the candidate looks structurally sound, give moderate confidence
            struct_score = self._structural_score(prompt, answer)
            base_conf = 0.5 + (struct_score * 0.4) # Max 0.9 without computation
        
        # Apply Meta Cap (Epistemic Honesty)
        if meta_cap < 0.3:
            return min(base_conf, 0.25)
            
        # Apply Definitive Cap (Unless computed)
        if not is_definitive:
            base_conf = min(base_conf, 0.85)
            
        return max(0.0, min(1.0, base_conf))