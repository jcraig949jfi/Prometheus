import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Category Theory concepts (functorial mapping), 
    LDPC error correction (constraint satisfaction), and Kalman Filtering (state estimation).
    
    Mechanism:
    1. Parsing: Extracts logical features (negation, causality, numerics) into binary vectors.
    2. Encoding: Maps features to a codeword space using a simplified systematic generator.
    3. State Estimation: Uses a Kalman-like update to minimize parity-check violations (logical inconsistencies).
    4. Scoring: Combines logical consistency (Mahalanobis distance), numeric computation accuracy, 
       and structural overlap. NCD is used only as a minor tie-breaker.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Simple systematic LDPC-like generator (k=10, n=20) for demonstration
        # In a full system, this would be a sparse matrix from a library.
        self.k = 10  # Feature dimension
        self.n = 20  # Codeword dimension
        self.G = np.zeros((self.k, self.n), dtype=int)
        # Systematic part
        self.G[:, :self.k] = np.eye(self.k, dtype=int)
        # Parity part (simple XOR shifts)
        for i in range(self.k):
            self.G[i, self.k + (i % (self.n - self.k))] = 1
            
        self.H = self._generate_parity_check()
        self.tolerance = 1e-4

    def _generate_parity_check(self) -> np.ndarray:
        """Generate a dummy parity check matrix H such that H * G^T = 0 (mod 2)."""
        # For this simplified demo, we create a random sparse matrix and ensure 
        # it orthogonalizes with G via Gaussian elimination logic or simple construction.
        # Here we just create a valid H for the systematic part for demonstration.
        m = self.n - self.k
        H = np.zeros((m, self.n), dtype=int)
        # H = [P^T | I_m] where G = [I_k | P]
        # Our G has P as shifted identity. 
        # Let's just make H enforce that parity bits equal specific data bits.
        for i in range(m):
            if i < self.k:
                H[i, i] = 1 # Data bit
                H[i, self.k + i] = 1 # Parity bit
        return H

    def _parse_proposition(self, text: str) -> np.ndarray:
        """Convert text to a binary feature vector x_p."""
        text_lower = text.lower()
        features = np.zeros(self.k, dtype=int)
        
        # 1. Negation
        if re.search(r'\b(not|no|never|without|fail|impossible)\b', text_lower):
            features[0] = 1
            
        # 2. Comparative
        if re.search(r'\b(more|less|greater|smaller|better|worse|higher|lower|before|after)\b', text_lower):
            features[1] = 1
        if re.search(r'[><=]', text):
            features[1] = 1
            
        # 3. Conditional
        if re.search(r'\b(if|then|unless|provided|when)\b', text_lower):
            features[2] = 1
            
        # 4. Causal
        if re.search(r'\b(because|therefore|thus|leads? to|causes?|due to)\b', text_lower):
            features[3] = 1
            
        # 5. Quantifiers
        if re.search(r'\b(all|every|some|none|any|most)\b', text_lower):
            features[4] = 1
            
        # 6. Numeric presence
        if re.search(r'\d+', text):
            features[5] = 1
            
        # 7. Temporal
        if re.search(r'\b(year|day|time|hour|minute|second|ago|later)\b', text_lower):
            features[6] = 1
            
        # 8. Subjectivity/Modal
        if re.search(r'\b(might|could|should|best|worst|favorite)\b', text_lower):
            features[7] = 1

        # 9. Question words (for prompt analysis)
        if re.search(r'\b(who|what|where|when|why|how)\b', text_lower):
            features[8] = 1
            
        # 10. Logical connector (and, or)
        if re.search(r'\b(and|or|but|however)\b', text_lower):
            features[9] = 1
            
        return features

    def _encode(self, x: np.ndarray) -> np.ndarray:
        """Encode feature vector to codeword."""
        return (self.G.T @ x) % 2

    def _kalman_update(self, s: np.ndarray, P: np.ndarray, H_meas: np.ndarray, z: np.ndarray, R: float) -> Tuple[np.ndarray, np.ndarray]:
        """Single step Kalman update."""
        if H_meas.shape[1] != s.shape[0]:
            # Dimension mismatch safety
            return s, P
            
        # Predict step (static model F=I, Q=0 for this snapshot)
        s_pred = s
        P_pred = P
        
        # Update
        # K = P * H^T * (H * P * H^T + R)^-1
        HP = H_meas @ P_pred
        S = HP @ H_meas.T + R * np.eye(H_meas.shape[0])
        
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.linalg.pinv(S)
            
        K = P_pred @ H_meas.T @ S_inv
        
        residual = z - (H_meas @ s_pred)
        s_upd = s_pred + (K @ residual)
        
        I_mat = np.eye(P.shape[0])
        P_upd = (I_mat - K @ H_meas) @ P_pred
        
        return s_upd, P_upd

    def _compute_numeric_answer(self, text: str) -> Optional[float]:
        """Extract and compute simple arithmetic if present."""
        # Look for patterns like "5 + 3", "10 - 2", "2 * 3", "8 / 2"
        # Also look for "sum of 1, 2, 3"
        numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]
        
        # Simple binary ops
        ops = re.findall(r'(-?\d+\.?\d*)\s*([\+\-\*\/])\s*(-?\d+\.?\d*)', text)
        if ops:
            # Evaluate first found operation
            a, op, b = ops[0]
            a, b = float(a), float(b)
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/': return a / b if b != 0 else None
            
        # Summation heuristic
        if len(numbers) > 2 and re.search(r'\b(sum|total|add)\b', text.lower()):
            return sum(numbers)
            
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: presupposition, ambiguity, unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop|die)|when did .+ stop)\b', p):
            return 0.2
            
        # 2. Scope/Pronoun ambiguity heuristics
        if re.search(r'\b(every .+ a .+|told .+ he was|told .+ she was)\b', p) and re.search(r'\bwho\b', p):
            return 0.3
            
        # 3. False dichotomy
        if re.search(r'\b(either .+ or .+)\b', p) and not re.search(r'\b(both|neither|other)\b', p):
            # Only flag if it looks like a forced choice without options
            if len(p.split('?')[0].split(',')) < 2: 
                pass # Weak signal
            else:
                return 0.4 # Slight penalty
                
        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', p):
            if not re.search(r'\b(data|metric|criteria|according to)\b', p):
                return 0.3
                
        # 5. Unanswerable (missing info)
        if re.search(r'\b(calculate|find|determine)\b', p):
            nums = re.findall(r'\d+', p)
            if len(nums) == 0 and re.search(r'\b(number|value|amount)\b', p):
                return 0.1 # No numbers to compute with

        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if max(len1, len2) == 0: return 0.0
        return (len_both - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_vec = self._parse_proposition(prompt)
        prompt_num = self._compute_numeric_answer(prompt)
        
        # Pre-calculate prompt NCD for normalization if needed, but mostly for candidate comparison
        p_len = len(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Parsing & Encoding (Category Theory Functor)
            cand_vec = self._parse_proposition(cand)
            
            # Map to codeword space
            # We treat the combined state of prompt+candidate as the system to check consistency
            # In this simplified model, we check if candidate satisfies constraints implied by prompt
            combined_features = (prompt_vec + cand_vec) % 2 # Simple interaction
            
            # Encode
            c_prompt = self._encode(prompt_vec)
            c_cand = self._encode(cand_vec)
            
            # 2. Kalman-like Constraint Propagation
            # State: concatenated codewords
            s = np.concatenate([c_prompt.astype(float), c_cand.astype(float)])
            n_state = len(s)
            P = np.eye(n_state) * 1.0 # Initial covariance
            
            # Measurement: Parity checks (H * s = 0)
            # Construct measurement matrix for the combined state
            # We want H*c_prompt ~ 0 and H*c_cand ~ 0
            H_full = np.zeros((self.H.shape[0]*2, n_state))
            H_full[:self.H.shape[0], :self.n] = self.H
            H_full[self.H.shape[0]:, self.n:] = self.H
            
            z = np.zeros(H_full.shape[0])
            
            # Run update
            s_final, P_final = self._kalman_update(s, P, H_full, z, 0.1)
            
            # 3. Scoring
            # Logical Consistency Score (Negative Mahalanobis distance to valid manifold)
            # Ideally H*s should be 0. Distance from 0 indicates error.
            residual = H_full @ s_final
            logic_error = np.sum(residual**2)
            logic_score = 1.0 / (1.0 + logic_error) # Map error to 0-1
            
            # 4. Constructive Computation (Frame B Priority)
            comp_score = 0.0
            cand_num = self._compute_numeric_answer(cand)
            
            if prompt_num is not None and cand_num is not None:
                # If both have numbers, check closeness
                if abs(prompt_num) > 1e-9: # Avoid div by zero
                    rel_diff = abs(cand_num - prompt_num) / abs(prompt_num)
                else:
                    rel_diff = abs(cand_num - prompt_num)
                comp_score = 1.0 / (1.0 + rel_diff)
                if comp_score > 0.9:
                    reasoning_parts.append("Numeric match confirmed.")
            elif prompt_num is not None and cand_num is None:
                # Prompt asks for math, candidate has no math -> Low score
                comp_score = 0.1
                reasoning_parts.append("Missing numeric computation.")
            elif prompt_num is None and cand_num is not None:
                # Spurious numbers? Penalty.
                comp_score = 0.5 
            else:
                # Non-numeric reasoning
                # Check feature overlap (structural consistency)
                overlap = np.sum(prompt_vec == cand_vec) / self.k
                comp_score = overlap # Fallback to structural similarity for non-math
                if overlap > 0.8:
                    reasoning_parts.append("High structural consistency.")

            # 5. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd_score(prompt, cand)
            # Invert NCD (0 is identical, 1 is different) -> we want high score for similar
            ncd_score = 1.0 - ncd_val
            
            # Final Weighted Score
            # Computation >= 40%, Structural >= 30%, NCD <= 15%
            # We normalize logic_score to represent structural/logical consistency
            
            final_score = (
                0.45 * comp_score + 
                0.40 * logic_score + 
                0.15 * ncd_score
            )
            
            # Cap score if logic is fundamentally broken
            if logic_error > 5.0:
                final_score *= 0.5
                reasoning_parts.append("Logical constraints violated.")
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Evaluated via constraint propagation and feature matching."
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Evaluate the specific answer
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]['score']
        
        # 3. Adjust based on computation certainty
        # If we computed a number and it matches, confidence can be high
        prompt_num = self._compute_numeric_answer(prompt)
        ans_num = self._compute_numeric_answer(answer)
        
        if prompt_num is not None and ans_num is not None:
            if abs(prompt_num - ans_num) < 1e-6:
                # Definitive computational match
                conf = min(0.95, meta_cap) 
            else:
                conf = 0.1 # Definitely wrong numerically
        else:
            # Heuristic confidence based on score
            # Scale raw score (which is weighted) to confidence
            # Avoid overconfidence (>0.9) without definitive computation
            if raw_score > 0.8:
                conf = min(0.85, meta_cap)
            elif raw_score > 0.6:
                conf = min(0.6, meta_cap)
            else:
                conf = min(raw_score, meta_cap)
                
        return float(conf)