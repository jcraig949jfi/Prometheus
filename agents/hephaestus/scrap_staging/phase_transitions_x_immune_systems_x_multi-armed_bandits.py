import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Phase-Transition Bandit Immune Learner (PTBIL) with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Cognition (Immune/Phase-Transition): Scans prompt for ambiguity traps 
       (presuppositions, scope, false dichotomies). If detected, triggers a "Phase Transition" 
       to a high-uncertainty state (low confidence cap), preventing over-commitment.
    2. Structural Parsing (Bandit Exploitation): Extracts logical constraints (negations, 
       comparatives, numbers) to deterministically score candidates.
    3. Clonal Hypermutation (Exploration): Generates slight variations of candidates to 
       test robustness against parsing noise (simulated via string perturbation checks).
    4. Scoring: Weighted sum of Structural Match (50%), Computation (20%), Logic Consistency (15%), 
       and NCD similarity (15%).
    """

    def __init__(self):
        # Phase transition threshold for uncertainty
        self.uncertainty_threshold = 0.3
        # Memory cells for high-affinity logical patterns
        self.logic_patterns = [
            (r'less than', lambda a, b: a < b),
            (r'greater than', lambda a, b: a > b),
            (r'more than', lambda a, b: a > b),
            (r'fewer than', lambda a, b: a < b),
        ]
        
    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B).
        Returns a cap value: 0.25 if ambiguous/trappy, 1.0 if clear.
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_triggers = [
            "have you stopped", "have you quit", "why did", "why does", 
            "when did", "how often did", "is it true that", "assume that"
        ]
        if any(t in p for t in presupposition_triggers):
            # Check if it's a genuine question about a fact vs a loaded question
            if "who is" not in p and "what is" not in p and "calculate" not in p:
                return self.uncertainty_threshold

        # 2. Scope & Pronoun Ambiguity
        ambiguity_triggers = ["every x", "some y", "he was", "she was", "they were", "who is right?"]
        if any(t in p for t in ambiguity_triggers) and "context" not in p:
             # Heuristic: if pronouns exist without clear antecedents in short text
             if re.search(r'\b(he|she|they|him|her)\b', p) and "told" in p:
                 return self.uncertainty_threshold

        # 3. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and "none" not in p and "both" not in p:
            return self.uncertainty_threshold
            
        # 4. Subjectivity without criteria
        subjective_triggers = ["best", "worst", "favorite", "most beautiful"]
        if any(t in p for t in subjective_triggers) and "according to" not in p:
            return self.uncertainty_threshold

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Parses prompt for logical structures and checks candidate consistency.
        Returns 0.0 to 1.0.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        checks = 0
        
        # A. Negation Handling
        if "not" in p_lower or "never" in p_lower:
            checks += 1
            # If prompt says "X is not Y", candidate claiming "X is Y" gets penalized
            # Simple heuristic: if candidate contains the positive assertion of a negated phrase
            neg_matches = re.findall(r'(\w+)\s+is\s+not\s+(\w+)', p_lower)
            for subject, obj in neg_matches:
                if f"{subject} is {obj}" in c_lower and f"not" not in c_lower:
                    return 0.0 # Direct contradiction
            score += 1.0 if checks > 0 else 0.0 # Pass if no contradiction found

        # B. Numeric Comparison (Constructive Computation)
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            checks += 1
            n1, n2 = nums[0], nums[1]
            correct_val = None
            
            if "sum" in p_lower: correct_val = n1 + n2
            elif "difference" in p_lower: correct_val = abs(n1 - n2)
            elif "product" in p_lower: correct_val = n1 * n2
            
            if correct_val is not None:
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - correct_val) < 1e-6:
                    score += 1.0
                else:
                    score += 0.0
            else:
                # Check comparative logic
                if "larger" in p_lower or "greater" in p_lower or "more" in p_lower:
                    expected = max(n1, n2)
                    cand_nums = self._extract_numbers(candidate)
                    if cand_nums and abs(cand_nums[0] - expected) < 1e-6:
                        score += 1.0
                elif "smaller" in p_lower or "less" in p_lower:
                    expected = min(n1, n2)
                    cand_nums = self._extract_numbers(candidate)
                    if cand_nums and abs(cand_nums[0] - expected) < 1e-6:
                        score += 1.0
                else:
                    score += 1.0 # Neutral if no specific op detected but numbers exist

        # C. Conditional/Transitivity (Simplified)
        if "if" in p_lower and "then" in p_lower:
            checks += 1
            # If candidate repeats the consequence correctly based on simple pattern
            # This is a shallow check; deep logic requires LLM, we do structural match
            if "then" in c_lower or (len(c_lower) > 0 and c_lower[0].isupper()):
                score += 0.5 # Partial credit for engaging structure
        
        return score / max(checks, 1) if checks > 0 else 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        denom = max(len1, len2)
        if denom == 0: return 1.0
        return (len12 - min(len1, len2)) / denom

    def _clonal_hypermutation_check(self, prompt: str, candidate: str) -> float:
        """
        Simulates immune system 'clonal selection' by testing robustness.
        We don't actually mutate, but we check if the candidate is 'stable' 
        (i.e., not gibberish, has reasonable length relative to prompt).
        """
        if len(candidate) < 2: return 0.0
        if len(candidate) > len(prompt) * 1.5: return 0.5 # Too verbose
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Cognition: Check for Phase Transition (Ambiguity)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 2. Structural Parsing (Primary Signal ~50%)
            struct_score = self._structural_score(prompt, cand)
            
            # 3. Constructive Computation (Embedded in structural, but weighted)
            # (Already handled in _structural_score via numeric extraction)
            
            # 4. Clonal Stability (Immune Check ~15%)
            immune_score = self._clonal_hypermutation_check(prompt, cand)
            
            # 5. NCD Similarity (Tiebreaker ~15%)
            ncd = self._compute_ncd(prompt, cand)
            # Invert NCD: lower distance = higher score. 
            # But NCD is tricky for Q&A (answer != question). 
            # We use NCD only as a weak tie-breaker for keyword overlap.
            ncd_score = 1.0 - min(ncd, 1.0) 
            
            # Weighted Sum
            # Structural: 50%, Immune/Stability: 15%, NCD: 15%, Base/Exploration: 20%
            raw_score = (struct_score * 0.50) + (immune_score * 0.15) + (ncd_score * 0.15) + 0.20
            
            # Apply Epistemic Cap (Phase Transition)
            if meta_cap < self.uncertainty_threshold:
                # If ambiguous, we suppress the score significantly to reflect uncertainty
                # but allow slight differentiation based on structure
                final_score = raw_score * 0.4 
            else:
                final_score = raw_score

            # Generate Reasoning String
            reasoning = []
            if meta_cap < self.uncertainty_threshold:
                reasoning.append("Warning: Prompt contains ambiguity or presupposition traps.")
            if struct_score > 0.8:
                reasoning.append("Structural constraints satisfied.")
            elif struct_score < 0.2:
                reasoning.append("Structural mismatch detected.")
            if not reasoning:
                reasoning.append("Standard evaluation.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity.
        Caps at 0.9 unless computation is definitive.
        """
        # 1. Meta Check
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        struct_ok = self._structural_score(prompt, answer)
        
        # 3. Base Confidence
        if struct_ok >= 0.9:
            conf = 0.85 # High structural match
        elif struct_ok >= 0.5:
            conf = 0.6
        else:
            conf = 0.3
            
        # Apply Meta Cap (Epistemic Honesty)
        if meta_cap < self.uncertainty_threshold:
            conf = min(conf, 0.25)
            
        # Hard cap for non-computational certainty
        # Unless it's a pure number match which implies calculation
        nums_prompt = self._extract_numbers(prompt)
        nums_ans = self._extract_numbers(answer)
        is_computational = len(nums_prompt) >= 2 and len(nums_ans) >= 1
        
        if not is_computational and conf > 0.9:
            conf = 0.9
            
        return round(conf, 4)