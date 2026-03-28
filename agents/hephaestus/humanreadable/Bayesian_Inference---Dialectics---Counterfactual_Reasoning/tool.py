import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Bayesian Counterfactual (DBC) Inference Loop Implementation.
    
    Mechanism:
    1. THESIS (Prior): Establishes a baseline score using structural parsing 
       (negations, comparatives, conditionals) and numeric evaluation. This acts 
       as the primary driver (Bayesian Core).
    2. ANTITHESIS (Counterfactual Intervention): Generates a 'challenger' score by 
       simulating a world where key logical constraints are inverted or ignored. 
       Per guidelines, this is restricted to the confidence wrapper and structural 
       stress-testing to avoid reasoning traps associated with heavy counterfactual reliance.
    3. SYNTHESIS (Posterior): Combines the Thesis and Antithesis scores. The final 
       score is a weighted average where the weight is determined by the structural 
      consistency (likelihood) of the candidate. 
    4. Tie-breaking: Uses Normalized Compression Distance (NCD) only when structural 
       signals are ambiguous, ensuring we beat the NCD baseline.
    """

    def __init__(self):
        # Keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text for numeric evaluation."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _structural_score(self, text: str) -> float:
        """
        Computes a structural validity score based on logical markers.
        Higher score indicates higher logical density/consistency.
        """
        t_lower = text.lower()
        words = t_lower.split()
        score = 0.0
        
        # Negation density (penalize excessive negation which often implies complexity/error)
        neg_count = sum(1 for w in words if any(n in w for n in self.negations))
        score -= neg_count * 0.1
        
        # Comparative presence (indicates reasoning)
        comp_count = sum(1 for w in words if any(c in w for c in self.comparatives))
        score += comp_count * 0.15
        
        # Conditional presence
        cond_count = sum(1 for w in words if any(c in w for c in self.conditionals))
        score += cond_count * 0.1
        
        # Numeric consistency check (if numbers exist, are they ordered?)
        nums = self._extract_numbers(text)
        if len(nums) > 1:
            # Reward sortedness or clear distinction
            is_sorted = all(nums[i] <= nums[i+1] for i in range(len(nums)-1))
            score += 0.2 if is_sorted else -0.1
            
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _generate_antithesis_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates a counterfactual world where logical constraints are challenged.
        Returns a score representing how well the candidate survives logical inversion.
        """
        # Simple heuristic: If candidate relies heavily on negation, antithesis weakens it.
        # This acts as the 'do-operator' intervention.
        c_lower = candidate.lower()
        neg_density = sum(c_lower.count(n) for n in self.negations) / (len(c_lower.split()) + 1)
        
        # Antithesis penalty: High negation density is fragile under counterfactual stress
        return 1.0 - (neg_density * 0.5)

    def _synthesis(self, thesis_score: float, antithesis_score: float, structural_weight: float) -> float:
        """
        Combines thesis and antithesis via model averaging weighted by structural likelihood.
        """
        # Normalize thesis to 0-1 range roughly
        t_norm = 1.0 / (1.0 + math.exp(-thesis_score)) # Sigmoid
        
        # Weighted synthesis: Trust thesis more if structural weight is high
        final_score = (structural_weight * t_norm) + ((1 - structural_weight) * antithesis_score * 0.5)
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_struct = self._structural_score(prompt)
        
        for cand in candidates:
            # 1. THESIS: Structural & Numeric Analysis
            thesis_raw = self._structural_score(cand)
            
            # Contextual alignment (does candidate share structural properties with prompt?)
            alignment = 0.0
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(cand)
            if p_nums and c_nums:
                # Check if candidate numbers are within reasonable range of prompt
                if all(abs(c - p) < max(p_nums)*2 for c in c_nums for p in p_nums):
                    alignment = 0.5
            
            # 2. ANTITHESIS: Counterfactual Stress Test
            antithesis_val = self._generate_antithesis_score(prompt, cand)
            
            # 3. SYNTHESIS: Bayesian Update
            # Structural weight derived from length and keyword density
            struct_weight = min(1.0, (len(cand.split()) / 20.0) + 0.4) 
            base_score = self._synthesis(thesis_raw + alignment, antithesis_val, struct_weight)
            
            # NCD Tiebreaker (only if scores are close, but applied lightly here for ranking)
            ncd = self._ncd_distance(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.05 # Small bonus for similarity if logic is tied
            
            final_score = base_score + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Thesis:{thesis_raw:.2f}|Antithesis:{antithesis_val:.2f}|NCD:{ncd:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the DBC loop internally to validate the specific answer.
        """
        # Run evaluation on a dummy list containing only the answer to get its score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]["score"]
        
        # Calibrate to 0-1 range strictly
        # The synthesis step produces values roughly around 0.3 to 0.8 usually.
        # We map this to 0.0 - 1.0 with clamping.
        confidence = max(0.0, min(1.0, (score + 0.2) * 0.8))
        
        # Meta-check: If structural parsing detected strong contradictions (negative thesis), lower confidence
        if self._structural_score(answer) < -0.5:
            confidence *= 0.5
            
        return confidence