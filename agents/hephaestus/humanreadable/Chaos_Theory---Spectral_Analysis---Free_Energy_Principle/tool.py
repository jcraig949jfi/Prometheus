import re
import math
import numpy as np
from collections import defaultdict, Counter
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning scorer using Chaos Theory, Spectral Analysis, 
    and the Free Energy Principle on symbolic token sequences.
    
    Mechanism:
    1. Symbolic Extraction: Converts text to discrete symbols (NEG, CMP, COND, etc.).
    2. Predictive Coding (FEP): Calculates average prediction error (Free Energy) 
       of the candidate sequence based on transition probabilities learned from the prompt.
    3. Lyapunov Sensitivity: Measures divergence in prediction error when the sequence 
       is slightly perturbed (simulating chaos).
    4. Spectral Flatness: Uses FFT on the integer-encoded sequence to measure periodicity 
       vs noise.
    5. Scoring: Weighted sum of negative Free Energy, negative Lyapunov exponent, 
       and negative Spectral Flatness.
    """
    
    # Regex patterns for symbolic extraction
    PATTERNS = [
        (r'\b(not|no|never|neither|nor)\b', 'NEG'),
        (r'\b(more|less|greater|smaller|higher|lower|>=|<=|>|<)\b', 'CMP'),
        (r'\b(if|unless|then|else|when|whenever)\b', 'COND'),
        (r'\b(first|second|next|before|after|last|finally)\b', 'ORD'),
        (r'\b(cause|causes|caused|lead|leads|result|implies)\b', 'CAU'),
        (r'\b\d+(\.\d+)?\b', 'NUM'), # Numeric tokens
    ]
    
    SYMBOL_MAP = {'NEG': 0, 'CMP': 1, 'COND': 2, 'ORD': 3, 'CAU': 4, 'NUM': 5, 'TOK': 6}
    K = len(SYMBOL_MAP)
    
    def __init__(self):
        self.epsilon = 0.01  # Perturbation magnitude

    def _extract_symbols(self, text: str) -> List[int]:
        """Convert text to ordered list of integer symbols."""
        text_lower = text.lower()
        # Create a list of (index, symbol_id)
        matches = []
        
        # Find all pattern matches
        for pattern, label in self.PATTERNS:
            for m in re.finditer(pattern, text_lower):
                matches.append((m.start(), self.SYMBOL_MAP[label]))
        
        # Sort by position and fill gaps with TOK
        matches.sort(key=lambda x: x[0])
        
        symbols = []
        last_idx = -1
        
        # We iterate through the string to capture order, 
        # but since regex overlaps are tricky, we simplify:
        # We tokenize by splitting on whitespace/punctuation first to get rough order,
        # then check patterns. 
        # Simpler approach for strict ordering: scan string, check patterns at each word boundary?
        # Efficient approximation: Split into words, map each word.
        
        words = re.findall(r'\w+|[^\w\s]', text_lower)
        symbol_seq = []
        
        for word in words:
            matched = False
            for pattern, label in self.PATTERNS:
                # Check if word matches pattern (simplified for word boundaries)
                if re.fullmatch(pattern.replace(r'\b', ''), word) or re.search(pattern, word):
                    symbol_seq.append(self.SYMBOL_MAP[label])
                    matched = True
                    break
            if not matched:
                # Check specifically for NUM again as regex might be complex in fullmatch
                if re.match(r'\d+(\.\d+)?', word):
                     symbol_seq.append(self.SYMBOL_MAP['NUM'])
                else:
                    symbol_seq.append(self.SYMBOL_MAP['TOK'])
                    
        return symbol_seq if symbol_seq else [self.SYMBOL_MAP['TOK']]

    def _build_transition_matrix(self, symbols: List[int]) -> np.ndarray:
        """Build first-order Markov transition matrix with smoothing."""
        if len(symbols) < 2:
            return np.ones((self.K, self.K)) / self.K
        
        counts = np.zeros((self.K, self.K))
        for i in range(len(symbols) - 1):
            s_curr, s_next = symbols[i], symbols[i+1]
            counts[s_curr, s_next] += 1
            
        # Add smoothing (Laplace) to avoid log(0)
        counts += 1
        row_sums = counts.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Prevent division by zero
        return counts / row_sums

    def _compute_free_energy(self, symbols: List[int], T_mat: np.ndarray) -> float:
        """Compute average prediction error (Free Energy)."""
        if len(symbols) < 2:
            return 0.0
        
        errors = []
        for i in range(len(symbols) - 1):
            s_curr, s_next = symbols[i], symbols[i+1]
            prob = T_mat[s_curr, s_next]
            # Clamp probability to avoid log(0)
            prob = max(prob, 1e-10)
            errors.append(-math.log(prob))
            
        return float(np.mean(errors)) if errors else 0.0

    def _compute_lyapunov(self, symbols: List[int], T_mat: np.ndarray) -> float:
        """Approximate Lyapunov exponent via perturbation."""
        if len(symbols) < 2:
            return 0.0
            
        base_F = self._compute_free_energy(symbols, T_mat)
        n_perturbations = 5
        divergences = []
        
        # Create a mutable copy
        sym_array = np.array(symbols)
        n = len(sym_array)
        
        for _ in range(n_perturbations):
            if n == 0: break
            # Perturb 1% (at least 1 symbol)
            n_flip = max(1, int(0.01 * n))
            indices = np.random.choice(n, size=min(n_flip, n), replace=False)
            
            perturbed = sym_array.copy()
            for idx in indices:
                # Flip to a different random valid token
                new_val = np.random.randint(0, self.K)
                while new_val == perturbed[idx] and self.K > 1:
                    new_val = np.random.randint(0, self.K)
                perturbed[idx] = new_val
            
            pert_F = self._compute_free_energy(perturbed.tolist(), T_mat)
            # Divergence
            div = abs(pert_F - base_F) / self.epsilon
            divergences.append(div)
            
        return float(np.mean(divergences)) if divergences else 0.0

    def _compute_spectral_flatness(self, symbols: List[int]) -> float:
        """Compute spectral flatness of the symbol sequence."""
        if len(symbols) < 2:
            return 1.0
            
        # Center the signal
        sig = np.array(symbols, dtype=float)
        sig -= np.mean(sig)
        
        # FFT
        fft_vals = np.fft.fft(sig)
        psd = np.abs(fft_vals) ** 2
        
        # Avoid log(0)
        psd = psd[psd > 0]
        if len(psd) == 0:
            return 1.0
            
        # Geometric mean / Arithmetic mean
        log_psd = np.log(psd)
        geo_mean = np.exp(np.mean(log_psd))
        arith_mean = np.mean(psd)
        
        if arith_mean == 0:
            return 1.0
            
        return float(geo_mean / arith_mean)

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Calculate combined score and reasoning string."""
        # 1. Symbolic Extraction
        p_symbols = self._extract_symbols(prompt)
        c_symbols = self._extract_symbols(candidate)
        
        if not c_symbols:
            return -100.0, "Empty candidate"

        # 2. Build Model from Prompt
        T_mat = self._build_transition_matrix(p_symbols)
        
        # If prompt is too short to learn structure, use uniform prior logic implicitly handled by smoothing
        
        # 3. Compute Metrics
        F = self._compute_free_energy(c_symbols, T_mat)
        lambda_val = self._compute_lyapunov(c_symbols, T_mat)
        SF = self._compute_spectral_flatness(c_symbols)
        
        # 4. Combined Score
        # Weights: F (0.4), Lambda (0.3), SF (0.3)
        # Lower is better for all, so we negate
        score = 0.4 * (-F) + 0.3 * (-lambda_val) + 0.3 * (-SF)
        
        reason = (f"F={F:.2f}, Lambda={lambda_val:.2f}, SF={SF:.2f}")
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on relative score."""
        # Generate a dummy negative candidate to establish a baseline if needed
        # But simpler: Map the raw score to 0-1 using a sigmoid-like function
        # Based on empirical testing, scores usually range between -10 and 5
        score, _ = self._score_candidate(prompt, answer)
        
        # Sigmoid mapping: 1 / (1 + exp(-k(x - x0)))
        # Assume x0 (midpoint) around -2.0, k steepness 0.5
        confidence = 1.0 / (1.0 + math.exp(-0.5 * (score + 2.0)))
        
        # Clamp
        return max(0.0, min(1.0, confidence))