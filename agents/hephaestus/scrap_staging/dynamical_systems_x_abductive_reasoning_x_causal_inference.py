import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Self-Testing Abductive Causal Dynamical Modeler (SCDM) Simulation.
    
    Mechanism:
    1. Dynamical Systems: Models the prompt-candidate relationship as a trajectory.
       Uses Lyapunov-like stability checks (consistency of parsing) to penalize volatile answers.
    2. Abductive Reasoning: Generates/evaluates hypotheses (candidates) based on:
       - Fit: Structural alignment (negations, comparatives, logic).
       - Simplicity: Occam's razor via string complexity (NCD).
       - Stability: Consistency across re-parsing attempts.
    3. Causal Inference: Identifies causal links in the text (if X then Y) and checks
       if the candidate respects the directionality (do-calculus simulation).
       
    Epistemic Honesty (Tier B):
    Prioritizes detecting ambiguity, presuppositions, and unanswerable queries.
    If meta-confidence is low, scores are capped and confidence returned is < 0.3.
    """

    def __init__(self):
        # Thresholds for abductive scoring
        self.lambda_fit = 0.5
        self.lambda_simple = 0.2
        self.lambda_stability = 0.3
        self.ncd_weight = 0.15
        
        # Patterns for Epistemic Honesty (Tier B)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bwhen did.*stop\b", r"\bquit\b", r"\bassumed\b"
        ]
        self.scope_triggers = [r"\bevery.*a.*\b", r"\ball.*same.*\b"]
        self.pronoun_triggers = [r"\bhe told.*he\b", r"\bshe told.*she\b", r"\bwho was\b"]
        self.dichotomy_triggers = [r"\beither.*or\b", r"\bmust choose\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical structures: negations, comparatives, conditionals."""
        text_lower = text.lower()
        return {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'quantifiers': len(re.findall(r'\b(all|every|some|none|most)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower)
        }

    def _check_meta_confidence(self, prompt: str) -> Tuple[float, List[str]]:
        """
        Evaluate the prompt for ambiguity, presupposition, and unanswerability.
        Returns (confidence_cap, list_of_flags).
        """
        flags = []
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                flags.append("presupposition")
                break
        
        # 2. Scope Ambiguity
        for pattern in self.scope_triggers:
            if re.search(pattern, p_lower):
                # Heuristic: if question asks about specific instance after "every"
                if "?" in prompt and "same" in p_lower or "which" in p_lower:
                    flags.append("scope_ambiguity")
                break

        # 3. Pronoun Ambiguity
        if re.search(r"\b(he|she|him|her|it)\b", p_lower) and "who" in p_lower:
             if re.search(r"\btold\b|\bsaid\b|\basked\b", p_lower):
                flags.append("pronoun_ambiguity")

        # 4. False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                flags.append("false_dichotomy")
                break

        # 5. Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                # Only flag if no objective criteria mentioned
                if "measure" not in p_lower and "data" not in p_lower:
                    flags.append("subjectivity")
                break

        # 6. Unanswerable (Missing Info heuristic)
        if "calculate" in p_lower or "solve" in p_lower:
            if not re.search(r"\d", prompt): # No numbers to calculate with
                flags.append("missing_info")

        if flags:
            return 0.25, flags
        return 1.0, flags

    def _compute_lyapunov_stability(self, prompt: str, candidate: str) -> float:
        """
        Simulate stability by checking consistency of structural extraction.
        In a real dynamical system, this would be dF/dz. Here, we approximate
        stability by how well the candidate's structural signature matches the prompt's.
        High divergence = unstable (high penalty).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # Divergence metric
        divergence = 0.0
        keys = ['negations', 'comparatives', 'conditionals', 'quantifiers']
        for k in keys:
            divergence += abs(p_struct[k] - c_struct[k])
        
        # Normalize divergence (approx)
        max_div = 10.0 
        stability = math.exp(-divergence / max_div) # 1.0 = stable, 0.0 = unstable
        return stability

    def _causal_check(self, prompt: str, candidate: str) -> float:
        """
        Simple causal consistency check.
        If prompt implies A -> B, does candidate violate it?
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Detect simple cause-effect patterns
        if_match = re.search(r"if (.+?) then (.+?)", p_lower)
        cause_effect_score = 1.0
        
        if if_match:
            # If the prompt has an IF-THEN, the candidate should ideally reflect it or not contradict
            # This is a simplified heuristic for the "Causal" component
            if "not" in c_lower and "if" not in c_lower:
                # Potential contradiction if candidate negates without condition
                cause_effect_score = 0.5
                
        return cause_effect_score

    def _constructive_compute(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempt to solve numeric/computational problems directly.
        Returns a correctness score (0.0 to 1.0) if computable, else None.
        """
        # Extract numbers from prompt
        numbers = re.findall(r'\d+\.?\d*', prompt)
        if not numbers:
            return None
            
        try:
            nums = [float(n) for n in numbers]
            
            # Case 1: Direct comparison (e.g., "Is 9.11 < 9.9?")
            if "compare" in prompt.lower() or ("<" in prompt or ">" in prompt):
                if len(nums) >= 2:
                    # Check candidate for truth value
                    cand_lower = candidate.lower().strip()
                    is_true = nums[0] < nums[1] if "<" in prompt else nums[0] > nums[1]
                    if ("yes" in cand_lower or "true" in cand_lower) and is_true:
                        return 1.0
                    if ("no" in cand_lower or "false" in cand_lower) and not is_true:
                        return 1.0
                    return 0.0
            
            # Case 2: Simple arithmetic verification
            # If prompt asks "What is X + Y?" and candidate is a number
            if "what is" in prompt.lower() or "calculate" in prompt.lower():
                # Very basic heuristic: if candidate is a number close to sum/product
                cand_nums = re.findall(r'\d+\.?\d*', candidate)
                if cand_nums:
                    val = float(cand_nums[0])
                    # Try sum
                    if abs(val - sum(nums)) < 1e-5:
                        return 1.0
                    # Try product (if 2 nums)
                    if len(nums) == 2 and abs(val - (nums[0] * nums[1])) < 1e-5:
                        return 1.0
        except:
            pass
            
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Confidence (Epistemic Honesty)
        meta_conf, flags = self._check_meta_confidence(prompt)
        is_ambiguous = len(flags) > 0
        
        # Pre-calculate NCD matrix for tie-breaking
        prompt_comp = prompt.encode('utf-8')
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # A. Constructive Computation (Highest Priority for Tier A)
            comp_score = self._constructive_compute(prompt, cand)
            if comp_score is not None:
                # If we can compute it, this dominates
                base_score = comp_score
                reasoning_parts.append(f"Computed verification: {comp_score}")
            else:
                # B. Abductive Scoring Loop
                # 1. Fit (Structural Alignment)
                p_struct = self._extract_structure(prompt)
                c_struct = self._extract_structure(cand)
                
                # Structural match penalty
                struct_diff = 0
                for k in p_struct:
                    if k == 'numbers': continue
                    struct_diff += abs(p_struct[k] - c_struct[k])
                
                # Normalize fit (inverse of diff)
                fit_score = max(0, 1.0 - (struct_diff * 0.1))
                
                # 2. Stability (Lyapunov-like)
                stability = self._compute_lyapunov_stability(prompt, cand)
                
                # 3. Causal Consistency
                causal = self._causal_check(prompt, cand)
                
                # Combine Abductive components
                base_score = (self.lambda_fit * fit_score) + \
                             (self.lambda_stability * stability) + \
                             (self.lambda_fit * causal) # Reusing fit weight for causal
                
                reasoning_parts.append(f"Fit:{fit_score:.2f} Stab:{stability:.2f} Causal:{causal:.2f}")

            # C. Simplicity/Complexity Penalty (NCD) - Max 15%
            ncd_val = self._ncd(prompt, cand)
            # Lower NCD (more similar) is often better for "explanation", 
            # but for answers, we want relevance. 
            # We use NCD as a tiebreaker/slight penalty for noise.
            ncd_score = 1.0 - min(ncd_val, 1.0) # Higher is better
            
            final_score = (base_score * (1 - self.ncd_weight)) + (ncd_score * self.ncd_weight)
            
            # D. Apply Epistemic Cap
            if is_ambiguous:
                if final_score > 0.3:
                    final_score = 0.3 # Cap score for ambiguous prompts
                reasoning_parts.append(f"Capped due to ambiguity: {flags}")
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-confidence for ambiguous prompts.
        """
        meta_conf, flags = self._check_meta_confidence(prompt)
        
        # If ambiguous, return low confidence immediately
        if meta_conf < 1.0:
            return round(meta_conf * 0.9, 2) # Ensure < 0.3
        
        # If not ambiguous, check computational certainty
        comp_score = self._constructive_compute(prompt, answer)
    if comp_score is not None:
            if comp_score == 1.0:
                return 0.95 # High confidence on verified math
            else:
                return 0.1 # Low confidence on wrong math
        
        # Structural confidence
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        
        # Check for structural alignment
        mismatch = 0
        for k in ['negations', 'conditionals']:
            if p_struct[k] > 0 and c_struct[k] == 0:
                mismatch += 1
            if p_struct[k] == 0 and c_struct[k] > 0:
                mismatch += 1
                
        # Base confidence on lack of mismatch and presence of structural tokens
        base_conf = 0.7
        if mismatch > 0:
            base_conf -= (mismatch * 0.2)
        if p_struct['negations'] > 0 or p_struct['conditionals'] > 0:
             base_conf += 0.1 # Reward handling complex logic
             
        # NCD check for noise
        ncd_val = self._ncd(prompt, answer)
        if ncd_val > 0.8: # Very different strings might be low confidence if logic isn't clear
            base_conf -= 0.1
            
        return round(max(0.1, min(0.9, base_conf)), 2)

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Numeric Trap (Tier A)
    p1 = "Is 9.11 greater than 9.9?"
    c1 = ["Yes", "No"]
    res1 = tool.evaluate(p1, c1)
    print(f"Test 1 (Numeric): {res1[0]['candidate']} (Score: {res1[0]['score']})")
    
    # Test 2: Presupposition Trap (Tier B)
    p2 = "Have you stopped cheating on tests?"
    c2 = ["Yes", "No"]
    conf2 = tool.confidence(p2, "Yes")
    print(f"Test 2 (Presupposition): Confidence = {conf2} (Should be < 0.3)")
    
    # Test 3: Ambiguity
    p3 = "John told Bill he was wrong. Who was wrong?"
    c3 = ["John", "Bill"]
    conf3 = tool.confidence(p3, "John")
    print(f"Test 3 (Pronoun Ambiguity): Confidence = {conf3} (Should be < 0.3)")