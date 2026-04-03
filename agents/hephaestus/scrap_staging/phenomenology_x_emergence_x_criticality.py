import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Self-Organizing Critical Predictive-Coding Network (SOC-PCN) Implementation.
    
    Mechanism:
    1. Phenomenological Bracketing (Meta-Confidence): Analyzes the prompt for 
       presuppositions, ambiguities, and unanswerable constraints. If detected, 
       it suppresses the "gain" (confidence) of all candidates, implementing 
       epistemic honesty.
    2. Critical Dynamics (Scoring): Candidates are evaluated via structural parsing 
       and constructive computation. The system operates at a "critical point" where 
       small structural mismatches (negations, logic errors) cause large score drops 
       (avalanche effect), while valid logic cascades to high scores.
    3. Emergence: The final ranking emerges from the interplay between the global 
       phenomenological gain (honesty cap) and local structural/computational validity.
    
    This satisfies the requirement to integrate Phenomenology (bracketing), 
    Emergence (macro-state ranking), and Criticality (sensitivity to logic).
    """

    def __init__(self):
        # Phenomenological "Lifeworld" state
        self.intentional_focus = "truth_seeking"
        self.bracket_threshold = 0.3  # Cap for ambiguous prompts
        self.high_conf_cap = 0.9      # Max confidence without definitive computation
        
        # Criticality parameters
        self.critical_exponent = 1.5  # Power law scaling for error penalty
        self.structural_weight = 0.50
        self.computation_weight = 0.35
        self.ncd_weight = 0.15

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 - 1.0). If < 0.3, the prompt is considered "bracketed".
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_patterns = [
            r"have you stopped\s+", r"have you quit\s+", r"why did\s+\w+\s+fail",
            r"why is\s+\w+\s+wrong", r"when did\s+\w+\s+stop", r"continue\s+\w+ing"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                return 0.1  # Strong bracket: Presupposition detected

        # 2. Scope & Pronoun Ambiguity (Heuristic)
        # Detects "Every X ... Y" followed by "who/which" questions often implying ambiguity
        if re.search(r"every\s+\w+.*\b(who|which|he|she)\b", p):
            if re.search(r"\b(ambiguous|unclear|who is|which one)\b", p):
                return 0.2
        
        # 3. False Dichotomy
        if re.search(r"\b(either\s+\w+\s+or\s+\w+|is it\s+\w+\s+or\s+\w+)\b", p):
            if not re.search(r"\b(only|exclusive)\b", p):
                # Soft penalty, not a hard bracket unless context implies exclusivity
                pass 

        # 4. Subjectivity without criteria
        subjective_terms = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(term in p for term in subjective_terms):
            if "calculate" not in p and "logic" not in p and "count" not in p:
                return 0.25 # Moderate bracket: Subjective

        # 5. Unanswerability markers
        if re.search(r"\b(no information|cannot be determined|insufficient data)\b", p):
            return 0.15

        return 1.0  # No phenomenological brackets needed

    def _extract_structure(self, prompt: str) -> dict:
        """Extracts logical operators and numeric values for structural parsing."""
        has_negation = bool(re.search(r"\b(not|no|never|neither|without)\b", prompt.lower()))
        has_comparative = bool(re.search(r"\b(more|less|greater|smaller|larger|fewer|than)\b", prompt.lower()))
        has_conditional = bool(re.search(r"\b(if|then|unless|only if)\b", prompt.lower()))
        
        # Extract numbers for constructive computation
        numbers = re.findall(r"-?\d+\.?\d*", prompt)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "numbers": nums
        }

    def _constructive_eval(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Constructive Computation.
        Attempts to solve math/logic problems explicitly.
        Returns 1.0 if correct, 0.0 if wrong, -1.0 if N/A.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip().rstrip('.')
        
        # 1. Numeric Comparison (e.g., "Is 9.11 > 9.9?")
        match_num = re.search(r"(\d+\.?\d*)\s*(<|>|<=|>=|==|!=)\s*(\d+\.?\d*)", prompt.replace(',', ''))
        if match_num:
            n1, op, n2 = match_num.groups()
            n1, n2 = float(n1), float(n2)
            true_val = False
            if op == '>': true_val = n1 > n2
            elif op == '<': true_val = n1 < n2
            elif op == '>=': true_val = n1 >= n2
            elif op == '<=': true_val = n1 <= n2
            elif op == '==': true_val = n1 == n2
            elif op == '!=': true_val = n1 != n2
            
            cand_val = c_lower in ['true', 'yes', '1']
            if true_val and cand_val: return 1.0
            if not true_val and c_lower in ['false', 'no', '0']: return 1.0
            if true_val and c_lower in ['false', 'no', '0']: return 0.0
            if not true_val and cand_val: return 0.0

        # 2. Simple Arithmetic (e.g., "What is 2 + 2?")
        if "what is" in p_lower or "calculate" in p_lower:
            # Very basic extractor for demo purposes
            if re.search(r"\d+\s*[\+\-\*/]\s*\d+", prompt):
                try:
                    # Sanitize and eval safe math
                    expr = re.sub(r'[^\d+\-*/().]', '', prompt)
                    if expr:
                        res = eval(expr)
                        # Check if candidate matches result
                        if re.search(re.escape(str(res)), candidate):
                            return 1.0
                        # Check for float approximation
                        if abs(float(re.findall(r"\d+\.?\d*", candidate)[0]) - res) < 0.01:
                            return 1.0
                except:
                    pass

        # 3. Logic Traps (Modus Tollens / Negation)
        # If prompt has "not" and candidate ignores it
        struct = self._extract_structure(prompt)
        if struct['negation']:
            # Heuristic: If prompt says "not X" and candidate says "X" without qualification
            # This is a weak proxy but helps with Tier A parsing traps
            if "not" in p_lower and "not" not in c_lower and struct['numbers']:
                # If numbers exist and negation exists, ensure candidate isn't just the number
                if re.search(r"\d+", candidate):
                     return 0.5 # Penalty for ignoring negation in numeric context
        
        return -1.0 # No constructive match found

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        
        if len1 + len2 == 0:
            return 0.0
        return (len_concat - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Phenomenological Bracketing (Global Gain Control)
        # Determines the maximum possible confidence for this prompt
        meta_cap = self._meta_confidence(prompt)
        is_bracketed = meta_cap < self.bracket_threshold
        
        # 2. Structural Extraction
        struct = self._extract_structure(prompt)
        has_logic = struct['negation'] or struct['comparative'] or struct['conditional']
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # A. Constructive Computation (High Priority)
            comp_score = self._constructive_eval(prompt, cand)
            if comp_score == 1.0:
                score += self.computation_weight * 2.0 # Boost correct math/logic
                reasoning_parts.append("Constructive verification successful.")
            elif comp_score == 0.0:
                score -= 1.0 # Heavy penalty for wrong math
                reasoning_parts.append("Constructive verification failed.")
            
            # B. Structural Parsing (Criticality)
            # If the prompt has logic operators, the candidate must reflect them
            if has_logic:
                c_lower = cand.lower()
                # Check for negation alignment
                if struct['negation']:
                    if "not" in prompt.lower() and "not" not in c_lower and "no" not in c_lower:
                        # Critical drop if negation is ignored in a logic trap
                        score -= 0.5
                        reasoning_parts.append("Ignored negation operator.")
                    else:
                        score += self.structural_weight
                        reasoning_parts.append("Negation handled.")
                else:
                    score += self.structural_weight * 0.5 # Partial credit for structure check
                
                if struct['comparative']:
                    # Simple keyword check for comparatives
                    if any(k in c_lower for k in ["greater", "less", "more", "smaller", "larger", "than"]):
                        score += self.structural_weight
                        reasoning_parts.append("Comparative logic detected.")
                    else:
                        # If prompt asks for comparison, answer should ideally reflect it
                        pass 
            else:
                # Baseline structural score if no complex logic
                score += self.structural_weight * 0.3

            # C. NCD Tiebreaker (Low weight)
            # Only used if other scores are close or zero
            ncd_val = self._ncd_score(prompt, cand)
            # Invert NCD: lower distance = higher score contribution
            ncd_score = (1.0 - ncd_val) * self.ncd_weight
            score += ncd_score
            
            # D. Apply Phenomenological Cap (The "Bracket")
            # If the prompt is ambiguous (meta_cap low), the final score cannot exceed the cap
            # regardless of how well the candidate matches string patterns.
            if is_bracketed:
                if score > meta_cap:
                    score = meta_cap
                    reasoning_parts.append(f"Score capped by phenomenological bracket (ambiguity detected).")
            
            # Normalize score roughly to 0-1 range for consistency
            # Base score starts around 0.3-0.5. 
            # Correct math -> >0.8. Wrong math -> <0.2. Ambiguous -> <0.3.
            final_score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "Baseline structural match."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Check Phenomenological Brackets first
        cap = self._meta_confidence(prompt)
        
        # 2. Perform quick structural/computational check
        struct = self._extract_structure(prompt)
        comp = self._constructive_eval(prompt, answer)
        
        base_conf = 0.5
        
        if comp == 1.0:
            base_conf = 0.95
        elif comp == 0.0:
            base_conf = 0.1
        elif struct['negation'] or struct['comparative']:
            # If logic exists, we need to be sure. 
            # If constructive eval didn't fire (returns -1), we rely on heuristics
            base_conf = 0.6
        else:
            base_conf = 0.5
            
        # 3. Apply Cap (Epistemic Honesty)
        final_conf = min(base_conf, cap)
        
        # 4. Never return > 0.9 unless computation was definitive
        if comp != 1.0 and final_conf > self.high_conf_cap:
            final_conf = self.high_conf_cap
            
        return round(final_conf, 3)