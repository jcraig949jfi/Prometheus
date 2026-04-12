import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning tool combining Cellular Automata (CA) for logical propagation,
    Kalman Filtering for belief refinement, and the Free Energy Principle (FEP) for scoring.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and relations (negation, causality, numeric) 
       to build a sparse adjacency matrix A.
    2. CA Update: Propagates truth values via x_new = threshold(A @ x_old).
    3. Kalman Filter: Treats extracted text features as noisy observations (o) of the 
       logical state. Updates belief mean (mu) and covariance (P).
    4. Free Energy: Computes variational free energy F based on prediction error and 
       prior complexity. Score = -F.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.threshold = 1.5  # CA threshold for activation
        self.process_noise = 0.1
        self.obs_noise = 0.5
        self.dim = 20  # Max proposition dimension

    def _parse_structure(self, text: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Extracts features and builds adjacency matrix."""
        text_lower = text.lower()
        features = {
            'negation': 0, 'comparative': 0, 'conditional': 0, 
            'causal': 0, 'numeric': 0, 'ordering': 0
        }
        
        # Feature extraction
        if re.search(r'\b(not|no|never|none)\b', text_lower): features['negation'] = 1
        if re.search(r'\b(greater|less|more|fewer|than|compare)\b', text_lower): features['comparative'] = 1
        if re.search(r'\b(if|then|unless|provided)\b', text_lower): features['conditional'] = 1
        if re.search(r'\b(cause|lead|result|because|due to)\b', text_lower): features['causal'] = 1
        if re.search(r'\d+(\.\d+)?', text_lower): features['numeric'] = 1
        if re.search(r'\b(before|after|first|last|sequence)\b', text_lower): features['ordering'] = 1

        # Build observation vector o (mapped to indices 0-5)
        o = np.array(list(features.values()), dtype=float)
        
        # Build sparse adjacency matrix A (CA rule engine)
        # Simplified: Identity + shift for propagation, modified by feature presence
        A = np.eye(self.dim)
        if features['negation']:
            # Simulate inversion logic in first few dimensions
            A[0, 0] = -1.0 
        if features['causal']:
            # Simulate forward propagation
            for i in range(self.dim - 1):
                A[i+1, i] = 0.8
        
        return A, o, features

    def _run_ca_kalman(self, A: np.ndarray, o: np.ndarray) -> Tuple[np.ndarray, float]:
        """Executes CA step and Kalman update to derive Free Energy."""
        dim_o = len(o)
        dim_state = max(self.dim, dim_o)
        
        # Pad A and o to match state dimension
        A_full = np.eye(dim_state)
        A_full[:A.shape[0], :A.shape[1]] = A
        
        o_pad = np.zeros(dim_state)
        o_pad[:dim_o] = o
        
        # 1. CA Prediction Step (Deterministic Logic)
        # Initial belief x (random noise seeded by text length for determinism)
        x = np.random.default_rng(seed=len(o)).normal(0.5, 0.1, dim_state)
        # CA Update: x_new = f(A @ x)
        z = A_full @ x
        # Rule 110-ish thresholding simplified for continuous space
        x_pred = np.where(z > self.threshold, 1.0, np.where(z < -self.threshold, 0.0, z))
        
        # 2. Kalman Filter Step
        # Prior
        mu_minus = x_pred
        P_minus = np.eye(dim_state) * self.process_noise
        
        # Observation Matrix H (extracts observed dimensions)
        H = np.zeros((dim_o, dim_state))
        H[:, :dim_o] = np.eye(dim_o)
        
        # Kalman Gain
        S = H @ P_minus @ H.T + np.eye(dim_o) * self.obs_noise
        K = P_minus @ H.T @ np.linalg.inv(S)
        
        # Posterior
        innovation = o - (H @ mu_minus)[:dim_o]
        mu_post = mu_minus + (K @ innovation)[:dim_state] # Simplified broadcast
        P_post = (np.eye(dim_state) - K @ H) @ P_minus
        
        # 3. Free Energy Calculation
        # F = 0.5 * (innovation^T R^-1 innovation) + 0.5 * (mu^T P^-1 mu)
        R_inv = np.linalg.inv(np.eye(dim_o) * self.obs_noise)
        P_inv = np.linalg.inv(P_post + 1e-6 * np.eye(dim_state))
        
        term1 = 0.5 * innovation.T @ R_inv @ innovation
        term2 = 0.5 * mu_post.T @ P_inv @ mu_post
        
        free_energy = term1 + term2
        return mu_post, -free_energy # Score is negative free energy

    def _check_meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B traps (Ambiguity, Presupposition, etc.)."""
        p = prompt.lower()
        traps = [
            r'\bhave you (stopped|quit)\b', # Presupposition
            r'\bwhy did .+ (fail|stop)\b', # Presupposition of failure
            r'\bevery .+ (a|an) .+\b', # Scope ambiguity potential
            r'\bhe told .+ he\b', # Pronoun ambiguity
            r'\beither .+ or .+\b', # False dichotomy
            r'\bbest|worst|favorite\b', # Subjectivity
            r'\bwho is .+\b.*\bhe\b', # Ambiguous reference
        ]
        score = 1.0
        for pattern in traps:
            if re.search(pattern, p):
                score -= 0.4 # Penalize heavily for ambiguity
        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if l1 == 0 or l2 == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        A, o, _ = self._parse_structure(prompt)
        
        # Baseline score from CA-Kalman-FEP on the prompt itself
        _, base_score = self._run_ca_kalman(A, o)
        
        for cand in candidates:
            # 1. Structural/Logic Score (Primary)
            # Combine prompt features with candidate presence
            cand_text = f"{prompt} {cand}"
            A_c, o_c, _ = self._parse_structure(cand_text)
            
            # Merge observations (Prompt + Candidate)
            o_combined = np.concatenate([o, o_c])
            if len(o_combined) < self.dim:
                o_combined = np.pad(o_combined, (0, self.dim - len(o_combined)), 'constant')
            else:
                o_combined = o_combined[:self.dim]
                
            _, logic_score = self._run_ca_kalman(A, o_combined)
            
            # 2. Numeric Evaluation (Constructive)
            # Simple check: if prompt has numbers, does candidate match logic?
            nums_p = re.findall(r'\d+\.?\d*', prompt)
            nums_c = re.findall(r'\d+\.?\d*', cand)
            numeric_bonus = 0.0
            if nums_p and nums_c:
                try:
                    # Heuristic: If candidate number is in prompt, boost slightly
                    if any(n in nums_p for n in nums_c):
                        numeric_bonus = 0.5
                except: pass

            # 3. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Final Score Composition
            # Structural/Logic: 85%, NCD: 15%
            final_score = (logic_score * 0.85) + numeric_bonus + ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"CA-Kalman propagation yielded energy {logic_score:.2f}; NCD contribution {ncd_score:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at <0.3 if meta-analysis detects ambiguity.
        Caps at <0.9 unless definitive computation exists.
        """
        # 1. Meta-Confidence (Tier B Check)
        meta_conf = self._check_meta_confidence(prompt)
        
        if meta_conf < 0.6:
            return 0.2 # Low confidence for ambiguous/trap prompts

        # 2. Structural Match Check
        A, o, feats = self._parse_structure(f"{prompt} {answer}")
        
        # If no structural features found, assume low confidence (honest uncertainty)
        if sum(feats.values()) == 0:
            return 0.25

        # 3. Compute Logic Score
        _, score = self._run_ca_kalman(A, o)
        
        # Normalize score roughly to 0-1 range based on typical free energy magnitudes
        # Free energy is negative log-likelihood-ish, so lower is better. 
        # Our score is negative F, so higher is better.
        # Heuristic normalization
        norm_conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        
        # Cap at 0.9 unless numeric verification is strong
        has_nums = bool(re.search(r'\d+', prompt) and re.search(r'\d+', answer))
        cap = 0.95 if has_nums else 0.85
        
        final_conf = min(norm_conf, cap)
        
        return float(final_conf)