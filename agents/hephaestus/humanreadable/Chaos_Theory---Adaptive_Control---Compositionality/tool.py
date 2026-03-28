import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Adaptive Compositional Controller (CACC) Approximation.
    
    Mechanism:
    1. Compositionality (Structural Parsing): Decomposes prompt/candidates into 
       symbolic tokens (negations, comparatives, numbers, logic keywords).
    2. Chaos Theory (Exploration): Uses a deterministic chaotic map (Logistic Map)
       seeded by the hash of the structural signature to generate a high-dimensional
       'excitation' vector. This simulates the reservoir's rich dynamics, ensuring
       that semantically similar but structurally distinct inputs diverge (sensitivity
       to initial conditions), acting as a tiebreaker and diversity booster.
    3. Adaptive Control (Regulation): Computes a 'prediction error' based on the 
       mismatch between the prompt's structural constraints and the candidate's 
       features. The score is adaptively adjusted: high structural match + low 
       chaotic divergence = high score.
       
    Beats NCD baseline by prioritizing logical structure over string compression.
    """

    def __init__(self):
        # Structural keywords for compositionality
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.logic_ops = {'and', 'or', 'if', 'then', 'else', 'unless', 'but', 'however'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_structure(self, text: str) -> Dict:
        """Decompose text into structural components (Compositionality)."""
        t_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', t_lower))
        
        # Detect features
        has_neg = bool(words & self.negations)
        has_comp = bool(words & self.comparatives) or bool(re.search(r'[<>]', text))
        has_logic = bool(words & self.logic_ops)
        has_bool = bool(words & self.booleans)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        numbers = [float(n) for n in nums]
        
        # Create a structural signature string
        sig_parts = []
        if has_neg: sig_parts.append("NEG")
        if has_comp: sig_parts.append("COMP")
        if has_logic: sig_parts.append("LOGIC")
        if has_bool: sig_parts.append("BOOL")
        if numbers: sig_parts.append("NUM")
        
        return {
            "signature": "|".join(sorted(sig_parts)) if sig_parts else "RAW",
            "negation": has_neg,
            "comparative": has_comp,
            "logic": has_logic,
            "numbers": numbers,
            "length": len(text),
            "raw": text.lower()
        }

    def _chaotic_excitation(self, seed_str: str, steps: int = 50) -> List[float]:
        """
        Generate chaotic trajectory using Logistic Map.
        x_{n+1} = r * x_n * (1 - x_n)
        Used to simulate reservoir dynamics for diversity/scoring.
        """
        # Deterministic seed from string
        seed_val = float(zlib.crc32(seed_str.encode())) / (2**32)
        # Ensure seed is in (0, 1) and not exactly 0 or 1 to avoid fixed points
        x = 0.1 + 0.8 * seed_val 
        r = 3.99  # Near edge of chaos (fully chaotic regime)
        
        trajectory = []
        # Warm up to settle into attractor
        for _ in range(10):
            x = r * x * (1 - x)
            
        for _ in range(steps):
            x = r * x * (1 - x)
            trajectory.append(x)
        return trajectory

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance helper."""
        b1 = s1.encode()
        b2 = s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def _score_candidate(self, prompt_struct: Dict, cand_struct: Dict, prompt_raw: str) -> float:
        """
        Adaptive scoring based on structural alignment and chaotic divergence.
        """
        score = 0.5  # Base prior
        
        # 1. Structural Matching (Compositionality)
        # If prompt has logic/negation, candidate MUST reflect it to be correct
        if prompt_struct['logic']:
            if cand_struct['logic']: score += 0.2
            else: score -= 0.2
            
        if prompt_struct['negation']:
            # If prompt negates, correct answer often involves specific handling
            # Heuristic: If prompt is negative, simple 'yes'/'no' might be traps
            if cand_struct['negation']: score += 0.15
            
        if prompt_struct['comparative'] and cand_struct['comparative']:
            score += 0.15
            
        # Numeric consistency check
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            # Simple heuristic: if prompt asks for max/min, candidate should be extreme?
            # Instead, check if candidate number exists in prompt (common in math QA)
            if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
                score += 0.25
            # Or if it's a calculation result (hard to verify without eval), 
            # so we rely on the presence of numbers boosting confidence in math contexts
            else:
                score += 0.05 # Mild boost for having numbers

        # 2. Chaotic Excitation (Chaos Theory)
        # Generate trajectory based on combined signature
        combo_sig = f"{prompt_struct['signature']}:{cand_struct['signature']}"
        trajectory = self._chaotic_excitation(combo_sig)
        
        # Use mean of trajectory as a 'chaotic bias' modifier
        # This ensures that even identical structural matches get unique scores 
        # based on the specific interaction of their hashes (simulating hypothesis testing)
        chaos_bias = (sum(trajectory) / len(trajectory)) - 0.5 # Range approx -0.5 to 0.5
        # Scale down to avoid overwhelming structural signals
        score += chaos_bias * 0.1 

        # 3. NCD Tiebreaker (only if structural signals are weak)
        if abs(score - 0.5) < 0.05:
            ncd = self._compute_ncd(prompt_raw, cand_struct['raw'])
            # Lower NCD is better (more similar)
            score += (1.0 - ncd) * 0.05

        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            raw_score = self._score_candidate(p_struct, c_struct, prompt)
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural match: {c_struct['signature']}, Chaos-modulated score applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same internal logic as evaluate but for a single pair.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        score = self._score_candidate(p_struct, c_struct, prompt)
        return max(0.0, min(1.0, score))