import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Tuning Emergent Rule-Space Explorer (Approximated).
    
    Mechanism:
    1. Structural Parsing (The "Loss Function L"): Extracts logical constraints 
       (negations, comparatives, conditionals) from the prompt. Candidates are 
       scored by how well they satisfy these structural constraints.
    2. Dynamical Stability (The "Lyapunov Regularizer"): Treats the candidate's 
       logical consistency as a dynamical system. We simulate a simple trajectory 
       where the state is the candidate's semantic alignment with extracted constraints.
       If small perturbations in the input (simulated via noise injection in the 
       constraint matching score) lead to large deviations in the output score, 
       the candidate is deemed "chaotic" (high Lyapunov exponent) and penalized.
    3. Emergence: The final score emerges from the interplay between satisfying 
       the prompt's structure (Loss) and maintaining stability under perturbation.
    4. NCD Tiebreaker: Used only if structural scores are identical.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "n't"}
        self.comparative_ops = {">", "<", "greater", "less", "more", "fewer", "larger", "smaller"}
        self.conditional_words = {"if", "then", "unless", "otherwise", "provided"}

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical signatures from text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparative_ops) or bool(re.search(r'\d+\s*(<|>|=)\s*\d+', lower_text))
        has_conditional = bool(words & self.conditional_words)
        
        # Numeric extraction
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', lower_text)]
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "numbers": numbers,
            "length": len(text),
            "word_set": words
        }

    def _compute_structural_loss(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Compute L(theta): Mismatch between prompt constraints and candidate properties.
        Lower is better.
        """
        loss = 0.0
        
        # Constraint 1: Negation consistency (simplified heuristic)
        # If prompt has strong negation, candidate should ideally reflect logic (hard to check without NLP)
        # Instead, we check for contradiction in simple numeric comparisons if present
        if prompt_struct["comparative"] and cand_struct["comparative"]:
            # If both have numbers, check consistency
            p_nums = prompt_struct["numbers"]
            c_nums = cand_struct["numbers"]
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Heuristic: Candidate number should relate logically to prompt numbers
                # This is a proxy for "answering the question"
                pass 

        # Penalty for length mismatch (proxy for completeness)
        if prompt_struct["length"] > 20 and cand_struct["length"] < 2:
            loss += 0.5 # Too short for complex prompt
            
        return loss

    def _estimate_lyapunov(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Estimate lambda_max: Sensitivity of the score to small perturbations.
        We perturb the 'structural perception' slightly. If the score changes wildly,
        the hypothesis (candidate) is unstable (chaotic).
        """
        epsilon = 0.1
        perturbations = 3
        scores = [base_score]
        
        # Simulate perturbation by altering the candidate string slightly (typo simulation)
        # and re-evaluating structural overlap.
        cand_list = list(candidate)
        if len(cand_list) == 0:
            return 1.0 # High instability for empty
            
        for i in range(perturbations):
            # Create a perturbed version
            idx = i % len(cand_list)
            original_char = cand_list[idx]
            cand_list[idx] = ' ' if original_char != ' ' else 'x'
            perturbed_cand = "".join(cand_list)
            
            # Re-evaluate structure
            p_struct = self._extract_structure(prompt)
            c_struct = self._extract_structure(perturbed_cand)
            
            # Quick re-score (simplified)
            pert_score = 0.0
            if p_struct["negation"] == c_struct["negation"]: pert_score += 0.2
            if p_struct["comparative"] == c_struct["comparative"]: pert_score += 0.2
            # NCD component for perturbed
            ncd = self._ncd(prompt, perturbed_cand)
            pert_score += (1.0 - ncd) * 0.6
            
            scores.append(pert_score)
            
            # Restore
            cand_list[idx] = original_char

        # Calculate max divergence (approximating Lyapunov exponent)
        if len(scores) < 2:
            return 0.0
        
        diffs = [abs(scores[i] - scores[i-1]) for i in range(1, len(scores))]
        return max(diffs) if diffs else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd = max(s[1] for s in ncd_scores)
        ncd_range = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Loss (L)
            # Reward matching structural features
            score = 0.0
            if prompt_struct["negation"] == cand_struct["negation"]: score += 0.3
            if prompt_struct["comparative"] == cand_struct["comparative"]: score += 0.3
            if prompt_struct["conditional"] == cand_struct["conditional"]: score += 0.2
            
            # Numeric consistency check (simple presence)
            if prompt_struct["numbers"] and cand_struct["numbers"]:
                score += 0.2
            elif not prompt_struct["numbers"]:
                score += 0.1 # Neutral if no numbers needed
                
            # 2. Lyapunov Regularization (Stability)
            # Penalize if small changes cause large score swings
            lyap = self._estimate_lyapunov(prompt, cand, score)
            stability_penalty = 0.5 * lyap # Beta * lambda
            
            final_score = score - stability_penalty
            
            # Normalize NCD to use as tiebreaker (lower NCD is better, so subtract)
            # But we want higher score = better. So: - (ncd - min) / range
            normalized_ncd = (self._ncd(prompt, cand) - min_ncd) / ncd_range
            final_score -= normalized_ncd * 0.01 # Very small weight, strictly tiebreaker

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {score:.2f}, Stability penalty: {stability_penalty:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on structural alignment and stability."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map score to 0-1 confidence
        # Base score is roughly 0.0 to 1.0 range from our heuristics
        score = res[0]["score"]
        confidence = max(0.0, min(1.0, (score + 0.5) / 1.5)) # Simple scaling
        return confidence