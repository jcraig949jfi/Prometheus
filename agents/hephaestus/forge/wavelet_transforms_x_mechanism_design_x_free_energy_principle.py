import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-resolution logical-graph scoring engine.
    Combines Wavelet Transforms (multi-scale analysis), Mechanism Design (incentive-compatible scoring),
    and Free Energy Principle (prediction error minimization) to evaluate textual reasoning.
    
    Mechanism:
    1. Parsing: Extracts logical propositions and relations (negation, conditional, causal, numeric) into a graph.
    2. Wavelet: Applies Haar DWT to relation vectors to capture coarse-to-fine logical structures.
    3. Free Energy: Computes variational free energy as the weighted sum of squared errors between 
       prompt and candidate detail coefficients, plus a complexity penalty.
    4. Scoring: Score = -FreeEnergy. Higher score (lower energy) indicates better structural alignment.
    """

    def __init__(self):
        # Relation types to detect
        self.relation_types = ['negation', 'comparative', 'conditional', 'causal', 'numeric', 'ordering']
        # Regex patterns for extraction
        self.patterns = {
            'negation': [r'\b(not|no|never|none)\b'],
            'comparative': [r'\b(more than|less than|greater than|smaller than|>|<)\b'],
            'conditional': [r'\b(if|then|unless|otherwise)\b'],
            'causal': [r'\b(because|leads to|results in|causes|due to)\b'],
            'numeric': [r'\b\d+(\.\d+)?\b'],
            'ordering': [r'\b(first|second|before|after|next|last)\b']
        }

    def _extract_relations(self, text: str) -> Dict[str, List[int]]:
        """Extract binary presence vectors for each relation type."""
        text_lower = text.lower()
        relations = {}
        for r_type, regex_list in self.patterns.items():
            count = 0
            for pattern in regex_list:
                matches = re.findall(pattern, text_lower)
                count += len(matches)
            # Normalize slightly to avoid huge numbers dominating wavelets, but keep magnitude
            relations[r_type] = [count] 
        return relations

    def _build_signal_vector(self, text: str, max_len: int = 32) -> np.ndarray:
        """
        Build a fixed-length signal vector representing the logical structure.
        We expand the extracted counts into a binary-like sequence to allow wavelet decomposition.
        """
        relations = self._extract_relations(text)
        # Create a base vector from relation counts
        base_vec = []
        for r_type in self.relation_types:
            val = relations[r_type][0]
            # Expand based on magnitude to create a signal suitable for 1D wavelet
            # If a relation appears 3 times, we add [1, 1, 1, 0, 0...] to stretch the signal
            expanded = [1.0] * min(val, 4) + [0.0] * max(0, 4 - val) 
            base_vec.extend(expanded)
        
        # Pad or truncate to max_len (must be power of 2 for simple Haar)
        vec = np.array(base_vec, dtype=float)
        if len(vec) < max_len:
            vec = np.pad(vec, (0, max_len - len(vec)), mode='constant')
        elif len(vec) > max_len:
            vec = vec[:max_len]
            
        return vec

    def _haar_dwt(self, data: np.ndarray) -> List[np.ndarray]:
        """
        Compute 1D Haar Discrete Wavelet Transform.
        Returns list of detail coefficients at each scale.
        """
        details = []
        current = data.astype(float)
        
        # Ensure length is power of 2
        n = len(current)
        if n == 0:
            return [np.array([0.0])]
            
        # Simple iterative Haar
        while len(current) > 1:
            if len(current) % 2 != 0:
                current = np.append(current, 0) # Pad if odd
            
            approx = (current[0::2] + current[1::2]) / 2.0
            detail = (current[0::2] - current[1::2]) / 2.0
            
            details.append(detail)
            current = approx
            
        return details if details else [np.array([0.0])]

    def _compute_free_energy(self, prompt_vec: np.ndarray, candidate_vec: np.ndarray) -> float:
        """
        Compute Variational Free Energy approximation.
        F = Sum_s ( lambda_s * ||d_s - d_hat_s||^2 ) + Complexity Penalty
        """
        prompt_details = self._haar_dwt(prompt_vec)
        cand_details = self._haar_dwt(candidate_vec)
        
        # Ensure same number of scales
        min_scales = min(len(prompt_details), len(cand_details))
        
        free_energy = 0.0
        total_complexity = 0.0
        
        for s in range(min_scales):
            d_prompt = prompt_details[s]
            d_cand = cand_details[s]
            
            # Pad to match lengths if necessary
            max_len = max(len(d_prompt), len(d_cand))
            d_prompt = np.pad(d_prompt, (0, max_len - len(d_prompt)))
            d_cand = np.pad(d_cand, (0, max_len - len(d_cand)))
            
            # Precision lambda_s = 1 / scale (coarser scales have lower precision weight)
            # Scale index s=0 is finest detail, higher s is coarser. 
            # Actually in our loop, s=0 is finest (first iteration). 
            # Let's weight finer details higher as they contain specific logical tokens.
            lambda_s = 1.0 / (s + 1) 
            
            # Prediction error (squared Euclidean distance)
            error = np.sum((d_prompt - d_cand) ** 2)
            free_energy += lambda_s * error
            
            # Complexity penalty: log-det approximation via eigenvalues of stacked details
            # We approximate this by the variance of the detail coefficients
            stacked = np.vstack([d_prompt, d_cand])
            try:
                eigs = np.linalg.eigvalsh(np.cov(stacked))
                # Avoid log(0)
                eigs = eigs[eigs > 1e-9]
                if len(eigs) > 0:
                    total_complexity += 0.5 * np.sum(np.log(eigs + 1e-9))
            except:
                total_complexity += 0.1 # Small penalty for failure cases

        return free_energy + total_complexity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._build_signal_vector(prompt)
        results = []
        
        scores = []
        for cand in candidates:
            cand_vec = self._build_signal_vector(cand)
            fe = self._compute_free_energy(prompt_vec, cand_vec)
            # Score is negative free energy (higher is better)
            score = -fe
            scores.append(score)
        
        # Normalize scores to be more interpretable if needed, but raw -F works for ranking
        # Add a small bonus for exact string match (mechanism design incentive for truth)
        for i, cand in enumerate(candidates):
            if cand.strip().lower() == prompt.strip().lower():
                scores[i] += 10.0 

        # Rank by score descending
        sorted_indices = np.argsort(scores)[::-1]
        
        for idx in sorted_indices:
            cand = candidates[idx]
            score = scores[idx]
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural alignment score: {score:.4f}. Lower free energy indicates higher logical fidelity to prompt constraints."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Derived from the inverse of free energy, mapped via sigmoid-like function.
        """
        prompt_vec = self._build_signal_vector(prompt)
        answer_vec = self._build_signal_vector(answer)
        
        fe = self._compute_free_energy(prompt_vec, answer_vec)
        
        # Map free energy to confidence. 
        # Low FE (negative large magnitude) -> High Confidence.
        # High FE (positive large) -> Low Confidence.
        # Heuristic scaling: assume typical FE range is -5 to 20.
        # Use 1 / (1 + exp(FE - offset)) logic roughly.
        
        # If FE is very low (good match), confidence near 1.
        # If FE is high (bad match), confidence near 0.
        conf = 1.0 / (1.0 + np.exp(fe - 2.0))
        
        # Clamp
        return float(np.clip(conf, 0.0, 1.0))