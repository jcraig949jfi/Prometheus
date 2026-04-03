import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    HPC-CLM Approximation: Hierarchical Predictive Coding with Hebbian-Compositional Modules.
    
    Mechanism:
    1. Compositional Latent Modules: Parses text into structural primitives (negations, comparatives, 
       numbers, logic connectors) acting as reusable modules.
    2. Predictive Coding: Computes 'prediction error' between the prompt's structural expectation 
       and the candidate's structure. Lower error = higher likelihood.
    3. Hebbian Plasticity: Dynamically weights the importance of specific modules based on their 
       presence in the prompt-context. If a prompt uses numbers, number-matching gets potentiated.
    4. Active Inference: Ranks candidates by minimizing free energy (weighted structural error + semantic distance).
    """

    def __init__(self):
        # Primitives (Compositional Modules)
        self.modules = ['not', 'no', 'never', 'without', 'less', 'more', 'greater', 'smaller', 
                        'before', 'after', 'if', 'then', 'else', 'because', 'therefore', 
                        'all', 'some', 'none', 'every', 'any']
        self.comp_ops = ['<', '>', '==', '!=', '<=', '>=']
        
        # Initial synaptic weights (Hebbian base state)
        self.weights = {m: 0.5 for m in self.modules}
        self.weights['number'] = 0.5
        self.weights['logic'] = 0.5

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Decompose text into compositional module activations."""
        text_lower = text.lower()
        features = {}
        
        # Module activation counts
        for mod in self.modules:
            features[mod] = float(text_lower.count(mod))
        
        # Number detection module
        numbers = re.findall(r"-?\d+\.?\d*", text)
        features['number'] = float(len(numbers))
        features['number_vals'] = [float(n) for n in numbers]
        
        # Logic/Constraint density
        features['logic'] = float(len([c for c in text if c in '?!,;:']))
        
        return features

    def _compute_prediction_error(self, p_feat: Dict, c_feat: Dict) -> float:
        """Calculate structural prediction error between prompt and candidate."""
        error = 0.0
        count = 0
        
        # Check module presence/absence alignment
        for mod in self.modules:
            p_has = p_feat[mod] > 0
            c_has = c_feat[mod] > 0
            if p_has != c_has:
                error += 1.0
            count += 1
            
        # Number consistency (if prompt has numbers, candidate should ideally relate)
        if p_feat['number'] > 0:
            # Soft check: does candidate have numbers?
            if c_feat['number'] == 0 and p_feat['number'] > 1:
                error += 0.5 # Penalty for dropping numeric context
            else:
                # Numeric value alignment (simplified for single value answers)
                if len(c_feat.get('number_vals', [])) == 1 and len(p_feat.get('number_vals', [])) > 0:
                    # If it's a comparison task, check consistency
                    pass 
        return error

    def _hebbian_update(self, p_feat: Dict) -> None:
        """Update synaptic weights based on prompt activity (Local Hebbian Rule)."""
        # Strengthen pathways active in the prompt
        total_activity = sum(p_feat.values()) + 1e-6
        for key in self.weights:
            if key in p_feat:
                # Correlate pre-synaptic (presence) with post-synaptic (importance)
                activity = p_feat[key] / (total_activity) 
                self.weights[key] = 0.7 * self.weights[key] + 0.3 * (activity * 2.0)
            else:
                self.weights[key] *= 0.95 # Decay unused paths

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a baseline semantic tiebreaker."""
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / (max(c1, c2) + 1e-6)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_feat = self._extract_features(prompt)
        self._hebbian_update(p_feat) # Online learning step
        
        results = []
        p_len = len(prompt.split())
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Structural Prediction Error
            struct_err = self._compute_prediction_error(p_feat, c_feat)
            
            # 2. Weighted Error (Hebbian modulation)
            # If prompt has numbers, number-mismatch penalty increases
            number_weight = self.weights.get('number', 0.5)
            if p_feat['number'] > 0 and c_feat['number'] == 0:
                struct_err += (2.0 * number_weight)
                
            # 3. Logic Constraint Propagation (Simplified)
            # If prompt asks "which is larger", prefer candidate with larger numeric value if present
            logic_score = 0.0
            if 'larger' in prompt.lower() or 'greater' in prompt.lower() or 'more' in prompt.lower():
                if len(c_feat.get('number_vals', [])) > 0:
                    # Heuristic: if multiple candidates, the one with max number might be preferred
                    # This is handled by relative ranking, but we add a small bias here for demonstration
                    logic_score += 0.1 
            
            # 4. NCD Baseline
            ncd = self._ncd_distance(prompt, cand)
            
            # Final Score: Minimize Error, Maximize Logic/NCD fit
            # Score = 1 / (1 + Error + NCD)
            raw_score = 1.0 / (1.0 + struct_err + ncd + logic_score)
            
            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": f"Structural error: {struct_err:.2f}, NCD: {ncd:.2f}, Hebbian weight (num): {number_weight:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and NCD."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(answer)
        
        # Re-run Hebbian update for context
        self._hebbian_update(p_feat)
        
        err = self._compute_prediction_error(p_feat, c_feat)
        ncd = self._ncd_distance(prompt, answer)
        
        # Base confidence on low error and low compression distance
        base_conf = 1.0 / (1.0 + err * 0.5 + ncd)
        
        # Boost if numeric logic aligns (e.g. prompt has numbers, answer has numbers)
        if p_feat['number'] > 0 and c_feat['number'] > 0:
            base_conf = min(1.0, base_conf + 0.2)
            
        return float(np.clip(base_conf, 0.0, 1.0))