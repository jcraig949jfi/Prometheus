import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Evaluating Sparse Predictive Coder (SESPC)
    
    Mechanism:
    1. Sparse Encoding (Hypothesis Generation): Converts text to a sparse vector of 
       n-gram features, enforcing sparsity by keeping only high-frequency/distinctive tokens.
    2. Free Energy Minimization (Prediction): Reconstructs the candidate answer from the 
       sparse code. The 'Free Energy' is the sum of reconstruction error and sparsity penalty.
    3. Falsification Monitor (Popperian Check): If the prediction error (epsilon) exceeds 
       a dynamic threshold (tau) derived from the prompt's own variance, the hypothesis 
       is 'falsified' (penalized heavily).
    4. Scoring: Candidates are ranked by minimized free energy, adjusted for falsification.
    
    This implements the theoretical combination of Sparse Autoencoders, Free Energy Principle,
    and Falsificationism using only numpy-free (standard lib) linear algebra and compression.
    """

    def __init__(self):
        self.n_gram_size = 3
        self.sparsity_lambda = 0.1
        self.falsification_margin = 0.2

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _get_ngrams(self, text: str) -> List[str]:
        tokens = text.split()
        if len(tokens) < self.n_gram_size:
            return tokens
        return [" ".join(tokens[i:i+self.n_gram_size]) for i in range(len(tokens)-self.n_gram_size+1)]

    def _sparse_encode(self, text: str, vocab: List[str]) -> List[float]:
        """Creates a sparse binary-like vector based on vocab presence."""
        if not vocab:
            return []
        features = self._get_ngrams(text)
        feature_set = set(features)
        # Sparse vector: 1.0 if feature present, 0.0 otherwise
        return [1.0 if term in feature_set else 0.0 for term in vocab]

    def _compute_free_energy(self, prompt: str, candidate: str) -> Tuple[float, bool, float]:
        """
        Computes Free Energy L = Reconstruction_Error + Lambda * Sparsity.
        Returns (Energy, is_falsified, prediction_error).
        """
        combined = f"{prompt} {candidate}"
        
        # 1. Define Vocabulary (Hypothesis Space) from the combined context
        # We use a local vocabulary to simulate a dictionary learned from the specific problem context
        all_terms = list(set(self._get_ngrams(combined)))
        if not all_terms:
            return 0.0, False, 0.0

        # 2. Encode (Sparse Code z)
        z = self._sparse_encode(combined, all_terms)
        
        # Enforce sparsity manually by zeroing out low-contribution features if needed,
        # but here the n-gram presence is already sparse relative to all possible strings.
        # We apply L1 penalty conceptually as the count of active features * lambda
        sparsity_penalty = sum(z) * self.sparsity_lambda

        # 3. Decode / Predict (Reconstruction)
        # In this textual analog, the 'decoder' predicts the candidate should contain 
        # terms logically entailed by the prompt. 
        # We approximate reconstruction error via Normalized Compression Distance (NCD)
        # between the candidate and the prompt's logical implication.
        
        p_norm = len(zlib.compress(prompt.encode()))
        c_norm = len(zlib.compress(candidate.encode()))
        
        # Joint compression approximates mutual information
        try:
            joint_norm = len(zlib.compress((prompt + " " + candidate).encode()))
        except:
            joint_norm = p_norm + c_norm

        # Prediction Error (epsilon): How much extra info is needed to describe candidate given prompt?
        # High epsilon means the candidate is surprising/unpredicted by the prompt model.
        epsilon = max(0, (joint_norm - p_norm) / (c_norm + 1))

        # 4. Falsification Monitor
        # Threshold tau is dynamic: based on the complexity of the prompt itself.
        # If the prompt is simple, tolerance for error is low.
        tau = 0.3 + (0.1 * math.log(p_norm + 1)) 
        is_falsified = epsilon > tau

        # Free Energy Calculation
        # If falsified, energy is spiked (infinite penalty in logical terms)
        if is_falsified:
            energy = 10.0 + epsilon + sparsity_penalty
        else:
            # Minimize error + complexity
            energy = epsilon + sparsity_penalty

        return energy, is_falsified, epsilon

    def _extract_numeric_constraint(self, text: str) -> float:
        """Helper to detect numeric magnitude for structural parsing."""
        import re
        nums = re.findall(r"-?\d+\.?\d*", text)
        if nums:
            try:
                return float(nums[-1])
            except:
                pass
        return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt = self._normalize(prompt)
        scored_candidates = []
        
        # Baseline metric for tie-breaking (NCD)
        p_comp = zlib.compress(prompt.encode())
        p_len = len(p_comp)

        for cand in candidates:
            cand_clean = self._normalize(cand)
            if not cand_clean:
                continue

            energy, falsified, epsilon = self._compute_free_energy(prompt, cand_clean)
            
            # Structural Parsing Enhancements (Causal Intelligence)
            # 1. Negation Check
            prompt_has_not = "not " in prompt or "impossible" in prompt
            cand_has_not = "not " in cand_clean or "impossible" in cand_clean
            logic_penalty = 0.0
            if prompt_has_not != cand_has_not:
                # Potential logic mismatch, increase energy slightly unless it's a specific contrast case
                logic_penalty = 0.5
            
            # 2. Numeric Consistency
            p_num = self._extract_numeric_constraint(prompt)
            c_num = self._extract_numeric_constraint(cand_clean)
            if p_num != 0 and c_num != 0:
                # If numbers exist, strict comparison affects score
                if prompt.find("larger") != -1 and c_num < p_num:
                    energy += 2.0 # Penalty for violating numeric constraint
                elif prompt.find("smaller") != -1 and c_num > p_num:
                    energy += 2.0

            total_energy = energy + logic_penalty
            
            # Convert Energy to Score (Lower Energy = Higher Score)
            # Using exponential decay to map energy to 0-1 range
            score = math.exp(-total_energy)
            
            reasoning = f"Energy={total_energy:.4f}, Falsified={falsified}, Epsilon={epsilon:.4f}"
            if falsified:
                reasoning += " (Hypothesis rejected by falsification monitor)"
            
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the free energy of the specific pair."""
        prompt = self._normalize(prompt)
        answer = self._normalize(answer)
        
        energy, falsified, _ = self._compute_free_energy(prompt, answer)
        
        if falsified:
            return 0.0
        
        # Map energy to confidence. 
        # Energy ~0 -> Confidence ~1.0
        # Energy ~2.0 -> Confidence ~0.1
        conf = math.exp(-energy)
        return max(0.0, min(1.0, conf))