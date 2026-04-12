import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, sparse ecological dynamics, 
    and property-based perturbation testing.
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical features (negations, comparatives, 
       conditionals, causality, numbers) to form a binary feature vector.
    2. Sparse Eco-Dynamics (Secondary/Validation): Treats features as species. Uses a 
       fixed interaction matrix (mutualism/predation) to simulate one step of Lotka-Volterra 
       dynamics. Reconstruction error after dynamics serves as a coherence score.
    3. Property-Based Testing (Robustness): Generates minimal perturbations (negation flips, 
       number shifts). Fragility (score drop under perturbation) penalizes the final score.
    4. Scoring: Base score from structural match + eco-coherence - fragility penalty. 
       NCD used only as a tiebreaker.
    """

    def __init__(self):
        # Feature keys for structural parsing
        self.feature_keys = [
            'has_negation', 'has_comparative', 'has_conditional', 
            'has_causal', 'has_ordering', 'has_numeric', 'is_affirmative'
        ]
        self.num_features = len(self.feature_keys)
        
        # Eco-interaction matrix (A): Simulated mutualism/predation
        # Diagonal is self-limitation, off-diagonal represents co-occurrence constraints
        # Index mapping: 0:neg, 1:comp, 2:cond, 3:caus, 4:ord, 5:num, 6:aff
        self.A = np.zeros((self.num_features, self.num_features))
        # Negation and Affirmative are predatory (mutually exclusive)
        self.A[0, 6] = -1.0 
        self.A[6, 0] = -1.0
        # Comparatives and Numerics often co-occur (mutualism)
        self.A[1, 5] = 0.5
        self.A[5, 1] = 0.5
        # Conditionals and Causals have mild mutualism
        self.A[2, 3] = 0.3
        self.A[3, 2] = 0.3
        # Self limitation (beta term equivalent in simplified dynamics)
        np.fill_diagonal(self.A, -0.5)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        t = text.lower()
        features = np.zeros(self.num_features)
        
        # Negation
        if re.search(r'\b(not|no|never|neither|none)\b', t):
            features[0] = 1.0
            
        # Comparative
        if re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', t) or \
           re.search(r'[<>]', t):
            features[1] = 1.0
            
        # Conditional
        if re.search(r'\b(if|unless|provided|otherwise)\b', t):
            features[2] = 1.0
            
        # Causal
        if re.search(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', t):
            features[3] = 1.0
            
        # Ordering
        if re.search(r'\b(before|after|precedes|follows|first|last)\b', t):
            features[4] = 1.0
            
        # Numeric
        if re.search(r'\d+(\.\d+)?', t):
            features[5] = 1.0
            
        # Affirmative (simple heuristic: no negation + presence of subject-verb-like structure)
        # Simplified: if no negation and length > 5, assume affirmative context
        if features[0] == 0 and len(t) > 5:
            features[6] = 1.0
            
        return features

    def _eco_dynamics_score(self, z: np.ndarray) -> float:
        """
        Simulate one step of linearized Lotka-Volterra dynamics.
        z' = z + alpha*(Az) - beta*(z*z)
        Return reconstruction error as a measure of ecological fit.
        """
        alpha = 0.1
        beta = 0.1
        
        # Interaction term
        interaction = self.A @ z
        
        # Dynamics step
        z_prime = z + alpha * interaction - beta * (z * z)
        
        # Clamp to [0, 1] for stability
        z_prime = np.clip(z_prime, 0, 1)
        
        # Reconstruction error (Euclidean distance between original and evolved state)
        # Lower error means the features are stable under ecological constraints
        error = np.linalg.norm(z - z_prime)
        return float(1.0 / (1.0 + error)) # Convert to score (higher is better)

    def _generate_perturbations(self, text: str) -> List[str]:
        """Generate property-based perturbations."""
        perturbations = []
        t = text.lower()
        
        # 1. Negation flip
        if 'not' in t:
            perturbations.append(text.replace('not', '', 1))
        else:
            perturbations.append(text + " not")
            
        # 2. Number increment (simple regex find/replace)
        nums = re.findall(r'\d+', text)
        if nums:
            n = int(nums[0])
            perturbations.append(text.replace(nums[0], str(n + 1), 1))
            perturbations.append(text.replace(nums[0], str(max(0, n - 1)), 1))
            
        # 3. Conditional removal
        if 'if' in t:
            perturbations.append(re.sub(r'if.*?then?', '', text, flags=re.IGNORECASE))
            
        return perturbations

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feat = self._extract_features(prompt)
        prompt_eco = self._eco_dynamics_score(prompt_feat)
        
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            
            # 1. Structural Match Score (Dot product similarity)
            struct_score = float(np.dot(prompt_feat, cand_feat)) / max(1.0, np.sum(prompt_feat))
            
            # 2. Eco-Dynamics Coherence
            eco_score = self._eco_dynamics_score(cand_feat)
            
            # 3. Property-Based Robustness Test
            base_score = (struct_score * 0.6) + (eco_score * 0.4)
            perturbations = self._generate_perturbations(cand)
            fragility_penalty = 0.0
            
            if perturbations:
                scores = []
                for p in perturbations:
                    p_feat = self._extract_features(p)
                    p_eco = self._eco_dynamics_score(p_feat)
                    p_struct = float(np.dot(prompt_feat, p_feat)) / max(1.0, np.sum(prompt_feat))
                    scores.append((p_struct * 0.6) + (p_eco * 0.4))
                
                if scores:
                    # Penalty based on variance or drop from base
                    min_p_score = min(scores)
                    drop = base_score - min_p_score
                    fragility_penalty = max(0, drop) * 0.5 # Gamma factor

            final_score = base_score - fragility_penalty
            
            # Tiebreaker: NCD against prompt (only if scores are very close, handled implicitly by sorting stability)
            # We add a tiny NCD component to break ties logically
            ncd_val = self._compute_ncd(prompt, cand)
            final_score -= (ncd_val * 0.001) 

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, Eco:{eco_score:.2f}, Fragility:{fragility_penalty:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and eco-stability."""
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Structural alignment
        align = np.dot(p_feat, a_feat)
        max_possible = np.sum(p_feat) if np.sum(p_feat) > 0 else 1.0
        struct_conf = align / max_possible
        
        # Eco stability of the answer itself
        eco_conf = self._eco_dynamics_score(a_feat)
        
        # Combined confidence
        conf = (struct_conf * 0.7) + (eco_conf * 0.3)
        return float(np.clip(conf, 0.0, 1.0))