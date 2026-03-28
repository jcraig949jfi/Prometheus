import re
import numpy as np
from itertools import combinations
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Neural Architecture Search (NAS) over pragmatic propositions 
    guided by the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts logical features (negations, comparatives, conditionals, 
       causality, ordering, numbers) from the prompt and candidates.
    2. NAS Loop: Enumerates masks (subsets of features, size <= 4).
    3. Optimization: For each mask, solves ridge regression to find weights that 
       best predict truth values based on feature presence.
    4. Free Energy: Computes F = Prediction Error + lambda * Complexity.
    5. Scoring: Selects the mask minimizing F. Candidate score = -F.
    """
    
    def __init__(self):
        self.lambda_reg = 0.1
        self.max_features = 4
        # Regex patterns for pragmatic features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|equal|bigger|smaller)\b', re.I),
            'conditional': re.compile(r'\b(if|then|provided|unless|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|leads|results|causes)\b', re.I),
            'ordering': re.compile(r'\b(before|after|precedes|follows|first|last)\b', re.I),
            'numbers': re.compile(r'\d+\.?\d*')
        }
        self.feature_keys = list(self.patterns.keys())
        self.k = len(self.feature_keys)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary features and numeric values from text."""
        text_lower = text.lower()
        features = np.zeros(self.k)
        
        # Binary flags
        for i, key in enumerate(self.feature_keys):
            if key == 'numbers':
                continue
            if self.patterns[key].search(text):
                features[i] = 1.0
        
        # Numeric comparison logic (simplified for single prompt context)
        nums = self.patterns['numbers'].findall(text)
        if len(nums) >= 2:
            # Check for comparative context to activate 'numbers' feature strongly
            # or derive a boolean truth if the prompt implies a check
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                # Heuristic: If prompt has numbers and comparative words, mark feature
                if features[self.feature_keys.index('comparative')] > 0:
                    features[self.feature_keys.index('numbers')] = 1.0
            except ValueError:
                pass
                
        return features

    def _generate_synthetic_training(self, prompt: str, candidates: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data (X, y) based on logical consistency.
        Since we don't have external data, we simulate 'truth' by checking 
        if the candidate preserves the structural constraints of the prompt.
        """
        prompt_feats = self._extract_features(prompt)
        X_data = []
        y_data = []
        
        # Create variations of the prompt features to simulate training samples
        # Base case: Prompt features match prompt (High truth)
        base_sample = np.concatenate([prompt_feats, np.zeros(self.k)]) # Placeholder for candidate feats
        
        # We simulate N samples by perturbing feature masks
        # In this specific implementation, we treat the "training" as evaluating 
        # how well the candidate's features align with the prompt's required logic.
        
        # To satisfy the NAS/Ridge requirement strictly:
        # We construct a tiny dataset where 'True' samples are those where 
        # candidate features mirror prompt features, and 'False' where they contradict.
        
        samples = []
        labels = []
        
        # Sample 1: Ideal match (Prompt features present)
        samples.append(prompt_feats)
        labels.append(1.0)
        
        # Sample 2: Negation flip (Simulate error case)
        neg_sample = prompt_feats.copy()
        if prompt_feats[0] > 0: neg_sample[0] = 0 # Flip negation
        else: neg_sample[0] = 1
        samples.append(neg_sample)
        labels.append(0.0)
        
        # Sample 3: Zero vector (No logic)
        samples.append(np.zeros(self.k))
        labels.append(0.0)
        
        return np.array(samples), np.array(labels)

    def _compute_free_energy(self, X: np.ndarray, y: np.ndarray, mask: np.ndarray) -> float:
        """Compute Free Energy: Prediction Error + Complexity."""
        # Apply mask
        active_indices = np.where(mask == 1)[0]
        if len(active_indices) == 0:
            return 1e6 # High energy for empty set
            
        X_masked = X[:, active_indices]
        
        # Ridge Regression: w = (X^T X + lambda I)^-1 X^T y
        # Using numpy.linalg.lstsq for stability
        try:
            # Add bias term implicitly by centering or just solving raw
            # Simple ridge solution
            reg_matrix = self.lambda_reg * np.eye(len(active_indices))
            XtX = X_masked.T @ X_masked + reg_matrix
            Xty = X_masked.T @ y
            
            # Solve linear system
            w, _, _, _ = np.linalg.lstsq(XtX, Xty, rcond=None)
            
            # Prediction
            y_hat = X_masked @ w
            mse = np.mean((y - y_hat) ** 2)
            complexity = np.sum(w ** 2)
            
            return mse + self.lambda_reg * complexity
        except np.linalg.LinAlgError:
            return 1e6

    def _find_best_mask(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Run NAS loop to find mask minimizing Free Energy."""
        # Combine prompt and candidate for feature extraction context
        # We evaluate if the candidate satisfies the prompt's logical structure
        full_text = f"{prompt} {candidate}"
        feats = self._extract_features(full_text)
        
        # Expand to matrix for the solver (using synthetic variations)
        X, y = self._generate_synthetic_training(prompt, [candidate])
        
        # If X is too small for the mask size, pad or adjust
        # Here we rely on the specific structure of _generate_synthetic_training
        
        best_F = float('inf')
        best_mask_str = ""
        
        # Enumerate masks (NAS)
        # We iterate over number of active features from 1 to max_features
        for r in range(1, self.max_features + 1):
            for indices in combinations(range(self.k), r):
                mask = np.zeros(self.k)
                mask[list(indices)] = 1.0
                
                # We need to project our specific candidate features into the training framework
                # Since we only have one candidate instance to score, we simulate the 
                # "prediction error" by seeing how well the masked features of the 
                # candidate align with the "ideal" truth pattern derived from the prompt.
                
                # Simplified F calculation for the specific candidate:
                # We use the synthetic training set generated from the prompt logic
                # and see how well the candidate's features (repeated) fit the model 
                # trained on the prompt's logical expectations.
                
                # To make this work with the defined interface:
                # We train on the synthetic set, then check error on the candidate's actual feature vector
                # treated as a single test point? 
                # No, the formula says F = Avg(Error) + Complexity.
                # Let's train on the synthetic set (which represents the logical rules)
                # and evaluate the error on the "truth" defined by the candidate's consistency.
                
                # Actually, let's strictly follow the prompt's math:
                # Train w on synthetic data (rules), then compute F.
                # But F is defined on the training set in the prompt description?
                # "F(a) = 1/N sum (y_i - y_hat_i)^2 ..."
                # We calculate F for the model defined by the mask.
                # Lower F means the mask explains the logical rules (synthetic data) better.
                # Then we bias this by how well the candidate fits.
                
                F_val = self._compute_free_energy(X, y, mask)
                
                # Penalty if candidate doesn't match the prompt's active features
                # This couples the candidate to the score
                candidate_feat_match = 0.0
                if np.sum(mask) > 0:
                    # How much of the mask is satisfied by the candidate+prompt combo?
                    candidate_feat_match = np.sum(feats * mask) / np.sum(mask)
                
                # Adjust F: High match reduces Free Energy (better score)
                # This is the pragmatic link: The hypothesis (mask) must explain the data (candidate)
                adjusted_F = F_val - (0.5 * candidate_feat_match) 
                
                if adjusted_F < best_F:
                    best_F = adjusted_F
                    best_mask_str = f"Mask[{','.join(map(str, indices))}]"
        
        return -best_F, best_mask_str # Score is negative Free Energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._find_best_mask(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Minimized Free Energy via NAS on pragmatic features. Active logic mask identified."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score, _ = self._find_best_mask(prompt, answer)
        # Normalize score roughly to 0-1 range based on typical F values
        # F is usually small positive. -F is negative. 
        # We want higher score -> higher confidence.
        # Transform: 1 / (1 + exp(F)) acts like a sigmoid on the energy
        import math
        conf = 1.0 / (1.0 + math.exp(score)) # If score is -F, and F is small, this is ~0.5-0.9
        # Heuristic adjustment to ensure discrimination
        conf = min(1.0, max(0.0, conf * 1.2)) 
        return float(conf)