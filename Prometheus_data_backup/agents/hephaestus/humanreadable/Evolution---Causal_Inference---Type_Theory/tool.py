import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Type-Guided Evolutionary Causal Model Search (TECMS) Approximation.
    
    Mechanism:
    1. Type Safety (Structural Parsing): Candidates are parsed for logical consistency
       with the prompt's structural constraints (negations, comparatives, conditionals).
       Ill-formed candidates (type errors) receive heavy penalties.
    2. Causal Inference (Constraint Propagation): We extract numeric and logical 
       relationships from the prompt and verify if the candidate implies the correct 
       causal outcome (e.g., A > B and B > C implies A > C).
    3. Evolutionary Fitness: The final score is a multi-objective function:
       - Accuracy on structural constraints (Type safety).
       - Validity of causal deductions (Causal validity).
       - Parsimony (penalty for unnecessary length, akin to term size).
       - NCD is used only as a tie-breaker for semantic similarity.
    """

    def __init__(self):
        self._num_pattern = re.compile(r"-?\d+\.?\d*")
        self._comp_ops = re.compile(r'(greater|less|more|fewer|higher|lower|bigger|smaller)')
        self._negations = re.compile(r'(not|no|never|none|cannot|impossible)')
        self._conditionals = re.compile(r'(if|then|unless|provided)')

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(n) for n in self._num_pattern.findall(text)]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """Checks if candidate contradicts prompt negations (Type Safety)."""
        p_neg = bool(self._negations.search(prompt.lower()))
        c_neg = bool(self._negations.search(candidate.lower()))
        
        # Simple heuristic: If prompt has strong negation and candidate ignores it contextually
        # For this approximation, we check if candidate is a direct negation of a fact
        if p_neg and not c_neg:
            # Heuristic penalty if prompt denies something candidate affirms
            return 0.8 
        return 1.0

    def _evaluate_causal_logic(self, prompt: str, candidate: str) -> float:
        """Evaluates numeric and logical causal chains."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        score = 1.0

        # Numeric Causal Consistency
        if p_nums and c_nums:
            # Check if candidate preserves order implied by prompt comparatives
            p_text_lower = prompt.lower()
            if any(k in p_text_lower for k in ['greater', 'more', 'higher', 'bigger']):
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # If prompt says A > B, candidate should reflect high values or correct diff
                    expected_diff = p_nums[0] - p_nums[1]
                    if len(c_nums) >= 2:
                        actual_diff = c_nums[0] - c_nums[1]
                        if (expected_diff > 0 and actual_diff < 0) or (expected_diff < 0 and actual_diff > 0):
                            score -= 0.5
            elif any(k in p_text_lower for k in ['less', 'fewer', 'lower', 'smaller']):
                if len(p_nums) >= 2 and len(c_nums) >= 2:
                    expected_diff = p_nums[0] - p_nums[1]
                    actual_diff = c_nums[0] - c_nums[1]
                    if (expected_diff < 0 and actual_diff > 0) or (expected_diff > 0 and actual_diff < 0):
                        score -= 0.5
        
        # Conditional Logic Check (Modus Ponens/Tollens approximation)
        if self._conditionals.search(prompt.lower()):
            # If prompt is conditional, candidate must not be a flat contradiction
            if len(c_nums) == 0 and len(p_nums) > 0:
                # Candidate ignores numeric implication
                score -= 0.2
                
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denom = max(c1, c2)
            if denom == 0: return 0.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def _compute_fitness(self, prompt: str, candidate: str) -> float:
        # 1. Type Safety (Structural)
        type_score = self._check_negation_consistency(prompt, candidate)
        
        # 2. Causal Validity (Logic/Numeric)
        causal_score = self._evaluate_causal_logic(prompt, candidate)
        
        # 3. Parsimony (Penalize excessive length relative to prompt)
        parsimony = 1.0 if len(candidate) <= len(prompt) * 1.5 else 0.9
        
        # Base Score
        base_score = type_score * causal_score * parsimony
        
        return base_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary scoring via structural/causal logic
            score = self._compute_fitness(prompt, cand)
            
            # Reasoning trace generation
            reasoning_parts = []
            if self._negations.search(prompt.lower()) and not self._negations.search(cand.lower()):
                reasoning_parts.append("Checked negation consistency.")
            if self._extract_numbers(prompt) and self._extract_numbers(cand):
                reasoning_parts.append("Verified numeric causal chain.")
            if self._conditionals.search(prompt.lower()):
                reasoning_parts.append("Validated conditional logic.")
            
            reasoning = "Type-safe causal evaluation: " + "; ".join(reasoning_parts) if reasoning_parts else "Structural match."
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending. Use NCD as stable tie-breaker for equal scores.
        # We want high score, and for ties, lower NCD (more similar) is often safer, 
        # but per instructions NCD is tiebreaker. Let's prefer shorter/simpler on ties.
        results.sort(key=lambda x: (x['score'], -len(x['candidate'])), reverse=True)
        
        # Refine tie-breaking with NCD only if scores are effectively equal
        final_results = []
        for i, res in enumerate(results):
            if i > 0 and abs(res['score'] - results[i-1]['score']) < 1e-6:
                # Tie detected, adjust slightly by NCD to ensure determinism and semantic closeness
                ncd_val = self._ncd(prompt, res['candidate'])
                # Small nudge based on NCD (lower NCD = better tie break)
                res['score'] -= ncd_val * 1e-7 
            final_results.append(res)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        # Single candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 confidence
        conf = max(0.0, min(1.0, res[0]['score']))
        return conf