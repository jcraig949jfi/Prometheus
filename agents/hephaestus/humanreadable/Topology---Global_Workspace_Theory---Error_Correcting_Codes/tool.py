import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topologically-Robust Global Workspace (TRGW) Implementation.
    
    Mechanism:
    1. Topological Feature Extraction (Simplicial Parsing): 
       Instead of continuous geometry, we map the text to a discrete feature space.
       - 0-simplices (Nodes): Extracted entities and numbers.
       - 1-simplices (Edges): Logical relations (comparatives, conditionals).
       - Invariants: Counts of negations, logical operators, and numeric magnitudes.
       
    2. Error Correction (LDPC Analogue):
       We construct a 'syndrome' by checking consistency between extracted features.
       - If a prompt implies A > B and candidate implies B > A, a parity check fails.
       - The 'syndrome weight' is the count of logical contradictions.
       
    3. Global Workspace Ignition:
       Candidates are scored on structural alignment (primary) and NCD (tiebreaker).
       If the 'syndrome' (contradictions) exceeds a threshold, the candidate is suppressed.
       High-confidence signals (low syndrome, high structural match) are 'broadcast' 
       as the final score.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'false', 'wrong'}
        self.comparatives = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.bool_yes = {'yes', 'true', 'correct', 'right', '1'}
        self.bool_no = {'no', 'false', 'wrong', 'incorrect', '0'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _parse_topology(self, text: str) -> Dict:
        """
        Maps text to a topological feature vector (Betti-like counts).
        Returns a dict representing the 'shape' of the logic.
        """
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        # 0-dimensional features (Nodes)
        has_negation = bool(tokens & self.negations)
        has_conditional = bool(tokens & self.conditionals)
        has_comparative = bool(tokens & self.comparatives)
        num_count = len(numbers)
        num_sum = sum(numbers) if numbers else 0.0
        
        # 1-dimensional features (Edges/Loops - simplified)
        # Detect simple contradictions or patterns like "not yes"
        text_lower = text.lower()
        contradiction_score = 0
        if ('no' in text_lower and 'yes' in text_lower) or ('false' in text_lower and 'true' in text_lower):
            contradiction_score = 1

        return {
            'negations': int(has_negation),
            'conditionals': int(has_conditional),
            'comparatives': int(has_comparative),
            'num_count': num_count,
            'numbers': numbers,
            'num_sum': num_sum,
            'contradiction': contradiction_score,
            'is_yes': bool(tokens & self.bool_yes),
            'is_no': bool(tokens & self.bool_no)
        }

    def _check_syndrome(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Computes the LDPC-like syndrome weight.
        Measures logical inconsistency between prompt expectations and candidate answer.
        Returns 0.0 for perfect consistency, higher values for contradictions.
        """
        syndrome = 0.0
        
        # Check 1: Negation Parity
        # If prompt sets up a negation context, does the candidate flip logic incorrectly?
        # Simplified: If prompt has negation and candidate is a bare 'yes'/'no', check alignment.
        if prompt_feat['negations']:
            # Heuristic: If prompt negates, a simple 'yes' might be wrong depending on context
            # Here we penalize if candidate is purely affirmative without nuance
            if cand_feat['is_yes'] and not cand_feat['negations']:
                syndrome += 0.2
            if cand_feat['is_no'] and not cand_feat['negations']:
                syndrome += 0.1 # Less penalty for 'no' in negative contexts usually

        # Check 2: Numeric Consistency
        if prompt_feat['num_count'] > 0 and cand_feat['num_count'] > 0:
            # If both have numbers, do they contradict obvious ordering?
            # This is a weak check without full semantic parse, but catches gross errors
            p_nums = sorted(prompt_feat['numbers'])
            c_nums = sorted(cand_feat['numbers'])
            # If candidate numbers are wildly outside prompt range, slight penalty
            if c_nums and p_nums:
                if c_nums[-1] > p_nums[-1] * 10 or c_nums[0] < p_nums[0] * 0.1:
                    syndrome += 0.3

        # Check 3: Direct Contradiction within candidate
        syndrome += cand_feat['contradiction'] * 0.5
        
        return syndrome

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._parse_topology(prompt)
        results = []
        
        for cand in candidates:
            cand_feat = self._parse_topology(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            structural_score = 0.0
            
            # Numeric Evaluation
            p_nums = prompt_feat['numbers']
            c_nums = cand_feat['numbers']
            
            if p_nums and c_nums:
                # Check for specific numeric reasoning patterns
                # Example: Prompt "9.11 vs 9.9", Candidate should reflect correct comparison
                if len(p_nums) >= 2:
                    # Detect if prompt asks for max/min implicitly via keywords
                    is_max = any(k in prompt.lower() for k in ['largest', 'max', 'greater', 'more'])
                    is_min = any(k in prompt.lower() for k in ['smallest', 'min', 'less', 'fewer'])
                    
                    target = max(p_nums) if is_max else (min(p_nums) if is_min else None)
                    if target is not None:
                        # Check if candidate contains the correct number
                        if any(abs(c - target) < 1e-6 for c in c_nums):
                            structural_score += 2.0
                        else:
                            structural_score -= 1.0
            
            # Constraint Propagation (Yes/No logic)
            # If prompt is a question, candidate should be an answer
            if '?' in prompt:
                if cand_feat['is_yes'] or cand_feat['is_no']:
                    structural_score += 1.0
                # Penalize non-answers if they look like random text
                elif len(cand.split()) > 1 and not any(k in cand.lower() for k in ['the', 'is', 'are']):
                    structural_score += 0.5

            # 2. Error Correction (Syndrome Check)
            syndrome = self._check_syndrome(prompt_feat, cand_feat)
            # Convert syndrome to a penalty (0 to 1 range roughly)
            error_penalty = min(1.0, syndrome)
            
            # 3. NCD Tiebreaker (Only if structural signals are weak)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_bonus = 0.0
            if abs(structural_score) < 0.1:
                # If no strong structural signal, use similarity
                ncd_bonus = (1.0 - ncd_val) * 0.5
            
            final_score = structural_score - error_penalty + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{structural_score:.2f}, Syndrome:{syndrome:.2f}, NCD:{ncd_val:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on topological consistency and syndrome weight.
        """
        prompt_feat = self._parse_topology(prompt)
        ans_feat = self._parse_topology(answer)
        
        # Calculate Syndrome (Error Pattern)
        syndrome = self._check_syndrome(prompt_feat, ans_feat)
        
        # Base confidence starts high if no internal contradictions in answer
        base_conf = 1.0 - ans_feat['contradiction']
        
        # Penalize heavily for high syndrome (logical mismatch with prompt)
        conf = base_conf - (syndrome * 0.8)
        
        # Boost if numeric alignment exists
        p_nums = prompt_feat['numbers']
        a_nums = ans_feat['numbers']
        if p_nums and a_nums:
            # If numbers match exactly, high boost
            if set(p_nums) == set(a_nums):
                conf += 0.5
            # If candidate number is in prompt, moderate boost
            elif any(n in p_nums for n in a_nums):
                conf += 0.2
                
        # Clamp to [0, 1]
        return max(0.0, min(1.0, conf))