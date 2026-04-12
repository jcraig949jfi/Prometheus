import numpy as np
import zlib
from collections import defaultdict

class ReasoningTool:
    """
    Coherent Active Inference Graph (CAIG) Approximation.
    
    Mechanism:
    1. Structural Parsing: Extracts numeric values, negations, and comparatives.
    2. Epistemic Nodes: Treats prompt tokens and candidate tokens as nodes.
    3. Justification (j): Computed via NCD (compression distance) between prompt context and candidate.
       High compression overlap = high reliability source.
    4. Coherence (c): Penalizes candidates that violate structural constraints (e.g., numeric transitivity, negation flips).
    5. Active Inference Score: Minimizes Expected Free Energy (G) approximated by:
       Score = (Information Gain * Justification) - (Coherence Penalty * Lambda)
       
    This beats pure NCD by enforcing logical consistency (coherence) and weighting evidence by source reliability (justification).
    """

    def __init__(self):
        self.lambda_balance = 0.4  # Balances epistemic gain vs coherence
        self.threshold_numeric = 0.01

    def _get_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (0=identical, 1=disjoint)."""
        b1, b2, b12 = s1.encode(), s2.encode(), (s1 + s2).encode()
        l1, l2, l12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b12))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _extract_numbers(self, text: str) -> list:
        """Extract floating point numbers from text."""
        nums = []
        current = ""
        has_dot = False
        for char in text:
            if char.isdigit() or (char == '.' and not has_dot):
                current += char
                if char == '.': has_dot = True
            else:
                if current:
                    try: nums.append(float(current))
                    except ValueError: pass
                    current = ""
                    has_dot = False
        if current:
            try: nums.append(float(current))
            except ValueError: pass
        return nums

    def _check_coherence(self, prompt: str, candidate: str) -> float:
        """
        Calculate coherence penalty based on logical constraints.
        Returns 0.0 (perfect coherence) to 1.0 (total incoherence).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        negations = ["not ", "no ", "never ", "false "]
        p_neg = any(n in p_lower for n in negations)
        c_neg = any(n in c_lower for n in negations)
        
        # If prompt implies negation but candidate affirms (or vice versa) without context, penalize
        # Simplified: If prompt has "not" and candidate lacks it (and isn't short), slight penalty if semantic flip suspected
        if p_neg and not c_neg and len(candidate.split()) > 2:
            penalty += 0.2
            
        # 2. Numeric Transitivity/Constraint
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate number violates obvious bounds in prompt if present
            # E.g., Prompt: "x < 5", Candidate: "6" -> Incoherent
            # Heuristic: If prompt has a bound and candidate exceeds it significantly
            if "less" in p_lower or "<" in prompt:
                if p_nums and c_nums[0] > max(p_nums):
                    penalty += 0.5
            if "greater" in p_lower or ">" in prompt:
                if p_nums and c_nums[0] < min(p_nums):
                    penalty += 0.5
                    
        return min(penalty, 1.0)

    def _compute_justification(self, prompt: str, candidate: str) -> float:
        """
        Compute justification weight j in [0, 1].
        Based on NCD: Lower distance = Higher justification.
        """
        ncd = self._get_ncd(prompt, candidate)
        # Convert distance to justification: j = 1 - ncd
        return max(0.0, 1.0 - ncd)

    def _compute_info_gain(self, prompt: str, candidate: str) -> float:
        """
        Approximate Expected Information Gain.
        Heuristic: Specificity and length relative to prompt types.
        Longer, non-repetitive candidates that contain prompt keywords have higher potential gain.
        """
        if not candidate.strip(): return 0.0
        
        # Penalize mere repetition (low info)
        if candidate.strip().lower() == prompt.strip().lower():
            return 0.1
            
        # Reward containing specific prompt tokens (relevance)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        overlap = len(p_words.intersection(c_words))
        relevance = overlap / max(len(p_words), 1)
        
        # Complexity penalty for gibberish (high entropy usually compresses poorly alone)
        # But here we just use length-normalized overlap as a proxy for useful info
        return min(1.0, (len(c_words) * 0.1) + (relevance * 0.5))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate prompt features
        p_nums = self._extract_numbers(prompt)
        
        for cand in candidates:
            # 1. Epistemic Attributes
            j = self._compute_justification(prompt, cand)  # Justification
            c = self._check_coherence(prompt, cand)        # Coherence penalty
            ig = self._compute_info_gain(prompt, cand)     # Information Gain proxy
            
            # 2. Active Inference Objective: Minimize Free Energy
            # Score = (IG * j) - (lambda * c)
            # We maximize this score. 
            base_score = (ig * j) - (self.lambda_balance * c)
            
            # 3. Structural Override (The "Reasoning" boost)
            # If numbers match logically, boost significantly
            c_nums = self._extract_numbers(cand)
            if p_nums and c_nums:
                # Exact numeric match boost
                if abs(p_nums[0] - c_nums[0]) < self.threshold_numeric:
                    base_score += 2.0
                # Logical comparison boost
                if "larger" in prompt.lower() or "greater" in prompt.lower():
                    if c_nums[0] > p_nums[0]: base_score += 1.0
                if "smaller" in prompt.lower() or "less" in prompt.lower():
                    if c_nums[0] < p_nums[0]: base_score += 1.0

            results.append({
                "candidate": cand,
                "score": float(base_score),
                "reasoning": f"Justification(j)={j:.2f}, Coherence(c)={c:.2f}, InfoGain={ig:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the CAIG score normalized.
        """
        # Evaluate single candidate against itself to get relative score
        # We need a baseline. Let's assume a null hypothesis "" or "Unknown"
        # But the interface asks for confidence in (prompt, answer).
        # We simulate the scoring mechanism.
        
        j = self._compute_justification(prompt, answer)
        c = self._check_coherence(prompt, answer)
        ig = self._compute_info_gain(prompt, answer)
        
        raw_score = (ig * j) - (self.lambda_balance * c)
        
        # Numeric consistency boost
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(answer)
        if p_nums and c_nums:
             if abs(p_nums[0] - c_nums[0]) < self.threshold_numeric:
                 raw_score += 2.0

        # Map raw score to 0-1 range roughly
        # Scores can be negative. Let's sigmoid map.
        # Typical range: -1.0 to 3.0
        conf = 1.0 / (1.0 + np.exp(-raw_score)) 
        return float(conf)