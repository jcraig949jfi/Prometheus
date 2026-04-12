import re
import math
import random
from typing import List, Dict, Tuple, Any

# No external dependencies beyond standard library and numpy
try:
    import numpy as np
except ImportError:
    # Fallback if numpy is strictly unavailable, though prompt allows it
    raise ImportError("numpy is required for this reasoning tool")

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Falsificationism, and Property-Based Testing.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (negations, comparatives, conditionals, numbers) 
       from the prompt to form a linear measurement model H.
    2. Kalman Update: Treats each candidate answer as a hypothesized state vector. Updates 
       belief based on how well the candidate satisfies the extracted constraints (measurements).
    3. Falsification (Property-Based Testing): Generates perturbations of the extracted facts.
       If a candidate fails these perturbed tests (high innovation), it is penalized.
    4. Scoring: Combines final uncertainty (log-det covariance) and falsification count.
    """

    def __init__(self):
        self.rng = random.Random(42)  # Deterministic seed
        self.threshold_tau = 2.0
        self.lambda_penalty = 0.5

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|>\|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'causal': len(re.findall(r'\b(because|therefore|leads to|causes)\b', text_lower)),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text),
            'length': len(text)
        }
        return features

    def _build_measurement_model(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Construct H matrix and measurement vector z.
        Rows correspond to extracted propositions.
        """
        props = self._extract_features(prompt)
        cand_props = self._extract_features(candidate)
        
        # Feature vector construction (simplified state space)
        # State x = [has_negation, has_comparative, has_conditional, has_causal, num_count_match, length_ratio]
        n_state = 6
        H = np.zeros((n_state, n_state))
        z = np.zeros(n_state)
        
        # Normalize features roughly to 0-1 scale for stability
        p_norm = [
            min(1.0, props['negations'] / 5.0),
            min(1.0, props['comparatives'] / 5.0),
            min(1.0, props['conditionals'] / 5.0),
            min(1.0, props['causal'] / 5.0),
            min(1.0, len(props['numbers']) / 10.0),
            min(1.0, props['length'] / 500.0)
        ]
        
        c_norm = [
            min(1.0, cand_props['negations'] / 5.0),
            min(1.0, cand_props['comparatives'] / 5.0),
            min(1.0, cand_props['conditionals'] / 5.0),
            min(1.0, cand_props['causal'] / 5.0),
            min(1.0, len(cand_props['numbers']) / 10.0),
            min(1.0, cand_props['length'] / 500.0)
        ]

        # Identity measurement matrix (we observe state directly)
        H = np.eye(n_state)
        
        # Measurement z is derived from prompt constraints
        # If prompt has numbers, we expect candidate to engage with them (simplified heuristic)
        z = np.array(p_norm)
        
        # Adjust z based on candidate alignment (The "Measurement" of the candidate against prompt logic)
        # If candidate lacks a feature present in prompt, innovation occurs
        z_observed = np.array(c_norm)
        
        return H, z, z_observed

    def _kalman_update(self, x_h: np.ndarray, P_h: np.ndarray, H: np.ndarray, z: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Perform one step of Kalman filtering."""
        # Predict
        z_hat = H @ x_h
        
        # Innovation
        y = z - z_hat
        
        # Innovation covariance
        S = H @ P_h @ H.T + R
        
        # Kalman Gain
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.linalg.pinv(S)
            
        K = P_h @ H.T @ S_inv
        
        # Update state
        x_new = x_h + K @ y
        I = np.eye(P_h.shape[0])
        P_new = (I - K @ H) @ P_h
        
        # Normalized innovation squared (Mahalanobis distance) for falsification check
        try:
            innov_norm = float(np.sqrt(y.T @ S_inv @ y))
        except:
            innov_norm = 10.0
            
        return x_new, P_new, innov_norm

    def _falsification_test(self, prompt: str, candidate: str, base_features: Dict[str, Any]) -> int:
        """
        Generate perturbations and check if the candidate holds up.
        Returns count of falsifications.
        """
        falsifications = 0
        n_tests = 5
        
        for _ in range(n_tests):
            # Perturb features slightly
            delta = {k: 0 for k in base_features}
            pert_type = self.rng.choice(['negation_flip', 'number_shift', 'conditional_drop'])
            
            if pert_type == 'negation_flip':
                delta['negations'] = 1 if base_features['negations'] == 0 else 0
            elif pert_type == 'number_shift':
                delta['numbers'] = 1 
            elif pert_type == 'conditional_drop':
                delta['conditionals'] = 0
                
            # Construct perturbed candidate representation (simulated)
            # In this simplified model, we check if the candidate is robust to missing logic
            # If the prompt has conditionals but candidate doesn't, and we drop the conditional requirement,
            # a weak candidate might suddenly look better. 
            # Here we simulate: if candidate relies on exact match, small perturbation breaks it.
            
            cand_feats = self._extract_features(candidate)
            
            # Simple heuristic: if prompt has strong logic (conditionals/numbers) and candidate ignores them,
            # it fails falsification tests where those logic gates are randomized.
            if base_features['conditionals'] > 0 and cand_feats['conditionals'] == 0:
                if self.rng.random() < 0.8: # High probability of failure if logic ignored
                    falsifications += 1
            if base_features['numbers'] and not cand_feats['numbers']:
                 if self.rng.random() < 0.8:
                    falsifications += 1
                    
        return falsifications

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_features = self._extract_features(prompt)
        
        # Global noise covariance
        R = np.eye(6) * 0.1
        
        for cand in candidates:
            # 1. Initialize Prior (uncertain)
            x_h = np.zeros(6)
            P_h = np.eye(6) * 1.0 # Large variance
            
            # 2. Build Model
            H, z_prompt, z_cand = self._build_measurement_model(prompt, cand)
            
            # 3. Kalman Update (Treat candidate as hypothesis x_h, update against prompt truth z)
            # We invert the logic: We want to see how much the candidate (as a state) 
            # needs to change to match the prompt (measurement).
            # Actually, per spec: x_h is candidate state. z is prompt truth.
            # We update belief in candidate correctness.
            
            # Let's treat the "state" as the validity of the candidate's claims relative to prompt
            x_h = z_cand # Initial guess based on candidate content
            z = z_prompt # The ground truth constraints
            
            x_post, P_post, innov_norm = self._kalman_update(x_h, P_h, H, z, R)
            
            # 4. Falsification / Property-Based Testing
            fals_count = self._falsification_test(prompt, cand, prompt_features)
            
            # 5. Scoring
            # Lower determinant of P_post means higher confidence (less uncertainty)
            try:
                log_det = np.log(np.linalg.det(P_post) + 1e-9)
            except:
                log_det = 10.0
                
            score = -log_det - (self.lambda_penalty * fals_count) - (innov_norm * 0.5)
            
            # Boost if numeric constraints are satisfied exactly
            p_nums = prompt_features['numbers']
            c_nums = self._extract_features(cand)['numbers']
            if p_nums and c_nums:
                # Check simple ordering if possible
                try:
                    p_val = float(p_nums[0])
                    c_val = float(c_nums[0])
                    if p_val == c_val:
                        score += 2.0
                except:
                    pass

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Innovation: {innov_norm:.2f}, Falsifications: {fals_count}, Uncertainty: {-log_det:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        # Sigmoid mapping to 0-1
        # Heuristic scaling based on typical score ranges
        conf = 1.0 / (1.0 + math.exp(-raw_score + 2.0))
        return max(0.0, min(1.0, conf))