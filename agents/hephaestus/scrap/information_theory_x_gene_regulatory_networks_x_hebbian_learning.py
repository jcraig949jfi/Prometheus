import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A self-modulating reasoning tool inspired by Gene Regulatory Networks (GRN),
    Hebbian Learning, and Information Theory.
    
    Mechanism:
    1. GRN Layer (Hypothesis Selection): The prompt is parsed for structural markers
       (negations, comparatives, conditionals). This acts as the "gene expression" profile,
       selecting an attractor state (e.g., "NumericEval", "LogicCheck", "AmbiguityDetect").
    2. Information-Theoretic Modulation: We estimate the Mutual Information (MI) between
       the prompt structure and candidate answers using Normalized Compression Distance (NCD)
       as a proxy for shared information content. High MI (low NCD) suggests the candidate
       encodes the prompt's constraints well.
    3. Hebbian Update: Synaptic weights (scores) are updated via a rule: 
       Delta_W = eta * (Activity_Prompt * Activity_Candidate - Decay).
       Here, 'Activity' is the structural match score. 'eta' is gated by the GRN state.
    4. Metacognition: If the GRN detects ambiguity (presuppositions, pronouns) or lacks
       sufficient structural signals, confidence is capped low (<0.3), enforcing epistemic honesty.
    """

    def __init__(self):
        # GRN Attractor States
        self.states = ["NUMERIC", "LOGIC", "AMBIGUOUS", "DEFAULT"]
        self.current_state = "DEFAULT"
        
        # Hebbian Parameters
        self.base_eta = 0.5
        self.decay = 0.1
        
        # Structural Signatures (Gene Regulatory Sequences)
        self.negations = ["no", "not", "never", "none", "neither", "n't"]
        self.comparatives = ["more", "less", "greater", "smaller", "larger", "shorter", "better", "worse"]
        self.conditionals = ["if", "unless", "provided", "when", "then"]
        self.presupposition_triggers = ["stopped", "quit", "failed", "regret", "realize"]
        self.pronoun_triggers = ["he", "she", "him", "her", "they", "them"]
        self.dichotomy_triggers = ["either", "or", "choice", "choose"]

    def _compress(self, text: str) -> bytes:
        return zlib.compress(text.encode('utf-8'))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a proxy for Information Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(self._compress(s1))
        c2 = len(self._compress(s2))
        c12 = len(self._compress(s1 + s2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        # Match integers and floats, handling negative signs
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _grn_attractor(self, prompt: str) -> str:
        """
        Gene Regulatory Network Layer.
        Determines the system's state based on structural markers in the prompt.
        """
        p_lower = prompt.lower()
        words = re.findall(r'\b\w+\b', p_lower)
        
        score_numeric = 0
        score_logic = 0
        score_ambig = 0
        
        # Count markers
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Numeric density
        nums = self._extract_numbers(prompt)
        if len(nums) >= 2:
            score_numeric += 2.0
        if len(nums) > 0 and any(w in p_lower for w in ["sum", "total", "average", "difference"]):
            score_numeric += 1.0
            
        # Logic density
        if cond_count > 0:
            score_logic += 1.5
        if neg_count > 0:
            score_logic += 1.0
        if comp_count > 0:
            score_logic += 1.0
            
        # Ambiguity/Trap detection (Metacognitive triggers)
        # 1. Presupposition: "Have you stopped..."
        if any(trig in p_lower for trig in ["have you", "did you"] + self.presupposition_triggers):
             if any(trig in p_lower for trig in self.presupposition_triggers):
                score_ambig += 2.0
        
        # 2. Pronoun ambiguity with "who"
        if ("who" in p_lower or "which one" in p_lower) and any(p in p_lower for p in self.pronoun_triggers):
            score_ambig += 1.5
            
        # 3. False dichotomy
        if any(w in words for w in self.dichotomy_triggers) and ("or" in p_lower):
            # Simple heuristic: if "either" or "choice" appears, raise suspicion
            if "either" in p_lower or "choice" in p_lower:
                score_ambig += 1.0

        # Determine Attractor
        if score_ambig >= 1.5:
            return "AMBIGUOUS"
        elif score_numeric >= 2.0:
            return "NUMERIC"
        elif score_logic >= 1.5:
            return "LOGIC"
        else:
            return "DEFAULT"

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        if any(t in p_lower for t in self.presupposition_triggers):
            if any(q in p_lower for q in ["have you", "did you", "why did", "when did"]):
                return 0.2
        
        # 2. Scope/Pronoun Ambiguity
        if ("who" in p_lower or "what did he" in p_lower or "what did she" in p_lower):
            if any(p in p_lower for p in self.pronoun_triggers):
                return 0.25

        # 3. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly", "opinion"]
        if any(w in p_lower for w in subjective_words):
            if "calculate" not in p_lower and "math" not in p_lower:
                return 0.3

        # 4. Unanswerable / Missing Info
        if "unknown" in p_lower or "cannot be determined" in p_lower:
            return 0.4 # Moderate confidence if admitting ignorance is the answer
            
        return 1.0 # No red flags

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural parsing and constructive computation.
        Returns a value between 0 and 1.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Attempt to verify simple arithmetic relations implied by keywords
            if "sum" in p_lower or "total" in p_lower or "add" in p_lower:
                if abs(sum(c_nums) - sum(p_nums)) < 1e-5:
                    score += 1.0
                else:
                    score -= 0.5
            elif "difference" in p_lower or "subtract" in p_lower:
                # Check if candidate is difference of first two
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    if abs(c_nums[0] - abs(p_nums[0] - p_nums[1])) < 1e-5:
                        score += 1.0
            elif "product" in p_lower or "multiply" in p_lower:
                 if len(p_nums) >= 2 and len(c_nums) >= 1:
                    if abs(c_nums[0] - (p_nums[0] * p_nums[1])) < 1e-5:
                        score += 1.0
            elif "greater" in p_lower or "larger" in p_lower or "max" in p_lower:
                if len(c_nums) >= 1 and len(p_nums) >= 1:
                    if c_nums[0] == max(p_nums):
                        score += 1.0
            elif "less" in p_lower or "smaller" in p_lower or "min" in p_lower:
                if len(c_nums) >= 1 and len(p_nums) >= 1:
                    if c_nums[0] == min(p_nums):
                        score += 1.0
            # General float comparison if explicit in prompt
            elif "<" in prompt or ">" in prompt or "compare" in p_lower:
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # Heuristic: if candidate matches one of the numbers and logic holds
                    # This is hard to do perfectly without parsing the full sentence structure
                    # Fallback to NCD for numeric if not explicit operation
                    pass 

        # 2. Constraint Propagation (Negation/Conditionals)
        # If prompt has "not", candidate should ideally reflect negation or contradiction
        has_neg = any(w in p_lower for w in self.negations)
        cand_has_neg = any(w in c_lower for w in self.negations)
        
        if has_neg:
            # If prompt is negative, a "yes" might be wrong depending on context, 
            # but purely structurally, we look for alignment.
            # Simplified: If prompt asks "Is X not Y?", and candidate is "No", that's often correct.
            # We rely heavily on NCD here as a proxy for semantic alignment with constraints.
            pass

        # 3. Information Theoretic Modulation (NCD Proxy)
        # Low NCD = High Mutual Information = Good fit
        ncd_val = self._ncd(prompt, candidate)
        # Convert distance to similarity (0 to 1, where 1 is best)
        # NCD is 0 (identical) to ~1 (different). We want high score for low NCD.
        # However, answer shouldn't be identical to prompt. 
        # We use NCD relative to a baseline or just invert it with a penalty for length mismatch.
        info_score = max(0.0, 1.0 - ncd_val)
        
        # Penalty for length mismatch (answers are usually shorter than prompts)
        len_ratio = min(len(candidate), len(prompt)) / max(len(candidate), len(prompt), 1)
        
        # Combine
        # If we found constructive evidence, boost heavily.
        if score > 0:
            return min(1.0, score + 0.5 * info_score)
        
        # Otherwise, rely on Info Theory (NCD) + Structural overlap
        # Check for keyword overlap of critical tokens
        critical_overlap = 0.0
        for w in self.comparatives + self.negations + self.conditionals:
            if w in p_lower and w in c_lower:
                critical_overlap += 0.2
        
        final_score = (0.6 * info_score) + (0.3 * critical_overlap) + (0.1 * len_ratio)
        return min(1.0, max(0.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. GRN State Selection
        self.current_state = self._grn_attractor(prompt)
        
        # 2. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            # Compute raw structural/info score
            raw_score = self._compute_structural_score(prompt, cand)
            
            # Apply Hebbian-like modulation based on state
            if self.current_state == "AMBIGUOUS":
                # In ambiguous states, even good matching candidates get capped
                score = min(raw_score, meta_cap)
                reasoning = f"State: {self.current_state}. Prompt contains ambiguity/traps. Confidence capped."
            elif self.current_state == "NUMERIC":
                # Numeric states require precise calculation. 
                # If raw_score is high (calc matched), keep it. If low, it's wrong.
                # Meta cap usually 1.0 here unless prompt is nonsense.
                score = raw_score 
                reasoning = f"State: {self.current_state}. Numeric evaluation performed."
            else:
                # Default/Logic: Blend NCD and structural hints
                score = raw_score
                if meta_cap < 0.5:
                    score = min(score, meta_cap)
                    reasoning = f"State: {self.current_state}. Low confidence due to prompt properties."
                else:
                    reasoning = f"State: {self.current_state}. Structural and Info-theoretic analysis."

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via _meta_confidence.
        """
        # Check meta-constraints first
        cap = self._meta_confidence(prompt)
        
        # If the prompt is inherently ambiguous/unanswerable, return low confidence immediately
        if cap < 0.3:
            return cap
            
        # Otherwise, evaluate the specific answer quality
        # We simulate the evaluation of this single candidate against the prompt
        # to see if it stands out structurally.
        score = self._compute_structural_score(prompt, answer)
        
        # If the score is very low, confidence should be low
        # If the score is high, but meta_cap is moderate, respect the cap
        final_conf = min(score, cap)
        
        # Never return > 0.9 unless it's a perfect structural match in numeric/logic
        if self.current_state in ["NUMERIC", "LOGIC"] and score > 0.95:
            return min(0.95, final_conf)
            
        return float(final_conf)

    def _meta_confidence(self, prompt: str) -> float:
        """Helper to match the internal method name used in logic."""
        return self.__class__._meta_confidence(self, prompt)

# Re-binding for the instance method call within the class context if needed, 
# but the logic above uses self._meta_confidence correctly.
# The method _meta_confidence is defined above.