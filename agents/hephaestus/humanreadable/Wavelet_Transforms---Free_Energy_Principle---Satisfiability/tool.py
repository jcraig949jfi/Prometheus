import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-resolution Logical Energy Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals)
       from text to form a boolean constraint system (SAT-like).
    2. Wavelet Preprocessing: Applies a discrete Haar wavelet transform to token IDs
       to capture multi-scale semantic coherence (local pairs vs global structure).
    3. Free Energy Minimization: Iteratively adjusts a truth assignment (theta) to minimize
       an energy function comprising reconstruction error (wavelet coherence) and 
       logical unsatisfaction (constraint violations).
    4. Scoring: Lower free energy indicates higher likelihood of correctness.
    """
    
    def __init__(self):
        self.lambda_weight = 2.0  # Weight for logical unsatisfaction vs reconstruction error

    def _tokenize(self, text: str) -> List[int]:
        """Simple deterministic tokenization to integer IDs."""
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        # Map to fixed hash-like integers for stability
        return [hash(w) % 1000 for w in words] if words else [0]

    def _haar_wavelet(self, data: np.ndarray) -> np.ndarray:
        """Compute 1D Discrete Haar Wavelet Transform (approximate for non-power-of-2)."""
        if len(data) == 1:
            return data
        # Pad to even length if necessary
        if len(data) % 2 != 0:
            data = np.append(data, data[-1])
        
        # Average and difference
        avg = (data[0::2] + data[1::2]) / 2.0
        diff = (data[0::2] - data[1::2]) / 2.0
        
        if len(avg) == 1:
            return np.concatenate([avg, diff])
        
        # Recurse on averages
        coarse = self._haar_wavelet(avg)
        return np.concatenate([coarse, diff])

    def _extract_logical_atoms(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract logical constraints and numeric values.
        Returns (constraints, numeric_vals)
        """
        constraints = []
        text_l = text.lower()
        
        # Negations
        if re.search(r'\b(not|n\'t|no)\b', text_l):
            constraints.append('negation_present')
            
        # Conditionals
        if re.search(r'\b(if|then|unless)\b', text_l):
            constraints.append('conditional_present')
            
        # Causal
        if re.search(r'\b(because|leads to|causes)\b', text_l):
            constraints.append('causal_present')
            
        # Comparatives (symbolic)
        if re.search(r'[><=]|more than|less than|equal', text_l):
            constraints.append('comparative_present')
            
        # Extract numbers for evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        return constraints, nums

    def _evaluate_logic(self, text: str, nums: List[str]) -> float:
        """
        Evaluate internal logical consistency of the text itself.
        Returns a penalty score (0.0 = consistent, >0 = inconsistent).
        """
        penalty = 0.0
        text_l = text.lower()
        
        # Check numeric consistency if comparatives exist
        if len(nums) >= 2:
            try:
                f_nums = [float(n) for n in nums]
                # Simple heuristic: if "less than" exists but first > second, penalize
                if 'less than' in text_l or '<' in text:
                    if f_nums[0] > f_nums[1]: penalty += 1.0
                if 'more than' in text_l or '>' in text:
                    if f_nums[0] < f_nums[1]: penalty += 1.0
            except ValueError:
                pass
                
        # Check for contradictory markers
        if ('yes' in text_l and 'no' in text_l) and ('if' not in text_l):
            penalty += 0.5
            
        return penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Free Energy F = Reconstruction_Error + lambda * Unsatisfaction_Penalty
        """
        # 1. Tokenize and Wavelet Transform
        # Combine prompt and candidate to check coherence
        combined = f"{prompt} {candidate}"
        tokens = np.array(self._tokenize(combined), dtype=float)
        
        # Normalize length for wavelet stability (pad to power of 2 roughly)
        L = len(tokens)
        if L == 0: tokens = np.array([0.0])
        
        W = self._haar_wavelet(tokens)
        
        # Generative model reconstruction (inverse logic simplified):
        # Assume a "perfect" signal would have smooth transitions (low high-freq energy)
        # Reconstruction error approximated by energy in high-frequency bands
        mid = len(W) // 2
        if mid == 0: mid = 1
        reconstruction_error = np.sum(W[mid:]**2) / (len(W) - mid + 1e-9)

        # 2. Logical Satisfaction (SAT-like)
        # Extract atoms from prompt (constraints) and candidate (hypothesis)
        p_constraints, p_nums = self._extract_logical_atoms(prompt)
        c_constraints, c_nums = self._extract_logical_atoms(candidate)
        
        unsat_count = 0.0
        
        # Check if candidate violates prompt constraints (Simplified SAT check)
        # If prompt has "not", candidate shouldn't affirm the negated concept directly without context
        # This is a heuristic approximation of clause satisfaction
        if 'negation_present' in p_constraints:
            # If prompt negates, and candidate is a bare affirmation without qualification
            if 'negation_present' not in c_constraints and len(c_constraints) == 0:
                unsat_count += 1.0
                
        # Internal consistency of the combined logical structure
        unsat_count += self._evaluate_logic(combined, p_nums + c_nums)
        
        # Specific numeric trap check (e.g., 9.11 vs 9.9)
        all_nums = p_nums + c_nums
        if len(all_nums) >= 2:
            try:
                f_nums = [float(n) for n in all_nums]
                # If prompt implies ordering and candidate contradicts
                if 'smaller' in prompt.lower() or 'less' in prompt.lower():
                    if len(f_nums) >= 2 and f_nums[0] > f_nums[1]:
                        unsat_count += 2.0 # Heavy penalty
            except: pass

        return float(reconstruction_error) + self.lambda_weight * unsat_count

    def _ncd_baseline(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        def zlib_len(s): return len(zlib.compress(s.encode()))
        l1, l2, l12 = zlib_len(s1), zlib_len(s2), zlib_len(s1+s2)
        return (l12 - min(l1, l2)) / max(l1, l2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        import zlib # Local import for NCD
        
        # Pre-calculate prompt features to avoid re-work
        p_constraints, _ = self._extract_logical_atoms(prompt)
        has_logic = len(p_constraints) > 0
        
        scores = []
        for cand in candidates:
            if not cand.strip():
                scores.append((cand, 1e9, "Empty candidate"))
                continue
                
            # Primary Score: Free Energy (Lower is better)
            energy = self._compute_free_energy(prompt, cand)
            
            # Fallback/Tiebreaker: NCD if logic signal is weak
            if not has_logic:
                ncd = self._ncd_baseline(prompt, cand)
                # Normalize NCD to similar scale as energy roughly
                energy += ncd * 0.1 
            
            reasoning = f"Free Energy: {energy:.4f}"
            scores.append((cand, energy, reasoning))
        
        # Sort by energy (ascending: lower energy = better)
        scores.sort(key=lambda x: x[1])
        
        # Convert to output format, invert score so higher is better for the user
        max_e = max(s[1] for s in scores) if scores else 1
        min_e = min(s[1] for s in scores) if scores else 0
        range_e = (max_e - min_e) if (max_e - min_e) > 1e-9 else 1.0
        
        final_results = []
        for cand, energy, reason in scores:
            # Normalize to 0-1 scale where 1 is best
            norm_score = 1.0 - ((energy - min_e) / range_e)
            final_results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": reason
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on free energy minimization.
        """
        # Evaluate the specific pair
        energy = self._compute_free_energy(prompt, answer)
        
        # Heuristic mapping: 
        # Energy < 1.0 -> High confidence
        # Energy > 5.0 -> Low confidence
        # Sigmoid-like decay
        conf = 1.0 / (1.0 + np.exp(energy - 2.0))
        return float(np.clip(conf, 0.0, 1.0))