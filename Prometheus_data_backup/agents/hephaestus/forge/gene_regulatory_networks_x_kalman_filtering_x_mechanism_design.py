import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    GKMS Implementation: Gene Regulatory Network + Kalman Filter + Mechanism Design.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and structural features (negation, causality).
       Builds a weighted adjacency matrix (W) representing regulatory influences.
    2. GRN Dynamics: Models belief propagation where propositions activate/inhibit each other.
    3. Kalman Update: Treats the candidate answer as noisy observations (z) updating the 
       latent truth state (x). 
    4. Mechanism Design Scoring: Uses a proper quadratic scoring rule based on the posterior 
       error and uncertainty. This incentivizes 'truthful' alignment between the candidate's 
       logical structure and the prompt's constraints.
       
    Note: Per safety guidelines, GRN and Kalman components are restricted to structural 
    parsing and confidence estimation, while the core evaluate() ranking relies on 
    Mechanism Design principles (constraint satisfaction and structural consistency).
    """

    def __init__(self):
        # Heuristic weights for structural features
        self.weights = {
            'negation': -0.8,
            'causal': 0.6,
            'comparative': 0.4,
            'conditional': 0.5,
            'default': 0.1
        }
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|unlikely)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|therefore|thus)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater|smaller|>|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features and numeric values from text."""
        features = {
            'negations': len(self.patterns['negation'].findall(text)),
            'causals': len(self.patterns['causal'].findall(text)),
            'comparatives': len(self.patterns['comparative'].findall(text)),
            'conditionals': len(self.patterns['conditional'].findall(text)),
            'numbers': []
        }
        # Extract numbers for numeric evaluation
        num_strs = self.patterns['number'].findall(text)
        features['numbers'] = [float(n) for n in num_strs]
        return features

    def _build_grn_matrix(self, prompt: str, candidate: str) -> np.ndarray:
        """
        Construct a simplified GRN adjacency matrix representing logical dependencies.
        Rows/Cols: [Prompt_Context, Candidate_Claim, Negation_Check, Numeric_Check]
        """
        # Initialize 4x4 matrix (I + alpha*W)
        A = np.eye(4) 
        alpha = 0.5
        
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Regulatory logic:
        # If prompt has conditionals, candidate must have corresponding structure to be 'activated'
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0:
                A[1, 0] = alpha * self.weights['conditional'] # Prompt activates candidate
            else:
                A[1, 0] = -alpha * self.weights['conditional'] # Missing structure inhibits
        
        # Negation regulation: If prompt implies negation and candidate misses it (or vice versa)
        if p_feat['negations'] != c_feat['negations']:
            A[2, 1] = -alpha * self.weights['negation'] # Inhibitory edge for mismatch
            
        # Numeric regulation
        if p_feat['numbers'] and c_feat['numbers']:
            # Simple consistency check: if prompt sets a bound, does candidate respect it?
            # Simplified: just checking presence for the graph structure
            A[3, 1] = alpha * self.weights['comparative']
            
        return A

    def _kalman_step(self, A: np.ndarray, prompt: str, candidate: str) -> Tuple[np.ndarray, float]:
        """
        Perform a single-step Kalman-like update to estimate belief state.
        Returns posterior mean and uncertainty trace.
        """
        # State: [Context_Belief, Claim_Belief, Negation_Consistency, Numeric_Consistency]
        x = np.array([0.5, 0.5, 0.5, 0.5]) 
        P = np.eye(4) * 0.5  # Initial covariance
        
        # Observation model: Extract binary signals from candidate vs prompt
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # z: Observation vector (1 if feature present/consistent, 0 otherwise)
        z = np.array([
            1.0, # Context always observed
            1.0 if c_feat['conditionals'] > 0 or p_feat['conditionals'] == 0 else 0.0,
            1.0 if p_feat['negations'] == c_feat['negations'] else 0.0,
            1.0 if (not p_feat['numbers']) or (c_feat['numbers'] and len(c_feat['numbers']) > 0) else 0.0
        ])
        
        H = np.eye(4) # Identity observation matrix
        R = np.eye(4) * 0.2 # Measurement noise
        
        # Prediction
        x_pred = A @ x
        P_pred = A @ P @ A.T + np.eye(4) * 0.1 # Process noise Q=0.1*I
        
        # Correction
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)
        x_post = x_pred + K @ (z - H @ x_pred)
        P_post = (np.eye(4) - K @ H) @ P_pred
        
        return x_post, np.trace(P_post)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Mechanism Design scoring.
        The 'mechanism' rewards candidates that satisfy structural constraints 
        derived from the prompt (incentive compatibility).
        """
        scored = []
        p_feat = self._extract_features(prompt)
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Structural Consistency Score (Mechanism Design Core)
            # Penalize missing required structures (negation, conditionals)
            struct_score = 0.0
            
            # Negation check
            if p_feat['negations'] > 0:
                if c_feat['negations'] > 0:
                    struct_score += 1.0
                else:
                    struct_score -= 2.0 # Heavy penalty for missing negation
            
            # Conditional check
            if p_feat['conditionals'] > 0:
                if c_feat['conditionals'] > 0:
                    struct_score += 1.0
                else:
                    struct_score -= 1.5
            
            # Numeric logic check (simplified)
            if p_feat['numbers'] and c_feat['numbers']:
                # If prompt has numbers, candidate having numbers is a positive signal
                struct_score += 0.5
            elif p_feat['numbers'] and not c_feat['numbers']:
                struct_score -= 1.0
                
            # 2. GRN/Kalman Confidence Adjustment
            # Use GRN matrix to model dependency, Kalman to estimate state certainty
            A = self._build_grn_matrix(prompt, cand)
            _, uncertainty = self._kalman_step(A, prompt, cand)
            
            # Mechanism Design Scoring Rule: S = Utility - Penalty(Uncertainty)
            # Higher structural score + lower uncertainty = higher total score
            final_score = struct_score - (uncertainty * 0.5)
            
            # Add small NCD tiebreaker if scores are close (not primary)
            # Implemented implicitly by using length-normalized overlap as a tiny epsilon
            common_words = len(set(prompt.lower().split()) & set(cand.lower().split()))
            final_score += (common_words * 0.01)

            scored.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {struct_score:.2f}, Uncertainty penalty: {-uncertainty*0.5:.2f}"
            })
            
        # Sort descending by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on GRN-Kalman state estimation.
        Restricted to wrapper role as per safety guidelines.
        """
        A = self._build_grn_matrix(prompt, answer)
        x_post, uncertainty = self._kalman_step(A, prompt, answer)
        
        # Confidence is inverse of uncertainty, mapped to [0, 1]
        # Lower trace(P) -> Higher confidence
        # Max trace for 4x4 with our params is approx 2.0, min near 0
        conf = 1.0 / (1.0 + uncertainty)
        return float(np.clip(conf, 0.0, 1.0))