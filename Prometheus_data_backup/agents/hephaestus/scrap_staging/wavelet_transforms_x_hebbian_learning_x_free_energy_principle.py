import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Scattering Predictive Coding (WSPC) Tool.
    
    Mechanism:
    1. Wavelet Transform (Structural Parsing): Instead of signal frequencies,
       we decompose the text into "semantic frequencies": Negations (high-pass filters),
       Comparatives (band-pass), and Conditionals (modulation). This creates a 
       multi-resolution representation of the logical constraints.
       
    2. Free Energy Principle (Evaluation): The system maintains a "generative model"
       of the prompt's constraints. It calculates Variational Free Energy (VFE) for
       each candidate. VFE = Prediction Error - (Complexity * Precision).
       Candidates that satisfy structural constraints (low prediction error) and
       align with high-precision signals (negations/comparatives) minimize free energy.
       
    3. Hebbian Learning (Confidence/Scoring): Used strictly as a local binding mechanism.
       If a candidate's structural signature co-activates with the prompt's signature
       under low error conditions, the "synaptic weight" (score) is strengthened.
       This avoids global gradient descent, adhering to the constraint that Hebbian
       learning is a secondary support mechanism here.
       
    Primary Scoring: Structural constraint satisfaction (Free Energy minimization).
    Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        # Structural patterns acting as wavelet bases
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|larger|fewer|better|worse|higher|lower|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|unless|provided|when|then|else|otherwise)\b', re.IGNORECASE)
        self.numeric_pattern = re.compile(r'\d+\.?\d*')

    def _extract_wavelet_coeffs(self, text: str) -> Dict[str, float]:
        """
        Decomposes text into structural coefficients (Wavelet Transform analogy).
        Returns a vector of logical features.
        """
        text_lower = text.lower()
        neg_count = len(self.negation_pattern.findall(text_lower))
        comp_count = len(self.comparative_pattern.findall(text_lower))
        cond_count = len(self.conditional_pattern.findall(text_lower))
        nums = self.numeric_pattern.findall(text_lower)
        
        # Numeric complexity proxy
        num_val = 0.0
        if nums:
            try:
                num_val = sum(float(n) for n in nums)
            except ValueError:
                pass
                
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numeric_sum': num_val,
            'length': len(text.split())
        }

    def _calculate_precision(self, prompt_coeffs: Dict[str, float]) -> float:
        """
        Estimates precision (inverse variance) based on structural density.
        High structural density -> High precision required -> Higher penalty for errors.
        """
        density = (prompt_coeffs['negations'] * 2.0 + 
                   prompt_coeffs['comparatives'] * 1.5 + 
                   prompt_coeffs['conditionals'] * 1.2)
        # Base precision + scaled density
        return 1.0 + (density * 0.5)

    def _compute_prediction_error(self, prompt_coeffs: Dict[str, float], 
                                  cand_coeffs: Dict[str, float]) -> float:
        """
        Computes mismatch between prompt constraints and candidate implications.
        In predictive coding, this is the bottom-up error signal.
        """
        error = 0.0
        
        # Negation consistency: If prompt has negations, candidate should reflect logic
        # Simple heuristic: Check if candidate length/structure wildly deviates
        # A more robust check: Does the candidate contain contradictory markers?
        # For this implementation, we measure structural divergence.
        
        # Penalty for missing structural elements present in prompt
        if prompt_coeffs['negations'] > 0 and cand_coeffs['negations'] == 0:
            # Not a hard fail, but increases error if the candidate ignores the negation context
            # unless the candidate is very short (e.g., "No")
            if cand_coeffs['length'] > 3: 
                error += 2.0 * prompt_coeffs['negations']
                
        if prompt_coeffs['comparatives'] > 0 and cand_coeffs['comparatives'] == 0:
             if cand_coeffs['length'] > 5:
                error += 1.5 * prompt_coeffs['comparatives']

        # Numeric consistency check (simplified)
        if prompt_coeffs['numeric_sum'] > 0 and cand_coeffs['numeric_sum'] > 0:
            # If both have numbers, they should be somewhat related or the candidate 
            # shouldn't be wildly larger/smaller without context. 
            # Here we just penalize massive divergence in magnitude as "surprise"
            ratio = max(cand_coeffs['numeric_sum'], 1) / max(prompt_coeffs['numeric_sum'], 1)
            if ratio > 10 or ratio < 0.1:
                error += 1.0
                
        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp12 = len(zlib.compress(b1 + b2))
        
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Standard definition varies slightly, using: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Or simpler: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) is common.
        # Let's use: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        
        min_c = min(comp1, comp2)
        max_c = max(comp1, comp2)
        if max_c == 0: return 1.0
        
        return (comp12 - min_c) / max_c

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_coeffs = self._extract_wavelet_coeffs(prompt)
        precision = self._compute_precision(prompt_coeffs)
        
        scored_candidates = []
        
        # Pre-calculate prompt compression for NCD
        prompt_comp = len(zlib.compress(prompt.encode('utf-8')))
        
        for cand in candidates:
            cand_coeffs = self._extract_wavelet_coeffs(cand)
            
            # --- FREE ENERGY MINIMIZATION CORE ---
            # F = E - (P * S) roughly, but here we treat it as:
            # Score = - (Prediction_Error * Precision) + Bonus_Structural_Alignment
            
            pred_error = self._compute_prediction_error(prompt_coeffs, cand_coeffs)
            
            # Hebbian-style local update: 
            # Strengthen score if structural features co-activate (both have negations, etc)
            hebbian_bonus = 0.0
            if prompt_coeffs['negations'] > 0 and cand_coeffs['negations'] > 0:
                hebbian_bonus += 0.5
            if prompt_coeffs['comparatives'] > 0 and cand_coeffs['comparatives'] > 0:
                hebbian_bonus += 0.3
            if prompt_coeffs['conditionals'] > 0 and cand_coeffs['conditionals'] > 0:
                hebbian_bonus += 0.2
                
            # Free Energy Score (Lower is better, so we negate for ranking)
            # We want to minimize error weighted by precision
            free_energy = pred_error * precision
            
            # Base score starts high, subtracts free energy, adds hebbian bonus
            # Scaling factor to ensure NCD tiebreaker works in correct range
            base_score = 10.0 - free_energy + hebbian_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"FreeEnergy={free_energy:.2f}, Precision={precision:.2f}, HebbianBonus={hebbian_bonus:.2f}",
                "_ncd_cache": None # Placeholder for tiebreaker
            })
        
        # Sort by base score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply NCD as tiebreaker for top candidates within a small threshold
        # This ensures we beat the baseline on structural tasks but use NCD for nuance
        top_score = scored_candidates[0]["score"] if scored_candidates else 0
        threshold = 1.5 # Sensitivity range
        
        # Group by score proximity
        final_ranking = []
        if scored_candidates:
            # Simple bubble for NCD refinement on top contenders
            # Only re-rank if scores are very close
            for i in range(len(scored_candidates)):
                curr = scored_candidates[i]
                if abs(curr["score"] - top_score) <= threshold:
                    # Calculate NCD distance to prompt (lower is often better for "continuation" logic, 
                    # but for QA, we want semantic similarity. 
                    # However, standard NCD on (Prompt+Answer) vs Prompt is tricky.
                    # Let's use NCD between Prompt and Candidate as a similarity proxy.
                    if curr["_ncd_cache"] is None:
                        curr["_ncd_cache"] = self._ncd(prompt, curr["candidate"])
                
                # Adjust score slightly by NCD (lower NCD = higher similarity = slight boost)
                # But only if structural score is ambiguous
                ncd_penalty = 0.0
                if curr["_ncd_cache"] is not None:
                    # Normalize NCD impact to be smaller than structural signals
                    ncd_penalty = curr["_ncd_cache"] * 0.1 
                
                # Re-calculate final sort key
                curr["final_sort"] = curr["score"] - ncd_penalty
            else:
                curr["final_sort"] = curr["score"] # Fallback

            # Sort by final adjusted score
            scored_candidates.sort(key=lambda x: x.get("final_sort", x["score"]), reverse=True)
            
            # Clean up and format output
            for item in scored_candidates:
                item.pop("_ncd_cache", None)
                item.pop("final_sort", None)
                # Normalize score to 0-10 range roughly for readability, though raw is fine
                # Ensure deterministic output
                final_ranking.append({
                    "candidate": item["candidate"],
                    "score": round(item["score"], 4),
                    "reasoning": item["reasoning"]
                })

        return final_ranking

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Uses Hebbian co-activation as a secondary booster.
        """
        prompt_coeffs = self._extract_wavelet_coeffs(prompt)
        cand_coeffs = self._extract_wavelet_coeffs(answer)
        
        # Calculate Free Energy (Error)
        error = self._compute_prediction_error(prompt_coeffs, cand_coeffs)
        precision = self._compute_precision(prompt_coeffs)
        
        # Base confidence: Exponential decay of free energy
        # F = error * precision. 
        # Confidence = exp(-F)
        free_energy = error * precision
        base_conf = math.exp(-free_energy)
        
        # Hebbian Boost: If structural features match, strengthen confidence
        hebbian_factor = 0.0
        if prompt_coeffs['negations'] > 0 and cand_coeffs['negations'] > 0:
            hebbian_factor += 0.15
        if prompt_coeffs['comparatives'] > 0 and cand_coeffs['comparatives'] > 0:
            hebbian_factor += 0.1
        if prompt_coeffs['conditionals'] > 0 and cand_coeffs['conditionals'] > 0:
            hebbian_factor += 0.1
            
        # NCD check for exact match or high similarity
        ncd_val = self._ncd(prompt, answer)
        # If NCD is very low (high similarity), boost confidence
        if ncd_val < 0.3:
            hebbian_factor += 0.2
            
        conf = min(1.0, base_conf + hebbian_factor)
        return round(conf, 4)