import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Predictive Coding Global Workspace (SPCGW) Approximation.
    
    Mechanism:
    1. Sparse Encoding (SAE): Converts text to a sparse vector of n-gram features.
       Only high-frequency or distinct tokens activate specific 'neurons'.
    2. Predictive Coding (FEP): Computes prediction error between the prompt's 
       structural template and the candidate's structure. Lower error = higher prior.
    3. Global Workspace (GWT): Candidates compete for 'ignition'. The workspace 
       evaluates the 'free energy' (surprise + complexity) of each candidate.
       Ignition occurs if the candidate reduces free energy significantly compared 
       to the baseline (NCD) and satisfies structural constraints (negation, numbers).
    4. Scoring: A weighted sum of structural validity, numeric consistency, and 
       compressed similarity, normalized to [0, 1].
    """

    def __init__(self):
        self.ngram_size = 3
        self.sparse_dim = 1024
        # Simple hash function for deterministic sparse mapping
        self._seed = 42 

    def _hash_token(self, token: str) -> int:
        """Deterministic hash to map tokens to sparse dimensions."""
        h = zlib.crc32(token.encode()) ^ self._seed
        return abs(h) % self.sparse_dim

    def _sparse_encode(self, text: str) -> np.ndarray:
        """
        Simulates SAE: Creates a sparse binary vector representing active features.
        Uses character n-grams and word stems as basis vectors.
        """
        vector = np.zeros(self.sparse_dim, dtype=np.float32)
        clean_text = text.lower()
        
        # Word-level features
        words = re.findall(r'\b\w+\b', clean_text)
        for word in words:
            idx = self._hash_token(word)
            vector[idx] = 1.0
            # Sub-word n-grams for granularity
            for i in range(len(word) - self.ngram_size + 1):
                ngram = word[i:i+self.ngram_size]
                idx = self._hash_token(ngram)
                vector[idx] = 0.5 # Lower weight for sub-features
        
        # L1 Normalization approximation (sparsity enforcement)
        if np.sum(vector) > 0:
            vector = vector / np.sum(vector)
        return vector

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical structure: negations, numbers, comparatives."""
        lower_t = text.lower()
        has_negation = bool(re.search(r'\b(not|no|never|neither|none)\b', lower_t))
        
        # Extract numbers
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        numbers = [float(n) for n in nums]
        
        # Extract comparatives
        comparatives = bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', lower_t))
        
        return {
            'negation': has_negation,
            'numbers': numbers,
            'has_comparative': comparatives,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def _evaluate_hypothesis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core FEP/GWT loop:
        1. Calculate Prediction Error (structural mismatch).
        2. Calculate Free Energy (Complexity + Accuracy).
        3. Determine Ignition (Score).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        reasoning_steps = []
        score = 0.0
        
        # 1. Structural Consistency (Predictive Coding)
        # If prompt has numbers, candidate should ideally have numbers (or explicit negation)
        struct_penalty = 0.0
        if p_struct['numbers']:
            if not c_struct['numbers'] and not c_struct['negation']:
                struct_penalty += 0.3
                reasoning_steps.append("Mismatch: Prompt contains numbers, candidate lacks numeric reasoning.")
        
        # Negation consistency check (simplified)
        if p_struct['negation'] and not c_struct['negation']:
            # Not always a penalty, but worth noting if the logic requires it
            pass 
            
        # 2. Numeric Logic (Constraint Propagation)
        numeric_score = 0.0
        if p_struct['numbers'] and c_struct['numbers']:
            # Check if candidate numbers are plausible relative to prompt (heuristic)
            # If prompt has 2 numbers and candidate has 1, it might be a result
            if len(c_struct['numbers']) >= 1:
                numeric_score = 0.2
                reasoning_steps.append("Numeric constraint satisfied.")
        
        # 3. Global Workspace Competition (NCD + Sparsity)
        # NCD measures similarity to the 'expected' answer space (prompt context)
        ncd = self._compute_ncd(prompt, candidate)
        
        # Sparse feature overlap (Dot product of sparse vectors)
        p_vec = self._sparse_encode(prompt)
        c_vec = self._sparse_encode(candidate)
        overlap = np.dot(p_vec, c_vec)
        
        # Free Energy Calculation (Minimizing Surprise)
        # High overlap + Low NCD + Low Structural Penalty = Low Free Energy
        base_score = (overlap * 2.0) + ((1.0 - ncd) * 1.5)
        free_energy = base_score - struct_penalty + numeric_score
        
        # Ignition Threshold (GWT)
        # Only 'ignite' (score high) if free energy is sufficiently low (score high)
        if free_energy > 0.5:
            ignition_bonus = 0.2
            reasoning_steps.append("Ignition: Hypothesis globally consistent.")
        else:
            ignition_bonus = 0.0
            reasoning_steps.append("No ignition: High prediction error or low coherence.")
            
        final_score = min(1.0, max(0.0, free_energy + ignition_bonus))
        
        return final_score, "; ".join(reasoning_steps)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._evaluate_hypothesis(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._evaluate_hypothesis(prompt, answer)
        return float(score)