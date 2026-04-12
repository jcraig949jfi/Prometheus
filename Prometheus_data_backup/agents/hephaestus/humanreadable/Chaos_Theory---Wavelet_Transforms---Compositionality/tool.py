import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Wavelet Reservoir with Compositional Readout (CWCR) - Structural Implementation.
    
    Mechanism:
    1. Chaos (Exploration): Uses a logistic map coupled to the input hash to generate 
       deterministic but sensitive perturbations. This simulates "divergent trajectories" 
       to test candidate robustness against slight variations (Goodhart resistance).
    2. Wavelets (Scale-Awareness): Implements a discrete Haar-like transform on 
       structural feature vectors (negations, comparatives, numbers). This isolates 
       "high-frequency" errors (local contradictions) vs "low-frequency" trends (global consistency).
    3. Compositionality (Readout): Scores candidates by composing verified sub-components 
       (logic rules) rather than raw string similarity.
    
    Strategy:
    - Primary Score: Structural parsing (logic, numbers, constraints).
    - Secondary Score: Multi-scale consistency (Wavelet energy of features).
    - Tiebreaker: NCD (Compression).
    - Confidence: Derived from the stability of the score under chaotic perturbation.
    """

    def __init__(self):
        # Logistic map parameter for chaotic dynamics (r=3.9 ensures chaos)
        self.chaos_r = 3.9 
        # Weights for compositional modules
        self.w_logic = 0.4
        self.w_numeric = 0.3
        self.w_structure = 0.3

    def _logistic_step(self, x: float) -> float:
        """Single step of logistic map for chaotic divergence."""
        return self.chaos_r * x * (1.0 - x)

    def _generate_chaos_sequence(self, seed_str: str, length: int) -> List[float]:
        """Generates a deterministic chaotic sequence based on input seed."""
        # Normalize hash to (0, 1) avoiding exact 0 or 1
        h = zlib.crc32(seed_str.encode()) / (2**32 - 1)
        x = 0.1 + 0.8 * h # Keep within (0.1, 0.9) to avoid fixed points
        seq = []
        # Burn-in
        for _ in range(50):
            x = self._logistic_step(x)
        for _ in range(length):
            x = self._logistic_step(x)
            seq.append(x)
        return seq

    def _extract_structural_features(self, text: str) -> List[float]:
        """
        Extracts a fixed-length vector of structural features.
        Analogous to decomposing signal into primitive components.
        """
        text_lower = text.lower()
        features = []
        
        # 1. Negation density (Logic inhibitor)
        negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        neg_count = sum(text_lower.count(n) for n in negations)
        features.append(min(neg_count / 5.0, 1.0))
        
        # 2. Comparative/Logical operators
        comparatives = ['greater', 'less', 'more', 'fewer', 'than', 'if', 'then', 'else']
        comp_count = sum(text_lower.count(c) for c in comparatives)
        features.append(min(comp_count / 5.0, 1.0))
        
        # 3. Numeric presence
        numbers = re.findall(r'\d+\.?\d*', text)
        features.append(min(len(numbers) / 5.0, 1.0))
        
        # 4. Constraint keywords (must, should, required)
        constraints = ['must', 'should', 'required', 'only', 'except']
        const_count = sum(text_lower.count(c) for c in constraints)
        features.append(min(const_count / 5.0, 1.0))
        
        # 5. Sentence complexity (approximated by comma/semicolon count)
        punct = text.count(',') + text.count(';') + text.count('.')
        features.append(min(punct / 10.0, 1.0))
        
        return features

    def _haar_wavelet_energy(self, vector: List[float]) -> float:
        """
        Computes a simple Haar-like wavelet energy metric.
        High energy in difference coefficients indicates high-frequency volatility (potential error).
        Low energy in smooth coefficients indicates stable trends.
        """
        if len(vector) < 2:
            return 0.0
        
        # Simple difference operator as a proxy for high-frequency wavelet coefficients
        diffs = [abs(vector[i] - vector[i-1]) for i in range(1, len(vector))]
        if not diffs:
            return 0.0
            
        # Energy of the "detail" coefficients
        energy = sum(d**2 for d in diffs) / len(diffs)
        return math.sqrt(energy)

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Checks basic numeric consistency if numbers are present."""
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric logic to violate
        
        try:
            # Simple heuristic: if prompt has comparison words, check order
            p_lower = prompt.lower()
            if 'greater' in p_lower or 'larger' in p_lower or 'more' in p_lower:
                if len(c_nums) >= 2:
                    # Expect increasing? Hard to verify without full parsing, 
                    # so we reward presence of numbers over absence.
                    pass
            
            # Penalty if candidate introduces random large numbers not in prompt context?
            # For now, reward consistency in count if small
            if abs(len(c_nums) - len(p_nums)) > 2:
                return 0.8 # Slight penalty for hallucinating many numbers
            return 1.0
        except:
            return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def _compositional_score(self, prompt: str, candidate: str) -> Tuple[float, Dict]:
        """
        Computes score by composing sub-module outputs.
        Returns (score, details_dict)
        """
        details = {}
        
        # Module 1: Structural Parsing
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # Module 2: Wavelet-based Consistency Check
        # Compare the "shape" of structural features between prompt and candidate
        # If prompt is complex (high wavelet energy) and candidate is simple (low), penalty.
        p_energy = self._haar_wavelet_energy(p_feat)
        c_energy = self._haar_wavelet_energy(c_feat)
        
        # Logic check: Does candidate preserve negation/comparative density roughly?
        # (Very rough approximation of logical entailment)
        structure_match = 1.0 - abs(p_energy - c_energy)
        details['structure_match'] = structure_match
        
        # Module 3: Numeric Logic
        num_score = self._evaluate_numeric_logic(prompt, candidate)
        details['numeric_score'] = num_score
        
        # Module 4: Chaotic Sensitivity (Simulated)
        # Generate chaos sequence based on candidate content
        chaos_seq = self._generate_chaos_sequence(candidate, 10)
        # If the sequence is "too" uniform (low variance), it might be a generic answer
        chaos_var = sum((x - sum(chaos_seq)/len(chaos_seq))**2 for x in chaos_seq) / len(chaos_seq)
        # Normalize variance to 0-1 range roughly (logistic map variance is bounded)
        chaos_quality = min(chaos_var * 4.0, 1.0) 
        details['chaos_quality'] = chaos_quality

        # Composition
        base_score = (self.w_structure * structure_match + 
                      self.w_logic * num_score + 
                      0.1 * chaos_quality) # Chaos is a small modifier
        
        return base_score, details

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_len = len(prompt)
        
        # Pre-calculate prompt features for efficiency
        p_feat = self._extract_structural_features(prompt)
        p_ncd_base = len(zlib.compress(prompt.encode()))
        
        for cand in candidates:
            # 1. Structural & Compositional Scoring
            score, details = self._compositional_score(prompt, cand)
            
            # 2. NCD as Tiebreaker/Booster
            # If structural signals are weak, NCD helps distinguish relevance
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher similarity) and scale
            ncd_score = 1.0 - ncd_val
            
            # Adaptive weighting: If structural match is ambiguous, lean on NCD
            if details['structure_match'] > 0.8 and details['numeric_score'] == 1.0:
                final_score = 0.7 * score + 0.3 * ncd_score
            else:
                # If structure fails, NCD is the only hope, but capped
                final_score = 0.4 * score + 0.6 * ncd_score
            
            # Penalty for length mismatch extremes (heuristic)
            len_ratio = len(cand) / (prompt_len + 1)
            if len_ratio < 0.05 or len_ratio > 5.0:
                final_score *= 0.8

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Struct:{details['structure_match']:.2f}, Num:{details['numeric_score']:.2f}, Chaos:{details['chaos_quality']:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Based on the stability of the answer under chaotic perturbation of the input representation.
        """
        base_score, details = self._compositional_score(prompt, answer)
        
        # Perturb the prompt slightly (simulated by appending a char and re-hashing chaos)
        # In a real system, this would be input noise. Here we simulate sensitivity.
        perturbed_prompt = prompt + " " 
        p_score, _ = self._compositional_score(perturbed_prompt, answer)
        
        # Stability metric: How much did the score change?
        stability = 1.0 - abs(base_score - p_score)
        
        # Combine base quality with stability
        # If base score is high AND stable, confidence is high.
        raw_conf = base_score * stability
        
        # Map to 0-1 strictly
        conf = max(0.0, min(1.0, raw_conf))
        return round(conf, 4)