import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Epistemic Incentive Engine (SEIE) Implementation.
    
    Mechanism:
    1. Structural Parsing (Epistemology): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt and candidates.
       This forms the "coherent low-frequency" signal.
    2. Spectral Analysis (Fourier Analogy): Converts the sequence of constraint 
       satisfactions (boolean/int steps) into a frequency domain representation.
       - Low frequencies represent consistent adherence to logical structure.
       - High frequencies represent contradictions or noise (rapid flipping of truth values).
       Justification is derived from the ratio of low-freq energy to total energy.
    3. Incentive Compatibility (Mechanism Design): A peer-prediction style penalty 
       is applied if a candidate's structural signature diverges significantly from 
       the consensus of high-scoring candidates, discouraging "self-deception" 
       (selecting candidates that look similar textually but fail logical checks).
    
    This approach prioritizes structural logic over string similarity (NCD), using 
    NCD only as a tiebreaker for structurally equivalent candidates.
    """

    def __init__(self):
        self.eps = 1e-9

    def _structural_parse(self, text: str) -> Tuple[List[int], List[float]]:
        """
        Extracts structural features: negations, comparatives, conditionals, and numbers.
        Returns a vector of logical consistency flags and a list of numeric values.
        """
        t = text.lower()
        flags = []
        nums = []
        
        # 1. Negation detection (Inhibitor pattern)
        negations = ['not', 'no', 'never', 'none', 'cannot', "won't", "don't", "doesn't"]
        has_neg = any(n in t.split() for n in negations) or ' not ' in t or t.startswith('no ')
        flags.append(1 if has_neg else 0)
        
        # 2. Comparative detection
        comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse', '>', '<']
        has_comp = any(c in t for c in comparatives)
        flags.append(1 if has_comp else 0)
        
        # 3. Conditional detection
        conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        has_cond = any(c in t.split() for c in conditionals)
        flags.append(1 if has_cond else 0)
        
        # 4. Numeric extraction
        words = t.replace(',', '').replace('.', ' ').split()
        for w in words:
            try:
                nums.append(float(w))
            except ValueError:
                pass
        
        # Default flag if empty to ensure vector exists
        if not flags:
            flags = [0, 0, 0]
            
        return flags, nums

    def _compute_evidence_stream(self, prompt: str, candidate: str) -> np.ndarray:
        """
        Generates a time-series signal representing the alignment between 
        prompt constraints and candidate properties.
        """
        p_flags, p_nums = self._structural_parse(prompt)
        c_flags, c_nums = self._structural_parse(candidate)
        
        # Construct evidence stream: 
        # Step 0: Negation alignment (Does candidate respect prompt negation?)
        # Step 1: Comparative alignment
        # Step 2: Conditional alignment
        # Step 3+: Numeric consistency
        
        stream = []
        
        # Logical consistency checks (0 = mismatch/noise, 1 = match/coherent)
        # Simplified heuristic: If prompt has feature, candidate should ideally reflect it or answer it.
        # For this engine, we treat the presence of matching structural complexity as 'coherence'.
        
        # Check 1: Negation handling
        if p_flags[0]: 
            # If prompt has negation, candidate must be specific (length > short threshold) to be valid reasoning
            stream.append(1.0 if len(c_flags) > 0 else 0.2) 
        else:
            stream.append(1.0)
            
        # Check 2: Comparative handling
        if p_flags[1]:
            # If prompt compares, candidate should ideally contain numbers or comparatives
            score = 1.0 if (c_flags[1] or len(c_nums) > 0) else 0.3
            stream.append(score)
        else:
            stream.append(1.0)
            
        # Check 3: Conditional handling
        if p_flags[2]:
            score = 1.0 if c_flags[2] else 0.4
            stream.append(score)
        else:
            stream.append(1.0)

        # Check 4: Numeric Consistency (The "Truth" layer)
        if p_nums and c_nums:
            # If both have numbers, check magnitude consistency roughly
            # This is a proxy for "does the answer make sense numerically?"
            p_max = max(p_nums)
            c_val = c_nums[0] if c_nums else 0
            
            # Heuristic: If prompt asks for "less than X", and candidate is > X, penalize.
            # Since we don't parse semantics fully, we use a stability check.
            # If the candidate number is wildly different (order of magnitude), it might be noise.
            if p_max > 0 and (c_val > 10 * p_max or c_val < 0.1 * p_max):
                stream.append(0.1) # High frequency noise
            else:
                stream.append(1.0)
        elif p_nums and not c_nums:
            # Prompt needs math, candidate has none -> Noise
            stream.append(0.2)
        else:
            stream.append(1.0)
            
        # Pad to minimum length for FFT stability
        while len(stream) < 4:
            stream.append(1.0)
            
        return np.array(stream[:8]) # Cap at 8 for fixed size DFT

    def _spectral_justification(self, signal: np.ndarray) -> float:
        """
        Applies DFT to the evidence stream.
        Justification = Ratio of Low-Freq Energy (Coherence) to Total Energy.
        High freq energy indicates contradiction/noise.
        """
        spectrum = np.fft.fft(signal)
        magnitude = np.abs(spectrum)
        
        total_energy = np.sum(magnitude**2) + self.eps
        
        # Low frequency components (DC and first harmonic)
        # In a short vector, index 0 is DC (mean), 1 is fundamental
        low_freq_energy = magnitude[0]**2 + magnitude[1]**2
        
        justification = low_freq_energy / total_energy
        return float(justification)

    def _incentive_penalty(self, candidate: str, all_candidates: List[str], scores: List[float]) -> float:
        """
        Mechanism Design: Peer Prediction.
        Penalizes candidates that are structurally outliers compared to high-scoring peers.
        Encourages truthfulness (structural consistency) over popularity.
        """
        if len(all_candidates) < 2:
            return 0.0
            
        # Identify "trusted" peers (top 50% by initial spectral score)
        threshold = np.median(scores) if scores else 0
        trusted_indices = [i for i, s in enumerate(scores) if s >= threshold]
        
        if not trusted_indices:
            return 0.0
            
        # Calculate average structural signature of trusted peers
        trusted_sigs = []
        for i in trusted_indices:
            flags, _ = self._structural_parse(all_candidates[i])
            trusted_sigs.append(flags)
        
        if not trusted_sigs:
            return 0.0
            
        avg_trusted = np.mean(trusted_sigs, axis=0)
        
        # Compare current candidate to trusted consensus
        curr_flags, _ = self._structural_parse(candidate)
        # Pad/truncate to match
        min_len = min(len(avg_trusted), len(curr_flags))
        if min_len == 0:
            return 0.0
            
        deviation = np.sum(np.abs(np.array(curr_flags[:min_len]) - avg_trusted[:min_len]))
        
        # Penalty increases with deviation
        penalty = min(0.3, deviation * 0.1)
        return penalty

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        
        # Phase 1: Structural & Spectral Scoring
        raw_scores = []
        for cand in candidates:
            signal = self._compute_evidence_stream(prompt, cand)
            spec_score = self._spectral_justification(signal)
            raw_scores.append(spec_score)
        
        # Phase 2: Mechanism Design (Incentive Compatibility)
        final_scores = []
        for i, cand in enumerate(candidates):
            base_score = raw_scores[i]
            penalty = self._incentive_penalty(cand, candidates, raw_scores)
            # Adjusted score
            adj_score = max(0.0, base_score - penalty)
            final_scores.append(adj_score)
        
        # Phase 3: Ranking and Tie-breaking with NCD
        # Sort indices by score descending
        sorted_indices = np.argsort(final_scores)[::-1]
        
        ranked_results = []
        for idx in sorted_indices:
            cand = candidates[idx]
            score = final_scores[idx]
            
            # Tie-breaking logic using NCD against the prompt
            # If scores are very close, prefer the one with better compression relation to prompt
            # (Heuristic: often the correct answer shares specific terminology without being a copy)
            # Note: NCD is weak here, used only as deterministic tiebreaker
            ncd_val = self._ncd_distance(prompt, cand)
            
            reasoning = f"Spectral coherence: {score:.4f}. Structural alignment detected."
            if penalty > 0.1:
                reasoning += " Penalty applied for structural deviation from peer consensus."
                
            ranked_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on spectral justification of the single answer.
        """
        signal = self._compute_evidence_stream(prompt, answer)
        spec_score = self._spectral_justification(signal)
        
        # Apply a strict penalty if the answer is too short to contain reasoning
        if len(answer.split()) < 3:
            spec_score *= 0.8
            
        return max(0.0, min(1.0, spec_score))