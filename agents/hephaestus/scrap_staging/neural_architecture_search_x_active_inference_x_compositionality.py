import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Compositional Active Neural Architecture Search (CAN-NAS) inspired Reasoning Tool.
    
    Mechanism:
    1. Epistemic Honesty (Active Inference): Before scoring, the system performs 
       'meta-cognitive foraging' to detect ambiguity, presuppositions, and unanswerable 
       constraints in the prompt. If uncertainty is high, confidence is capped low.
    2. Structural Parsing (Compositionality): Decomposes prompts into logical modules 
       (negation, comparison, conditionals) to compute a structural score.
    3. Constructive Computation: Executes numeric/logic operations directly.
    4. NAS-inspired Selection: Ranks candidates based on a weighted sum of 
       Structural (50%), Computational (35%), and Compression (15%) scores.
    """

    # Keywords for meta-cognitive checks
    PRESUPPOSITION_TRIGGERS = ["stopped", "quit", "failed", "regret", "why did", "why has", "continue to"]
    AMBIGUITY_TRIGGERS = ["every", "all", "some", "he", "she", "they", "it", "who", "which one"]
    FALSE_DICHOTOMY_TRIGGERS = ["either", "or not", "only option", "must choose"]
    SUBJECTIVITY_TRIGGERS = ["best", "worst", "favorite", "beautiful", "opinion"]

    def __init__(self):
        self.ncd_weight = 0.15
        self.struct_weight = 0.50
        self.comp_weight = 0.35

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value (0.25 if ambiguous/unanswerable, 1.0 if clear).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for trigger in self.PRESUPPOSITION_TRIGGERS:
            if trigger in p_lower:
                # Heuristic: If it asks "why" about a failure/stop, it's likely a trap
                if "why" in p_lower and trigger in p_lower:
                    return 0.25
        
        # 2. False Dichotomy Check
        if "either" in p_lower and ("or" in p_lower):
            # Simple heuristic for false dichotomy patterns
            if "option" in p_lower or "choice" in p_lower:
                return 0.25

        # 3. Subjectivity Check (without criteria)
        for trigger in self.SUBJECTIVITY_TRIGGERS:
            if trigger in p_lower:
                if "measure" not in p_lower and "data" not in p_lower:
                    return 0.25

        # 4. Pronoun/Scope Ambiguity (Simplified)
        # If the prompt asks "who" or "which" but lacks clear antecedents in a short context
        if re.search(r'\b(who|which)\b', p_lower):
            # If the prompt is short and lacks specific names/entities, flag ambiguity
            words = re.findall(r'\b[a-zA-Z]+\b', p_lower)
            if len(words) < 10: 
                return 0.25

        return 1.0

    def _parse_structure(self, prompt: str, candidate: str) -> float:
        """
        Parses logical structure: negations, comparatives, conditionals.
        Returns a score 0-1 based on structural alignment.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        matches = 0
        total_checks = 0

        # Negation Check
        negation_words = ["not", "no", "never", "none", "cannot"]
        has_negation_prompt = any(w in p_lower for w in negation_words)
        has_negation_cand = any(w in c_lower for w in negation_words)
        
        total_checks += 1
        if has_negation_prompt == has_negation_cand:
            matches += 1
        
        # Comparative Check (Greater/Lesser)
        comp_ops = [">", "<", "greater", "less", "more", "fewer"]
        has_comp_prompt = any(op in p_lower for op in comp_ops)
        has_comp_cand = any(op in c_lower for op in comp_ops)
        
        # Also check for numeric presence as a proxy for comparison tasks
        nums_prompt = re.findall(r'\d+\.?\d*', p_lower)
        nums_cand = re.findall(r'\d+\.?\d*', c_lower)
        
        total_checks += 1
        if (has_comp_prompt or len(nums_prompt) > 0) and (has_comp_cand or len(nums_cand) > 0):
            matches += 1
        elif not has_comp_prompt and not has_comp_cand:
            matches += 1 # Both lack it, consistent

        # Conditional Check
        cond_words = ["if", "then", "unless", "otherwise"]
        has_cond_prompt = any(w in p_lower for w in cond_words)
        has_cond_cand = any(w in c_lower for w in cond_words)
        
        total_checks += 1
        if has_cond_prompt == has_cond_cand:
            matches += 1

        return matches / total_checks if total_checks > 0 else 0.5

    def _compute_answer(self, prompt: str) -> Optional[str]:
        """
        Attempts to constructively solve numeric or logical problems.
        Returns the string representation of the answer if solvable, else None.
        """
        # Extract numbers
        nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        p_lower = prompt.lower()

        # Pattern: "What is X + Y?" or "X plus Y"
        if "+" in prompt or "plus" in p_lower:
            if len(nums) >= 2:
                return str(nums[0] + nums[1])
        
        # Pattern: "X - Y" or "minus"
        if "-" in prompt and "negative" not in p_lower.split("-")[0] or "minus" in p_lower:
            if len(nums) >= 2:
                return str(nums[0] - nums[1])

        # Pattern: "X * Y" or "times"
        if "*" in prompt or "times" in p_lower or "x" in p_lower:
            if len(nums) >= 2:
                # Heuristic: if 'x' is used as multiplication, ensure we don't confuse with variable x
                # Simple case: two numbers and 'times'
                if "times" in p_lower:
                    return str(nums[0] * nums[1])
                if "*" in prompt:
                    return str(nums[0] * nums[1])

        # Pattern: Comparison "Which is larger, A or B?"
        if "larger" in p_lower or "greater" in p_lower or "smaller" in p_lower:
            if len(nums) >= 2:
                if "larger" in p_lower or "greater" in p_lower:
                    return str(max(nums[0], nums[1]))
                else:
                    return str(min(nums[0], nums[1]))

        return None

    def _ncd_score(self, s1: str, s2: str) -> float:
        """
        Normalized Compression Distance using zlib.
        Returns 0.0 (identical) to 1.0 (completely different).
        We invert this so 1.0 is similar.
        """
        import zlib
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            len1 = len(zlib.compress(b1))
            len2 = len(zlib.compress(b2))
            len12 = len(zlib.compress(b1 + b2))
            
            denominator = max(len1, len2)
            if denominator == 0:
                return 1.0
            
            ncd = (len12 - min(len1, len2)) / denominator
            return 1.0 - min(ncd, 1.0) # Invert: 1.0 = similar
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Cognitive Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Constructive Computation (Ground Truth)
        computed_answer = self._compute_answer(prompt)
        
        for cand in candidates:
            # Structural Score
            struct_score = self._parse_structure(prompt, cand)
            
            # Computational Score
            comp_score = 0.0
            if computed_answer is not None:
                # Normalize distance between computed and candidate
                try:
                    # Try exact float match first
                    cand_val = float(re.search(r'-?\d+\.?\d*', cand).group() if re.search(r'-?\d+\.?\d*', cand) else "nan")
                    comp_val = float(computed_answer)
                    diff = abs(cand_val - comp_val)
                    # Map difference to 0-1 score (exponential decay)
                    comp_score = math.exp(-diff) 
                except:
                    # If parsing fails but we have a computed answer, check string equality
                    if computed_answer.strip() == cand.strip():
                        comp_score = 1.0
                    else:
                        comp_score = 0.0
            else:
                # No computation possible, rely on structure/NCD
                comp_score = 0.5 # Neutral
            
            # NCD Score (Tiebreaker)
            ncd_score = self._ncd_score(prompt, cand)
            
            # Weighted Sum
            raw_score = (self.struct_weight * struct_score) + \
                        (self.comp_weight * comp_score) + \
                        (self.ncd_weight * ncd_score)
            
            # Apply Epistemic Cap
            # If the prompt is ambiguous (meta_cap < 0.3), we reduce the score variance
            # to reflect uncertainty, unless the candidate explicitly addresses ambiguity.
            if meta_cap < 0.3:
                # Penalize high confidence on ambiguous questions
                final_score = raw_score * 0.5 
            else:
                final_score = raw_score

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Struct:{struct_score:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}, MetaCap:{meta_cap}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation produced a definitive match.
        """
        # 1. Meta Confidence Check
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Check Computational Definitiveness
        computed = self._compute_answer(prompt)
        is_definitive = False
        
        if computed is not None:
            try:
                cand_val = float(re.search(r'-?\d+\.?\d*', answer).group() if re.search(r'-?\d+\.?\d*', answer) else "nan")
                comp_val = float(computed)
                if abs(cand_val - comp_val) < 1e-6:
                    is_definitive = True
            except:
                if computed.strip() == answer.strip():
                    is_definitive = True
        
        # Base score from evaluation logic
        eval_results = self.evaluate(prompt, [answer])
        base_score = eval_results[0]['score'] if eval_results else 0.5
        
        # Apply Caps
        if meta_cap < 0.3:
            return min(base_score, 0.25)
        
        if not is_definitive:
            # If not computationally proven, cap at 0.9 to avoid overconfidence
            return min(base_score, 0.9)
            
        return min(base_score, 1.0)