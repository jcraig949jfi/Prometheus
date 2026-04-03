from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple


class ReasoningTool:
    """
    Adaptive Kalman-Neuromodulated Sensitivity Scorer (AKNSS)
    
    Combines Kalman filtering, neuromodulation, and sensitivity analysis to score
    candidate answers by tracking state evolution of parsed logical features.
    
    Features tracked: negations, comparatives, conditionals, causality, numerics,
    ordering chains, quantifiers, modals. Kalman filter propagates uncertainty;
    neuromodulatory gain adapts feature weights; trajectory stability yields score.
    """
    
    def __init__(self):
        self.n_features = 9
        self.alpha = 0.15  # Neuromodulatory learning rate
        self.beta = 0.5    # Score scaling factor
        self.process_noise = 0.05
        self.sensor_noise = 0.1
        
    def _parse_features(self, text: str) -> np.ndarray:
        """Extract structural and logical features from text."""
        text_lower = text.lower()
        features = np.zeros(self.n_features)
        
        # 0: Negations
        features[0] = len(re.findall(r'\bnot\b|n\'t\b|never\b|no\b|none\b', text_lower))
        
        # 1: Comparatives
        features[1] = len(re.findall(r'\b(more|less|greater|fewer|higher|lower)\s+than\b', text_lower))
        features[1] += len(re.findall(r'[<>]=?', text))
        
        # 2: Conditionals
        features[2] = len(re.findall(r'\bif\b.*\bthen\b|\bwhen\b.*\bthen\b', text_lower))
        features[2] += len(re.findall(r'\bunless\b|\botherwise\b', text_lower))
        
        # 3: Causality
        features[3] = len(re.findall(r'\bbecause\b|\bsince\b|\bcauses?\b|\bleads?\s+to\b|\bresults?\s+in\b', text_lower))
        
        # 4: Numeric magnitude (sum of all numbers)
        nums = re.findall(r'-?\d+\.?\d*', text)
        features[4] = sum(abs(float(n)) for n in nums) if nums else 0
        
        # 5: Ordering/transitivity chains
        features[5] = len(re.findall(r'\b\w+\s*[<>]\s*\w+\s*[<>]\s*\w+', text))
        
        # 6: Quantifiers
        features[6] = len(re.findall(r'\b(all|every|each|some|any|most|few|many)\b', text_lower))
        
        # 7: Modals
        features[7] = len(re.findall(r'\b(must|should|might|may|could|would|can)\b', text_lower))
        
        # 8: Numeric count
        features[8] = len(nums)
        
        return features
    
    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """Constructive numeric evaluation."""
        p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt)]
        c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate)]
        
        if not c_nums:
            return 0.0
        
        # Check for comparison operators in prompt
        comp_match = re.search(r'(\d+\.?\d*)\s*([<>]=?)\s*(\d+\.?\d*)', prompt)
        if comp_match:
            left, op, right = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
            expected = eval(f"{left} {op} {right}")
            candidate_bool = 'yes' in candidate.lower() or 'true' in candidate.lower()
            return 1.0 if (expected == candidate_bool) else 0.0
        
        # Arithmetic evaluation
        if any(op in prompt for op in ['+', '-', '*', '/', '^']):
            try:
                prompt_clean = re.sub(r'[^\d+\-*/().\s]', '', prompt)
                if prompt_clean and c_nums:
                    expected = eval(prompt_clean.replace('^', '**'))
                    if abs(expected - c_nums[0]) < 0.01:
                        return 1.0
            except:
                pass
        
        return 0.3 if c_nums else 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _kalman_update(self, x_pred: np.ndarray, P_pred: np.ndarray, 
                       z: np.ndarray, H: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Kalman filter update step."""
        y = z - H @ x_pred
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)
        x_post = x_pred + K @ y
        P_post = (np.eye(len(x_pred)) - K @ H) @ P_pred
        return x_post, P_post
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect epistemic issues in the prompt."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you)\s+(stop|quit|cease)', p_lower):
            return 0.2
        if re.search(r'\bwhy\s+(did|does|do)\s+\w+\s+(fail|stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\btold\s+\w+\s+(he|she)\s+was', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either|only)\s+\w+\s+or\s+\w+\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(because|most|least|metric|measure)\b', p_lower):
            return 0.25
        
        # Insufficient information
        if re.search(r'\b(what|which|who)\b', p_lower) and len(prompt.split()) < 10:
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates using AKNSS."""
        z_prompt = self._parse_features(prompt)
        results = []
        
        for candidate in candidates:
            # Parse candidate features
            z_cand = self._parse_features(candidate)
            
            # Initialize Kalman state
            x_est = np.zeros(self.n_features)
            P_est = np.eye(self.n_features) * 1.0
            g = np.ones(self.n_features)  # Neuromodulatory gain
            
            # Process prompt as reference trajectory
            Q = np.eye(self.n_features) * self.process_noise
            R = np.eye(self.n_features) * self.sensor_noise
            
            # Prediction
            x_pred = x_est
            P_pred = P_est + Q
            
            # Neuromodulatory reward (similarity to prompt structure)
            reward = np.dot(z_cand, z_prompt) / (np.linalg.norm(z_cand) * np.linalg.norm(z_prompt) + 1e-6)
            g = g + self.alpha * (reward - g)
            g = np.clip(g, 0.5, 2.0)
            
            # Observation model with neuromodulation
            H = np.diag(g)
            
            # Update
            x_post, P_post = self._kalman_update(x_pred, P_pred, z_cand, H, R)
            
            # Score from trajectory stability (inverse uncertainty)
            trace_uncertainty = np.trace(P_post)
            kalman_score = np.exp(-self.beta * trace_uncertainty)
            
            # Structural alignment
            feature_diff = np.linalg.norm(z_cand - z_prompt)
            structural_score = np.exp(-0.1 * feature_diff)
            
            # Numeric computation
            numeric_score = self._compute_numeric_score(prompt, candidate)
            
            # NCD (tiebreaker only)
            ncd_score = 1.0 - self._ncd(prompt, candidate)
            
            # Weighted combination (dynamics >= 40%, structural >= 20%, numeric >= 20%, NCD <= 15%)
            final_score = (0.40 * kalman_score + 
                          0.25 * structural_score + 
                          0.25 * numeric_score + 
                          0.10 * ncd_score)
            
            # Reasoning explanation
            reasoning = f"Kalman={kalman_score:.2f} Struct={structural_score:.2f} Num={numeric_score:.2f} Trace={trace_uncertainty:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a prompt-answer pair."""
        # Meta-confidence check
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate answer
        results = self.evaluate(prompt, [answer])
        
        if not results:
            return 0.2
        
        base_score = results[0]["score"]
        
        # Check for definitive numeric computation
        numeric_score = self._compute_numeric_score(prompt, answer)
        if numeric_score > 0.9:
            return min(0.95, base_score * meta_conf)
        
        # Cap confidence unless very strong signal
        if base_score > 0.8:
            confidence_val = 0.75 * base_score
        else:
            confidence_val = 0.6 * base_score
        
        return min(confidence_val * meta_conf, 0.95)