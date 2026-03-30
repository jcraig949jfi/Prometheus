import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    GEINLA-inspired Reasoning Tool with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Confidence (Gauge Field): Evaluates the prompt for ambiguity, 
       presuppositions, and logical traps. If detected, caps confidence low.
    2. Structural Parsing (Fiber Bundle Base): Extracts negations, comparatives, 
       and conditionals to determine logical validity.
    3. Constructive Computation (Clonal Mutation): Attempts to solve numeric 
       expressions or logical transitivity explicitly.
    4. NCD (Immune Memory): Used only as a tiebreaker for semantic similarity.
    
    Scores are decomposed: Judgment (40%), Structural (30%), Computation (20%), NCD (10%).
    """

    def __init__(self):
        # Preset keywords for meta-cognitive checks
        self.presupposition_triggers = [
            "have you stopped", "have you quit", "why did", "why does", 
            "when did", "how often did", "failed to", "stopped"
        ]
        self.false_dichotomy_triggers = ["either", "or not", "choice between"]
        self.scope_ambiguity_patterns = [
            r"every\s+\w+\s+\w+\s+a\s+\w+", 
            r"each\s+\w+\s+\w+\s+the\s+same"
        ]
        self.pronoun_triggers = ["he told", "she told", "they told", "who was", "who is"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value: 0.25 if ambiguous/trapped, 1.0 if clear.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for trigger in self.presupposition_triggers:
            if trigger in p_lower:
                # Check if it's a direct question implying a fact not in evidence
                if "?" in prompt or "why" in p_lower:
                    return 0.25
        
        # 2. False Dichotomy Check
        if "either" in p_lower and ("or" in p_lower):
            if "option" in p_lower or "choice" in p_lower:
                return 0.25

        # 3. Pronoun Ambiguity
        if any(t in p_lower for t in self.pronoun_triggers):
            if "who" in p_lower and "?" in prompt:
                return 0.25

        # 4. Subjectivity Check
        subjective_words = ["best", "worst", "favorite", "opinion", "feel"]
        if any(w in p_lower for w in subjective_words):
            if "objective" not in p_lower and "fact" not in p_lower:
                return 0.25

        return 1.0

    def _parse_structure(self, prompt: str, candidate: str) -> float:
        """
        Parses logical structure: negations, comparatives, conditionals.
        Returns a score component (0.0 to 1.0).
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        has_no = " no " in p_lower or "not " in p_lower or "never " in p_lower
        cand_no = " no " in c_lower or "not " in c_lower or "never " in c_lower
        
        if has_no and cand_no:
            score += 0.4
        elif not has_no and not cand_no:
            score += 0.4
        elif has_no != cand_no:
            # Mismatch in negation usually implies wrongness, but context matters.
            # If prompt asks "Is it not X?" and answer is "No", that's complex.
            # Simple heuristic: if prompt has negation and candidate doesn't, penalize heavily?
            # Instead, rely on NCD for semantic match, but flag structural mismatch.
            score -= 0.2 

        # Comparative logic (greater/less)
        comparatives = ["greater", "less", "more", "fewer", "larger", "smaller"]
        if any(c in p_lower for c in comparatives):
            if any(c in c_lower for c in comparatives):
                score += 0.3
            else:
                # Candidate ignores comparative nature
                score -= 0.1

        return max(0.0, min(1.0, score))

    def _compute_answer(self, prompt: str) -> Optional[str]:
        """
        Attempts to solve numeric or logical problems constructively.
        Returns the computed answer as a string if solvable, else None.
        """
        # Extract numbers
        numbers = re.findall(r"-?\d+\.?\d*", prompt)
        
        # Case 1: Direct Comparison (e.g., "Is 9.11 > 9.9?")
        if len(numbers) >= 2:
            try:
                n1 = float(numbers[0])
                n2 = float(numbers[1])
                if "greater" in prompt.lower() or ">" in prompt:
                    return "yes" if n1 > n2 else "no"
                elif "less" in prompt.lower() or "<" in prompt:
                    return "yes" if n1 < n2 else "no"
                elif "equal" in prompt.lower() or "==" in prompt:
                    return "yes" if math.isclose(n1, n2) else "no"
            except ValueError:
                pass

        # Case 2: Simple Arithmetic (e.g., "What is 2 + 2?")
        if re.search(r"what is|calculate|solve", prompt.lower()):
            # Very basic eval safety check
            if re.match(r"^[\d\+\-\*\/\.\s\(\)]+$", prompt.replace("what is", "").replace("?", "")):
                try:
                    # Extract expression
                    expr = re.sub(r"[^\d\+\-\*\/\.\s\(\)]", "", prompt)
                    if expr:
                        res = eval(expr)
                        return str(res)
                except:
                    pass
        return None

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if len_combined == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Analysis (Gauge Field)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Constructive Computation (Clonal Selection)
        computed_ans = self._compute_answer(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # A. Structural Score (30%)
            struct_score = self._parse_structure(prompt, cand)
            
            # B. Computation Score (40% if computed, else 0)
            comp_score = 0.0
            if computed_ans is not None:
                if str(computed_ans).lower().strip() == cand.lower().strip():
                    comp_score = 1.0
                    reasoning_parts.append(f"Computed match: {computed_ans}")
                else:
                    comp_score = 0.0
                    reasoning_parts.append(f"Computed mismatch: expected {computed_ans}")
            else:
                # If no computation possible, shift weight to structure/NCD
                comp_score = 0.5 # Neutral
            
            # C. NCD Score (15%) - Tiebreaker
            ncd = self._ncd_score(prompt, cand)
            # Invert NCD (lower is better) and normalize roughly
            ncd_score = max(0.0, 1.0 - (ncd * 2)) 
            
            # D. Synthesis
            if computed_ans is not None:
                # If we can compute, computation dominates
                final_score = (comp_score * 0.6) + (struct_score * 0.3) + (ncd_score * 0.1)
            else:
                # If no computation, rely on structure and NCD
                final_score = (struct_score * 0.5) + (ncd_score * 0.5)
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is ambiguous, even a "matching" candidate shouldn't get high confidence
            if meta_cap < 0.3:
                final_score = min(final_score, 0.25)
                reasoning_parts.append("Low confidence: Prompt contains ambiguity or presupposition.")
            
            if not reasoning_parts:
                if computed_ans:
                    reasoning_parts.append("Structural and computational analysis.")
                else:
                    reasoning_parts.append("Semantic similarity and structural parsing.")

            results.append({
                "candidate": cand,
                "score": round(float(final_score), 4),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity.
        Caps at 0.9 unless computation produced the answer.
        """
        meta_cap = self._meta_confidence(prompt)
        computed_ans = self._compute_answer(prompt)
        
        # Base confidence from evaluation logic
        eval_res = self.evaluate(prompt, [answer])
        base_score = eval_res[0]["score"] if eval_res else 0.0
        
        # Apply Caps
        if meta_cap < 0.3:
            return 0.25
        
        # If we didn't compute it and it's not a perfect structural match, cap confidence
        if computed_ans is None:
            # If it's just NCD/Structure, don't claim > 0.85 certainty
            base_score = min(base_score, 0.85)
            
        return round(float(base_score), 4)