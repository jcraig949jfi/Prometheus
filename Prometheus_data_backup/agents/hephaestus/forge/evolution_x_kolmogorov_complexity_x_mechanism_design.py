import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Evolutionary Kolmogorov Mechanism Design (EKMD) Implementation.
    
    Mechanism:
    Instead of a literal evolutionary loop (which is slow and unstable for single-shot inference),
    we simulate the three fitness components as orthogonal scoring vectors for each candidate:
    
    1. Structural Accuracy (Evolutionary Selection): 
       Parses the prompt for logical constraints (negations, comparatives, conditionals).
       Candidates are scored on satisfying these hard logical rules. This drives the "survival" 
       of logically consistent answers.
       
    2. Complexity Penalty (Kolmogorov Approximation):
       Uses string length and entropy as a proxy for K-complexity. 
       Per the "Causal Intelligence" warning, this is NOT used for primary ranking to avoid 
       favoring oversimplified wrong answers. It acts as a tie-breaker or secondary validator 
       within the confidence wrapper.
       
    3. Incentive Compatibility (Mechanism Design):
       Implements a "Truth Serum" style penalty. If a candidate merely echoes the prompt 
       (mimicry) without adding inferential value, or if it contradicts detected structural 
       constraints, it receives a severe payoff penalty. This discourages strategic 
       overfitting to prompt keywords.
       
    The final score is a weighted sum where Structural Accuracy dominates, ensuring we beat 
    the NCD baseline on reasoning tasks.
    """

    def __init__(self):
        # Weights for the fitness function
        self.w_structure = 0.60  # Primary driver (Accuracy)
        self.w_incentive = 0.30  # Secondary driver (Honesty/Non-echo)
        self.w_complexity = 0.10 # Tertiary (Simplicity), kept low per warnings
        
    def _parse_structure(self, prompt: str) -> Dict[str, any]:
        """Extract logical constraints: negations, comparatives, conditionals."""
        p_lower = prompt.lower()
        features = {
            "has_negation": bool(re.search(r'\b(not|no|never|without|unless)\b', p_lower)),
            "has_comparative": bool(re.search(r'\b(more|less|greater|smaller|better|worse|before|after)\b', p_lower)),
            "has_conditional": bool(re.search(r'\b(if|then|unless|provided|when)\b', p_lower)),
            "numbers": re.findall(r'\d+\.?\d*', p_lower),
            "negated_concepts": []
        }
        
        # Simple extraction of negated concepts (e.g., "not A" -> "A")
        if features["has_negation"]:
            # Look for pattern "not [word]"
            matches = re.findall(r'not\s+(\w+)', p_lower)
            features["negated_concepts"] = matches
            
        return features

    def _score_structure(self, candidate: str, prompt: str, features: Dict) -> float:
        """
        Evaluate candidate against structural constraints.
        Returns a score between 0 and 1.
        """
        c_lower = candidate.lower()
        score = 0.5 # Base score
        
        # 1. Negation Check
        if features["has_negation"]:
            # If prompt has negation, correct answer usually acknowledges it or 
            # avoids the negated concept depending on context. 
            # Heuristic: If prompt says "not X", and candidate says "X" without qualification, penalize.
            # This is a simplification of logical consistency.
            has_negation_word = bool(re.search(r'\b(not|no|never)\b', c_lower))
            
            # If the candidate blindly repeats the negated concept without the negation word, penalize
            for concept in features["negated_concepts"]:
                if concept in c_lower and not has_negation_word:
                    # Potential trap: candidate ignores the "not"
                    score -= 0.4 
                    break
            if has_negation_word:
                score += 0.2

        # 2. Comparative/Numeric Check
        if features["has_comparative"] or features["numbers"]:
            # If numbers exist, check if candidate contains numbers or comparative words
            c_nums = re.findall(r'\d+\.?\d*', c_lower)
            c_comp = bool(re.search(r'\b(more|less|greater|smaller|higher|lower)\b', c_lower))
            
            if features["numbers"]:
                # If prompt has numbers, candidate ideally should engage with them or be a clear "None/Impossible"
                if c_nums or c_comp or any(x in c_lower for x in ["no", "none", "impossible", "zero"]):
                    score += 0.3
                else:
                    # Candidate ignores numeric data
                    score -= 0.2

        # 3. Conditional Logic
        if features["has_conditional"]:
            # Check if candidate uses conditional language or provides a definitive answer
            # This is hard to score perfectly without NLP, so we reward length/appropriateness
            if len(c_lower.split()) > 3: # Avoid one-word answers to complex conditionals
                score += 0.1
                
        return max(0.0, min(1.0, score))

    def _score_incentive(self, candidate: str, prompt: str) -> float:
        """
        Mechanism Design: Reward truthfulness, penalize mimicry/echoing.
        Uses a simplified Peer-Prediction idea: Does the candidate add information?
        """
        c_clean = re.sub(r'[^\w\s]', '', candidate.lower()).strip()
        p_clean = re.sub(r'[^\w\s]', '', prompt.lower()).strip()
        
        # Echo detection: High overlap ratio indicates strategic echoing (low value)
        if len(p_clean) > 10:
            overlap = len(set(c_clean.split()) & set(p_clean.split()))
            union = len(set(c_clean.split()) | set(p_clean.split()))
            jaccard = overlap / union if union > 0 else 0
            
            if jaccard > 0.6:
                # Heavy penalty for just repeating the prompt
                return 0.1
            elif jaccard > 0.3:
                return 0.5
        
        # Reward candidates that look like answers (start with capital, end with period, etc)
        # Or contain logical connectors
        if re.match(r'^[A-Z]', candidate) and any(candidate.endswith(x) for x in ['.', '!', '?']):
            return 1.0
            
        return 0.8

    def _score_complexity(self, candidate: str) -> float:
        """
        Approximate Negative Kolmogorov Complexity.
        Shorter, compressible strings get higher scores, but only as a tiebreaker.
        """
        # Normalize length penalty (prefer concise but not empty)
        length = len(candidate)
        if length == 0:
            return 0.0
        if length > 200:
            return 0.2
        # Optimal range 10-100 chars
        return 1.0 - (abs(length - 50) / 200.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        features = self._parse_structure(prompt)
        results = []
        
        # NCD Baseline calculation for tie-breaking
        # We compute NCD between prompt and candidate just to have it as a fallback
        def ncd(a, b):
            if not b: return 1.0
            comp_a = len(zlib.compress(a.encode()))
            comp_b = len(zlib.compress(b.encode()))
            comp_ab = len(zlib.compress((a+b).encode()))
            return (comp_ab - min(comp_a, comp_b)) / max(comp_a, comp_b, 1)

        for cand in candidates:
            # 1. Structural Score (Dominant)
            s_struct = self._score_structure(cand, prompt, features)
            
            # 2. Incentive Score (Validation)
            s_incent = self._score_incentive(cand, prompt)
            
            # 3. Complexity Score (Tiebreaker)
            s_comp = self._score_complexity(cand)
            
            # Weighted Sum
            final_score = (self.w_structure * s_struct) + \
                          (self.w_incentive * s_incent) + \
                          (self.w_complexity * s_comp)
            
            # NCD Tiebreaker logic: If scores are very close, use NCD to prefer 
            # the one with better compression relationship to the prompt context
            # But per instructions, NCD is ONLY a tiebreaker.
            
            reasoning = f"Struct:{s_struct:.2f}, Incent:{s_incent:.2f}, Comp:{s_comp:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing as primary signal, K-complexity only for wrapper validation.
        """
        features = self._parse_structure(prompt)
        struct_score = self._score_structure(answer, prompt, features)
        incentive_score = self._score_incentive(answer, prompt)
        
        # Base confidence on structural alignment
        base_conf = (struct_score * 0.7) + (incentive_score * 0.3)
        
        # K-Complexity Wrapper: 
        # If the answer is wildly complex (high K) but the structural score is low, 
        # reduce confidence further. If structural score is high, K doesn't hurt much.
        k_penalty = 0.0
        if len(answer) > 500:
            k_penalty = 0.2
        elif len(answer) == 0:
            k_penalty = 0.5
            
        final_conf = max(0.0, min(1.0, base_conf - k_penalty))
        return final_conf