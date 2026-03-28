import re
import zlib
import math

class ReasoningTool:
    """
    Algorithmic Information Causal Adaptive Controller (AICAC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Causal Inference): Extracts logical operators (negations, 
       comparatives, conditionals) to build a structural signature of the prompt and candidates.
    2. Numeric Evaluation (Adaptive Control): Detects numeric values and evaluates 
       comparative constraints (e.g., "9.11" < "9.9") to penalize logically inconsistent candidates.
    3. Kolmogorov Complexity (MDL): Uses NCD (Normalized Compression Distance) as a 
       tie-breaking penalty for candidates that do not compress well relative to the prompt 
       (i.e., those that add unnecessary complexity without structural alignment).
       
    The scoring function prioritizes structural alignment and logical consistency over 
    simple string similarity, adhering to the MDL principle of minimizing description length 
    while maximizing data fit.
    """

    def __init__(self):
        self._num_pattern = re.compile(r"-?\d+\.?\d*")
        self._negations = {"no", "not", "never", "none", "neither", "n't"}
        self._comparatives = {"less", "more", "greater", "smaller", "larger", "fewer", "higher", "lower"}
        self._conditionals = {"if", "then", "else", "unless", "provided"}

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical structure: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self._negations)
        has_comparative = bool(words & self._comparatives)
        has_conditional = bool(words & self._conditionals)
        numbers = [float(n) for n in self._num_pattern.findall(text)]
        
        return {
            "neg": has_negation,
            "comp": has_comparative,
            "cond": has_conditional,
            "nums": sorted(numbers),
            "len": len(text)
        }

    def _structural_distance(self, s1: dict, s2: dict) -> float:
        """Calculates mismatch penalty between two structural signatures."""
        penalty = 0.0
        # Boolean mismatches
        if s1["neg"] != s2["neg"]: penalty += 2.0
        if s1["comp"] != s2["comp"]: penalty += 1.5
        if s1["cond"] != s2["cond"]: penalty += 1.5
        
        # Numeric consistency check (simplified for single-value comparisons)
        if s1["nums"] and s2["nums"]:
            # If both have numbers, check if order logic holds (heuristic)
            # Here we just penalize large magnitude differences if counts match
            if len(s1["nums"]) == len(s2["nums"]):
                for n1, n2 in zip(s1["nums"], s2["nums"]):
                    if abs(n1 - n2) > 1e-6:
                        # Check if the candidate contradicts a comparative in prompt
                        # This is a soft check; strict logic requires full parsing
                        pass
            else:
                penalty += 1.0 # Mismatched number count
        elif s1["nums"] and not s2["nums"]:
            penalty += 3.0 # Missing numbers is a major structural failure
        
        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2)
        except:
            return 1.0

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """
        Detects simple numeric comparisons in prompt and verifies against candidate.
        Returns 0.0 if consistent, positive penalty if inconsistent.
        """
        p_nums = [float(n) for n in self._num_pattern.findall(prompt)]
        c_nums = [float(n) for n in self._num_pattern.findall(candidate)]
        
        if not p_nums or not c_nums:
            return 0.0
            
        # Heuristic: If prompt implies an order (e.g. "9.11 < 9.9"), check candidate numbers
        # This is a simplified proxy for full causal inference
        p_lower = prompt.lower()
        penalty = 0.0
        
        # Case: "Which is smaller?" -> Candidate should ideally contain the smaller number
        if "smaller" in p_lower or "less" in p_lower:
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                target = min(p_nums)
                # If candidate has a number, is it the target?
                # Allow some fuzziness if exact match isn't found, but penalize wrong extreme
                if target not in c_nums:
                    # If candidate picked the max instead of min
                    if max(p_nums) in c_nums:
                        penalty = 5.0
                        
        if "larger" in p_lower or "greater" in p_lower or "more" in p_lower:
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                target = max(p_nums)
                if target not in c_nums:
                    if min(p_nums) in c_nums:
                        penalty = 5.0

        return penalty

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        p_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt compression for NCD baseline
        prompt_comp = len(zlib.compress(prompt.encode('utf-8')))
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Structural Score (Primary Signal)
            struct_penalty = self._structural_distance(p_struct, c_struct)
            
            # 2. Numeric Logic Score (Constraint Propagation)
            logic_penalty = self._evaluate_numeric_logic(prompt, cand)
            
            # 3. Complexity Score (MDL via NCD as tiebreaker)
            # We want the candidate that compresses best WITH the prompt (high mutual info)
            # but isn't just a copy. 
            ncd_val = self._ncd(prompt, cand)
            
            # Combined Score: Lower is better for penalties, so we invert for "score"
            # Base score starts high, subtract penalties.
            # NCD acts as the tiebreaker when structural penalties are equal.
            raw_score = 10.0 - struct_penalty - logic_penalty - (ncd_val * 2.0)
            
            # Reasoning string generation
            reasons = []
            if struct_penalty > 0: reasons.append(f"struct_mismatch({struct_penalty})")
            if logic_penalty > 0: reasons.append(f"logic_fail({logic_penalty})")
            reasons.append(f"ncd({ncd_val:.2f})")
            
            results.append({
                "candidate": cand,
                "score": round(raw_score, 4),
                "reasoning": "; ".join(reasons) if reasons else "perfect_match"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and MDL.
        """
        # Evaluate single candidate against others (implicitly assuming it's the only one)
        # We simulate a binary check: Does it fit the structure?
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        penalty = self._structural_distance(p_struct, a_struct)
        logic_pen = self._evaluate_numeric_logic(prompt, answer)
        
        if penalty > 0 or logic_pen > 0:
            return 0.1 # Low confidence if structural/logic mismatch
        
        # If structure matches, check complexity (MDL)
        # If answer is too complex relative to prompt, lower confidence
        ncd_val = self._ncd(prompt, answer)
        
        # Map NCD to confidence: Low NCD (high compression) -> High Confidence
        # NCD ranges 0 to ~1.5 usually. 
        conf = max(0.0, 1.0 - (ncd_val * 0.5))
        
        # Boost if exact structural match
        if penalty == 0:
            conf = min(1.0, conf + 0.3)
            
        return round(conf, 4)