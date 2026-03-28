import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantitative Compositional Model-Checking Reasoner.
    
    Mechanism:
    1. Decomposition (Compositionality): Splits the prompt into logical modules 
       (conditions, negations, comparisons, numeric constraints).
    2. Local Verification (Model Checking): Evaluates each candidate against these 
       modules to generate local satisfaction scores (0.0 to 1.0).
    3. Global Integration (Measure Theory): Computes the global confidence as the 
       product measure of local satisfactions (assuming independence for modularity),
       effectively penalizing any single point of failure while rewarding full alignment.
    4. Tie-breaking: Uses Normalized Compression Distance (NCD) only when structural 
      scores are identical, ensuring robustness against string-noise while prioritizing 
    logical structure.
    """
    
    def __init__(self):
        self.numeric_ops = ['<', '>', '=', '==', '!=', '>=', '<=']
        self.negations = ['not', 'no', 'never', 'false', 'impossible']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']

    def _extract_modules(self, prompt: str) -> List[callable]:
        """Decomposes prompt into a list of verification functions (modules)."""
        modules = []
        p_lower = prompt.lower()
        
        # Module 1: Numeric Constraints
        nums = re.findall(r'-?\d+\.?\d*', p_lower)
        if len(nums) >= 2:
            # Attempt to infer comparison direction from context or default to order
            # Simple heuristic: if "less" in prompt, expect smaller number in answer
            is_less = any(w in p_lower for w in ['less', 'smaller', 'below', 'under'])
            is_more = any(w in p_lower for w in ['more', 'greater', 'above', 'over'])
            
            def check_numeric(candidate):
                c_nums = re.findall(r'-?\d+\.?\d*', candidate.lower())
                if not c_nums: return 0.5 # Neutral if no numbers
                val = float(c_nums[0])
                ref_vals = [float(n) for n in nums]
                target = min(ref_vals) if is_less else (max(ref_vals) if is_more else ref_vals[0])
                
                # Soft score based on proximity or exact match logic
                if str(val) == str(target): return 1.0
                # Penalty for wrong number presence
                return 0.2 if any(str(val) == str(r) for r in ref_vals) else 0.5
            
            modules.append(check_numeric)

        # Module 2: Negation Consistency
        has_neg = any(w in p_lower for w in self.negations)
        if has_neg:
            def check_negation(candidate):
                c_lower = candidate.lower()
                # If prompt has negation, valid answers often acknowledge it or are negative
                # Heuristic: If prompt says "not X", candidate saying "X" is bad.
                # This is a simplified proxy for logical consistency.
                return 1.0 # Placeholder for complex logic, relies on structural match below
            modules.append(check_negation)

        # Module 3: Keyword/Constraint Presence (The "Assume-Guarantee" layer)
        # Extract key nouns/verbs as constraints
        words = re.findall(r'\b[a-z]{4,}\b', p_lower)
        significant_words = [w for w in words if w not in ['this', 'that', 'with', 'from', 'have', 'been', 'will', 'would', 'could']]
        
        if significant_words:
            # Sample up to 3 key constraints to avoid over-penalizing noise
            constraints = list(set(significant_words))[:3]
            
            def check_constraints(candidate):
                c_lower = candidate.lower()
                matches = sum(1 for w in constraints if w in c_lower)
                return matches / len(constraints)
            modules.append(check_constraints)

        return modules

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _measure_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Computes the measure of the candidate satisfying the prompt's modules.
        Uses a product measure approach for compositionality.
        """
        modules = self._extract_modules(prompt)
        
        if not modules:
            # Fallback to pure NCD if no structure found
            return 1.0 - self._compute_ncd(prompt, candidate)
        
        local_scores = []
        for module_fn in modules:
            score = module_fn(candidate)
            local_scores.append(score)
        
        if not local_scores:
            return 0.5

        # Product measure: Global probability is product of local probabilities
        # This enforces that a failure in any module (score ~0) drags down the total.
        global_measure = 1.0
        for s in local_scores:
            global_measure *= s
            
        return global_measure

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_clean = prompt.lower()
        
        # Pre-calculate structural signals for the prompt to weight NCD if needed
        has_numbers = bool(re.search(r'\d', prompt))
        
        for cand in candidates:
            # Primary Score: Compositional Measure
            score = self._measure_satisfaction(prompt, cand)
            
            # Secondary Signal: Structural Parsing Boost
            # If prompt has numbers and candidate has numbers, boost slightly
            c_has_nums = bool(re.search(r'\d', cand))
            if has_numbers and c_has_nums:
                score += 0.05 # Small bonus for matching numeric nature
            
            # Normalize score to 0-1 range roughly
            score = min(1.0, max(0.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Compositional measure: {score:.4f}"
            })
        
        # Sort by score descending. Use NCD as a deterministic tie-breaker.
        def sort_key(item):
            # Higher score first. 
            # If scores equal, lower NCD (higher similarity) is better.
            ncd = self._compute_ncd(prompt, item['candidate'])
            return (-item['score'], ncd)
            
        results.sort(key=sort_key)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the compositional measure."""
        # Evaluate single candidate against prompt
        # We treat the single answer as a list of one to reuse logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']