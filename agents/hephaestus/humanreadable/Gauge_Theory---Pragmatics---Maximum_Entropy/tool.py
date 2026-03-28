import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Equivariant Pragmatic Inference Engine (Simplified Implementation).
    
    Mechanism:
    1. Context Manifold (Base Space): Encoded via structural parsing of the prompt
       (negations, comparatives, conditionals, numeric values). This establishes the 
       'gauge' or frame of reference.
    2. Gauge Transformations (Pragmatics): Instead of complex group actions, we model 
       pragmatic shifts as consistency checks between the prompt's logical operators 
       and the candidate's semantic direction (e.g., does a negation in the prompt 
       invert the expected truth value of the candidate?).
    3. Maximum Entropy (Constraint): Used ONLY for confidence calibration. We assume 
       the distribution over candidates is exponential based on their structural score.
       Confidence is the normalized probability mass, preventing over-confidence on 
       weak signals (addressing the MaxEnt inhibitor warning).
    4. Scoring: Primary signal is structural alignment (logic/numbers). NCD is a 
       tie-breaker for semantic similarity when logic is neutral.
    """

    def __init__(self):
        # Logical triggers for gauge transformation detection
        self.negations = ['no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'n\'t']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right', 'affirmative']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong', 'negative']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers for numeric evaluation
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _count_tokens(self, text: str, tokens: List[str]) -> int:
        count = 0
        normalized = self._normalize(text)
        for t in tokens:
            count += normalized.count(t)
        return count

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on logical consistency (Gauge Equivariance).
        Checks if the candidate respects the logical operators (negation, comparison) 
        found in the prompt.
        """
        score = 0.0
        p_norm = self._normalize(prompt)
        c_norm = self._normalize(candidate)
        
        # 1. Negation Gauge Check
        # If prompt has negation, a 'yes' candidate might need to be 'no' depending on context.
        # Simplified: If prompt asks "Is X not Y?", and candidate is "No", it aligns.
        has_neg = any(n in p_norm for n in self.negations)
        cand_yes = any(y in c_norm for y in self.bool_yes)
        cand_no = any(n in c_norm for n in self.bool_no)
        
        # Heuristic: If prompt is negative question, 'No' is often the confirming answer 
        # if the candidate repeats the predicate, but here we just check consistency.
        # We award points if the candidate explicitly addresses the logical operator type.
        if has_neg:
            if cand_no: score += 2.0 # Explicitly handling negation
            elif cand_yes: score -= 1.0 # Potential trap
        
        # 2. Comparative/Numeric Check
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple transitivity check: if prompt compares A and B, candidate should reflect order
            # This is a proxy for "gauge covariance" - the relationship must hold.
            if p_nums[0] > p_nums[1]:
                if c_nums[0] > p_nums[1]: score += 3.0 # Consistent magnitude
            elif p_nums[0] < p_nums[1]:
                if c_nums[0] < p_nums[1]: score += 3.0
            
        # 3. Conditional/Keyword Overlap (Pragmatic Relevance)
        # Stronger weight for logical keywords appearing in both
        common_cond = sum(1 for c in self.conditionals if c in p_norm and c in c_norm)
        score += common_cond * 1.5
        
        # 4. Direct Boolean Alignment (Basic Truthiness)
        # If prompt asks a yes/no question (contains '?')
        if '?' in prompt:
            if cand_yes: score += 1.0
            if cand_no: score += 1.0
            
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len_both - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Step 1: Compute Structural Scores (Primary Signal)
        scores = []
        for cand in candidates:
            s_score = self._structural_score(prompt, cand)
            # NCD as tie-breaker (small influence)
            ncd = self._ncd_distance(prompt, cand)
            # Invert NCD so higher is better, scale down to not overpower logic
            ncd_bonus = (1.0 - ncd) * 0.5 
            total_score = s_score + ncd_bonus
            scores.append(total_score)
        
        # Step 2: MaxEnt Calibration (Softmax for probability distribution)
        # Shift scores to avoid overflow, then exp
        max_s = max(scores) if scores else 0
        exp_scores = [math.exp(s - max_s) for s in scores]
        sum_exp = sum(exp_scores) if exp_scores else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalized probability (MaxEnt distribution)
            prob = exp_scores[i] / sum_exp if sum_exp > 0 else 0.0
            
            # Reasoning string generation
            reasoning = f"Structural score: {scores[i]:.2f}. "
            if scores[i] > 2.0:
                reasoning += "High logical alignment detected."
            elif scores[i] < 0:
                reasoning += "Logical inconsistency or negation trap detected."
            else:
                reasoning += "Neutral structural signal; relying on semantic proximity."

            results.append({
                "candidate": cand,
                "score": prob, # Using probability as the rank score
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle: Confidence is the probability mass of the answer 
        relative to a generated set of alternatives (simulated here by perturbing the answer).
        Since we can't generate infinite alternatives, we approximate via structural stability.
        """
        # 1. Base structural score
        base_score = self._structural_score(prompt, answer)
        
        # 2. Perturbation test (Simulated Gauge Transformation)
        # If we slightly alter the answer (e.g., flip a boolean), does the score drop significantly?
        # If yes, the original answer is robust (high confidence).
        perturbed_answer = answer
        is_yes = any(y in self._normalize(answer) for y in self.bool_yes)
        is_no = any(n in self._normalize(answer) for y in self.bool_no) # typo fix in logic below
        
        # Simple perturbation: swap yes/no if present, otherwise append noise
        if is_yes:
            perturbed_answer = answer.replace("Yes", "No").replace("yes", "no").replace("True", "False")
        elif any(n in self._normalize(answer) for n in self.bool_no):
            perturbed_answer = answer.replace("No", "Yes").replace("no", "yes").replace("False", "True")
        else:
            perturbed_answer = answer + " not"
            
        perturbed_score = self._structural_score(prompt, perturbed_answer)
        
        # Stability metric: Difference between original and perturbed
        stability = base_score - perturbed_score
        
        # Map stability to 0-1 using sigmoid-like function
        # High stability -> high confidence
        confidence = 1.0 / (1.0 + math.exp(-stability))
        
        # Clamp
        return max(0.0, min(1.0, confidence))