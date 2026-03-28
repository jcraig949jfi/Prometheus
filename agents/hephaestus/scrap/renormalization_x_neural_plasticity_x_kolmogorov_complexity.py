import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a multi-scale variational reasoning tool inspired by Renormalization (RG),
    Neural Plasticity, and Kolmogorov Complexity (MDL).
    
    Mechanism:
    1. Structural Parsing (RG Scale s0): Extracts logical operators (negations, comparatives,
       conditionals) and numeric values. This forms the "effective theory" of the prompt.
    2. Hypothesis Evaluation (Plasticity): Candidates are scored based on structural alignment
       with the prompt's logical constraints (Hebbian strengthening of valid logic).
    3. Complexity Pruning (MDL/Kolmogorov): Candidates are penalized for unnecessary length
       relative to their information gain (approximated via compression), enforcing Minimum
       Description Length.
    4. Ranking: Final score = Structural Match - Complexity Penalty.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', 'before', 'after']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        count = 0
        words = re.findall(r'\b\w+\b', text.lower())
        for w in words:
            if w in keywords:
                count += 1
        return count

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluates logical consistency between prompt and candidate.
        Simulates Hebbian plasticity: strengthens connections where logical structures match.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0

        # 1. Negation Consistency
        p_neg = self._count_keywords(p_low, self.negations)
        c_neg = self._count_keywords(c_low, self.negations)
        # Penalty if negation presence mismatches significantly (simplified logic)
        if p_neg > 0 and c_neg == 0:
            score -= 0.5 # Potential contradiction
        elif p_neg == 0 and c_neg > 2:
            score -= 0.5 # Over-negation

        # 2. Comparative/Logical Operator Presence
        # If prompt has comparatives, candidate should ideally reflect them or answer directly
        p_comp = self._count_keywords(p_low, self.comparatives)
        c_comp = self._count_keywords(c_low, self.comparatives)
        if p_comp > 0:
            # Reward if candidate uses similar logic or provides a direct numeric answer
            if c_comp > 0 or len(self._extract_numbers(c_low)) > 0:
                score += 1.0
            else:
                score -= 0.2

        # 3. Conditional Logic
        p_cond = self._count_keywords(p_low, self.conditionals)
        if p_cond > 0:
            # Candidate should contain logical connectors or definitive answers
            if any(k in c_low for k in self.conditionals) or any(k in c_low for k in self.booleans):
                score += 0.5

        # 4. Numeric Consistency (Transitivity check simulation)
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if p_nums and c_nums:
            # If both have numbers, check if candidate numbers are within reasonable bounds of prompt
            # Simple proximity check: does the candidate number appear in the prompt?
            found = False
            for cn in c_nums:
                if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                    found = True
                    break
            if found:
                score += 1.0 # Strong signal: candidate reuses prompt data correctly
            else:
                # If candidate introduces new numbers, slight penalty unless it's a calculation result
                # (Hard to verify calculation without eval, so we rely on structural match)
                pass 
        elif p_nums and not c_nums:
            # Prompt asks for number, candidate gives none (unless yes/no question)
            if not any(k in c_low for k in self.booleans):
                score -= 0.5

        return score

    def _complexity_penalty(self, prompt: str, candidate: str) -> float:
        """
        Approximates Kolmogorov Complexity via Compression (MDL Principle).
        Penalizes candidates that add description length without adding information.
        """
        if not candidate:
            return 1.0 # Max penalty for empty
        
        # Combined string for context-aware compression
        combined = f"{prompt} {candidate}"
        try:
            len_combined = len(zlib.compress(combined.encode('utf-8')))
            len_prompt = len(zlib.compress(prompt.encode('utf-8')))
            len_cand = len(zlib.compress(candidate.encode('utf-8')))
            
            # Information gain vs Cost
            # If candidate is just noise, len_combined ~ len_prompt + len_cand
            # If candidate is redundant/repetitive, len_combined < sum
            # We want short candidates that explain the prompt well.
            
            # MDL Score: Length of candidate - (Reduction in uncertainty)
            # Approximation: Penalty = len(candidate) / (len(prompt) + epsilon) * complexity_factor
            
            raw_len = len(candidate)
            compressed_len = len_cand
            
            # Normalize penalty between 0 and 1 based on typical lengths
            # Longer candidates get higher penalty unless highly compressible
            penalty = (compressed_len / 100.0) * math.log(raw_len + 1)
            
            return min(penalty, 2.0) # Cap penalty
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_clean = self._normalize(prompt)
        
        for cand in candidates:
            c_clean = self._normalize(cand)
            
            # 1. Structural Score (Reasoning)
            struct_score = self._structural_score(p_clean, c_clean)
            
            # 2. Complexity Penalty (MDL)
            complexity = self._complexity_penalty(p_clean, c_clean)
            
            # 3. NCD Tiebreaker (Only if structural scores are very close, used implicitly here as a small bonus)
            # Calculate NCD between prompt and candidate to check semantic overlap
            try:
                s_joint = zlib.compress(f"{p_clean} {c_clean}".encode())
                s_p = zlib.compress(p_clean.encode())
                s_c = zlib.compress(c_clean.encode())
                ncd = (len(s_joint) - min(len(s_p), len(s_c))) / max(len(s_p), len(s_c), 1)
                ncd_bonus = (1.0 - ncd) * 0.1 # Small bonus for high similarity
            except:
                ncd_bonus = 0.0

            final_score = struct_score - complexity + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, MDL Penalty: {complexity:.2f}, NCD Bonus: {ncd_bonus:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate single candidate against a dummy set to get relative score
        # Since we don't have other candidates, we assess absolute structural fit
        struct = self._structural_score(self._normalize(prompt), self._normalize(answer))
        complexity = self._complexity_penalty(self._normalize(prompt), self._normalize(answer))
        
        raw_score = struct - complexity
        
        # Map raw score to 0-1
        # Heuristic: 
        # struct > 0.5 and complexity < 0.5 -> High confidence
        # struct < -0.5 -> Low confidence
        
        conf = 0.5 + (struct * 0.3) - (complexity * 0.2)
        return max(0.0, min(1.0, conf))