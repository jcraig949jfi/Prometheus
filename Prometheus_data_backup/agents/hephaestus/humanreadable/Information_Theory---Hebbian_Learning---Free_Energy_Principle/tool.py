import re
import numpy as np
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Predictive-Error-Weighted Mutual Information (PEWMI) Engine.
    
    Mechanism:
    1. Parsing: Extracts symbolic tokens (predicates, negations, numerics, logic).
    2. Hebbian Learning: Builds a co-occurrence matrix (W) from prompt-answer pairs.
    3. Free Energy: Computes prediction error (KL divergence) between expected and observed symbols.
    4. Information Theory: Weights scores by mutual information minus prediction error.
    5. Epistemic Honesty: Detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        self.vocab = {}
        self.inv_vocab = {}
        self.W = None  # Hebbian matrix
        self.eta = 0.1
        self.lambda_factor = 0.5
        self._vocab_index = 0
        
        # Regex patterns for symbolic extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|lesser|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.I),
            'causal': re.compile(r'\b(because|due to|leads to|causes|therefore)\b', re.I),
            'numeric': re.compile(r'-?\d+(\.\d+)?'),
            'ordering': re.compile(r'\b(first|last|next|previous|second|third)\b', re.I),
            'predicate': re.compile(r'\b([a-z]+)\s+([a-z]+)\b', re.I) # Simple verb-noun approx
        }
        
        # Presupposition/Ambiguity triggers for Tier B
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\?', re.I),
            re.compile(r'\bwhy\s+did\s+\w+\s+(stop|fail|lose)\b', re.I),
            re.compile(r'\bhave\s+you\s+(stopped|quit)\b', re.I)
        ]
        self.ambiguity_triggers = [
            re.compile(r'\bevery\s+\w+.*\ba\s+\w+\b', re.I), # Scope ambiguity hint
            re.compile(r'\b(either|or)\b.*\b(without|no)\b.*\bother\b', re.I), # False dichotomy hint
            re.compile(r'\b(best|worst|favorite)\b.*\bwithout\b', re.I) # Subjectivity
        ]
        self.pronoun_triggers = re.compile(r'\b(he|she|him|her|they)\b.*\bwho\b', re.I)

    def _tokenize(self, text: str) -> Dict[str, int]:
        """Extract symbolic features and map to sparse vector indices."""
        tokens = set()
        text_lower = text.lower()
        
        # Extract specific logical tokens
        for key, pattern in self.patterns.items():
            if key == 'predicate':
                continue # Skip complex regex for now to save lines, focus on logic words
            matches = pattern.findall(text_lower)
            for m in matches:
                if isinstance(m, tuple): m = m[0]
                tokens.add(f"{key}:{m}")
        
        # Extract predicates (simplified)
        words = re.findall(r'\b[a-z]+\b', text_lower)
        for i in range(len(words)-1):
            tokens.add(f"pred:{words[i]}_{words[i+1]}")
            
        # Add n-grams for context
        for i in range(len(words)-2):
            tokens.add(f"ngram:{words[i]}_{words[i+1]}_{words[i+2]}")

        # Map to vocabulary
        vec = {}
        for t in tokens:
            if t not in self.vocab:
                self.vocab[t] = self._vocab_index
                self.inv_vocab[self._vocab_index] = t
                self._vocab_index += 1
            vec[self.vocab[t]] = 1
        return vec

    def _get_vector(self, text: str) -> np.ndarray:
        """Convert text to sparse binary vector based on current vocab."""
        tokens = self._tokenize(text)
        if self._vocab_index == 0:
            return np.zeros(0)
        vec = np.zeros(self._vocab_index)
        for idx in tokens:
            if idx < len(vec):
                vec[idx] = 1
        return vec

    def _hebbian_update(self, vec: np.ndarray):
        """Update Hebbian matrix W = W + eta * (x outer x)."""
        if vec.size == 0:
            return
        if self.W is None:
            n = len(vec)
            self.W = np.zeros((n, n))
        
        # Ensure dimensions match if vocab grew
        if self.W.shape[0] < len(vec):
            diff = len(vec) - self.W.shape[0]
            self.W = np.pad(self.W, ((0, diff), (0, diff)), mode='constant')
            
        outer = np.outer(vec, vec)
        self.W += self.eta * outer

    def _compute_free_energy(self, vec: np.ndarray) -> float:
        """Compute F = -log(p_hat) where p_hat = softmax(W * vec)."""
        if vec.size == 0 or self.W is None:
            return 10.0 # High energy (uncertainty) if no learning yet
            
        # Truncate W if vocab grew but no update yet
        curr_w = self.W[:len(vec), :len(vec)]
        
        # Prediction
        raw_pred = curr_w @ vec
        raw_pred -= np.max(raw_pred) # Stability
        exp_pred = np.exp(raw_pred)
        sum_exp = np.sum(exp_pred)
        if sum_exp == 0: sum_exp = 1e-9
        p_hat = exp_pred / sum_exp
        
        # KL Divergence approximation (Free Energy)
        # We treat the observed vector as the 'true' distribution (one-hot-ish)
        # F = - sum(x_i * log(p_hat_i)) for observed items
        observed_indices = np.where(vec > 0)[0]
        if len(observed_indices) == 0:
            return 0.0
            
        energy = 0.0
        for idx in observed_indices:
            if idx < len(p_hat):
                prob = p_hat[idx] + 1e-9
                energy -= np.log(prob)
        return energy

    def _compute_mutual_info(self, p_vec: np.ndarray, a_vec: np.ndarray) -> float:
        """Approximate MI using Hebbian weights as joint probability proxy."""
        if self.W is None or p_vec.size == 0:
            return 0.0
            
        # Normalize W to get joint prob approx
        total = np.sum(self.W)
        if total == 0: return 0.0
        
        # Simplified MI: Sum over co-occurring symbols in prompt/answer
        # I(P;A) approx sum_{i in P, j in A} W_ij * log(W_ij / (W_i * W_j))
        mi = 0.0
        p_indices = np.where(p_vec > 0)[0]
        a_indices = np.where(a_vec > 0)[0]
        
        if len(p_indices) == 0 or len(a_indices) == 0:
            return 0.0

        # Marginal approximations
        row_sums = np.sum(self.W, axis=1) + 1e-9
        col_sums = np.sum(self.W, axis=0) + 1e-9
        global_sum = np.sum(self.W) + 1e-9
        
        for i in p_indices:
            for j in a_indices:
                if i < self.W.shape[0] and j < self.W.shape[1]:
                    w_ij = self.W[i, j]
                    if w_ij > 0:
                        p_ij = w_ij / global_sum
                        p_i = row_sums[i] / global_sum
                        p_j = col_sums[j] / global_sum
                        if p_i > 0 and p_j > 0:
                            mi += p_ij * np.log(p_ij / (p_i * p_j))
        return mi

    def _check_constraints(self, text: str) -> float:
        """Simple constraint violation check (penalty)."""
        penalty = 0.0
        text_lower = text.lower()
        
        # Check for contradictory comparatives if present
        if ("greater" in text_lower and "less" in text_lower) or ("more" in text_lower and "fewer" in text_lower):
            # Heuristic: if both appear, might be complex, but if "not" appears nearby, could be violation
            if "not" in text_lower:
                penalty += 0.5
                
        return penalty

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in self.presupposition_triggers:
            if pat.search(prompt):
                return 0.2 # Low confidence on presupposition traps
        
        # 2. Ambiguity / Subjectivity
        for pat in self.ambiguity_triggers:
            if pat.search(prompt):
                return 0.3
        
        # 3. Pronoun Ambiguity
        if self.pronoun_triggers.search(prompt):
            return 0.3
            
        # 4. Unanswerable / Missing Info indicators
        if "information not provided" in p_lower or "cannot be determined" in p_lower:
            return 0.4
            
        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0-1, lower is similar)."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt
        p_vec = self._get_vector(prompt)
        
        # 2. Offline Exposure Simulation (Hebbian Update)
        # In a real system, this happens over a corpus. Here we do a lightweight 
        # exposure on the prompt + candidate combinations to simulate context learning.
        # We update W based on the union of prompt and each candidate to establish co-occurrence.
        for cand in candidates:
            combined = f"{prompt} {cand}"
            c_vec = self._get_vector(combined)
            self._hebbian_update(c_vec)
            
        results = []
        
        for cand in candidates:
            a_vec = self._get_vector(cand)
            
            # 3. Free Energy (Prediction Error)
            F = self._compute_free_energy(a_vec)
            
            # 4. Mutual Information
            MI = self._compute_mutual_info(p_vec, a_vec)
            
            # 5. Constraint Penalty
            C = self._check_constraints(cand)
            
            # Score: S = MI - lambda*F - C
            score = MI - (self.lambda_factor * F) - C
            
            # NCD Tiebreaker (max 15% influence logic handled by scaling if needed, 
            # but here we use it as a small bonus for string similarity if scores are close)
            ncd = self._ncd_score(prompt, cand)
            # Normalize NCD to be a small bonus (inverse distance)
            ncd_bonus = (1.0 - ncd) * 0.1 
            score += ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"MI={MI:.2f}, Error={F:.2f}, Penalty={C:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on epistemic honesty checks (Tier B).
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.5:
            return meta_cap
            
        # 2. Structural Match Check
        p_vec = self._get_vector(prompt)
        a_vec = self._get_vector(answer)
        
        if np.sum(p_vec) == 0 or np.sum(a_vec) == 0:
            return 0.1 # No structural parse found
            
        # 3. Compute internal metrics
        F = self._compute_free_energy(a_vec)
        MI = self._compute_mutual_info(p_vec, a_vec)
        
        # Base confidence on low error and high MI
        # Normalize F (assume max ~10 for scaling)
        base_conf = (1.0 - (F / 10.0)) * 0.6 + (min(MI, 1.0)) * 0.4
        base_conf = max(0.0, min(1.0, base_conf))
        
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 unless computation was definitive (hard to prove definitively without ground truth)
        # But if meta_cap is 1.0 and score is high, we allow up to 0.95
        if final_conf > 0.95:
            final_conf = 0.95
            
        return float(final_conf)