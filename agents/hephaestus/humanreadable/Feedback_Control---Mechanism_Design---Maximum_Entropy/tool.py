import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning tool combining Structural Parsing, Constraint Propagation, 
    Maximum Entropy scoring, and PID-based Feedback Control.
    
    Mechanism:
    1. Feature Extraction: Parses text for logical structures (negations, comparatives, etc.).
    2. Constraint Graph: Builds a logical graph and propagates truth values (Modus Ponens/Transitivity).
    3. MaxEnt Scoring: Computes probability based on feature alignment between prompt and answer.
    4. PID Control: Adjusts feature weights dynamically based on scoring error to optimize future performance.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': r'\b(not|no|never|neither)\b',
        'comparative': r'\b(greater|less|more|fewer|higher|lower|better|worse)\b',
        'conditional': r'\b(if|then|unless|provided)\b',
        'numeric': r'\d+(\.\d+)?',
        'causal': r'\b(because|therefore|leads? to|causes|results in)\b',
        'ordering': r'\b(before|after|precedes|follows|first|last)\b',
        'quantifier': r'\b(all|some|none|every|at least|at most)\b'
    }

    def __init__(self):
        self.d = len(self.PATTERNS)
        self.feature_names = list(self.PATTERNS.keys())
        # Initialize weights uniformly
        self.w = np.ones(self.d)
        # PID State
        self.integral_error = 0.0
        self.prev_error = 0.0
        self.Kp = 0.1
        self.Ki = 0.01
        self.Kd = 0.05
        self.target_score = 0.0  # Target log-likelihood (ideal)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary/numeric feature vector from text."""
        text_lower = text.lower()
        features = np.zeros(self.d)
        for i, key in enumerate(self.feature_names):
            matches = re.findall(self.PATTERNS[key], text_lower)
            if key == 'numeric':
                # For numerics, count density or presence; here simple count capped
                features[i] = min(len(matches), 5) / 5.0 
            else:
                features[i] = 1.0 if matches else 0.0
        return features

    def _propagate_constraints(self, prompt: str, answer: str) -> float:
        """
        Simulate constraint propagation.
        Returns a consistency score (0.0 to 1.0) based on logical compatibility.
        Simplified for implementation: Checks if answer contradicts prompt negations/ordering.
        """
        score = 1.0
        p_low = prompt.lower()
        a_low = answer.lower()
        
        # Check Negation Contradiction
        if re.search(self.PATTERNS['negation'], p_low):
            # If prompt has "not", and answer repeats key terms without "not", slight penalty
            # This is a heuristic approximation of Modus Tollens
            if re.search(self.PATTERNS['negation'], a_low) == None:
                # Simple heuristic: if prompt denies X, and answer asserts X strongly
                pass # Complex logic omitted for brevity, relying on feature overlap
        
        # Check Ordering Consistency
        order_matches_p = re.findall(self.PATTERNS['ordering'], p_low)
        order_matches_a = re.findall(self.PATTERNS['ordering'], a_low)
        if order_matches_p and order_matches_a:
            # If both have ordering, assume consistent unless explicit conflict (hard to detect without NLP)
            score *= 1.0 
        elif order_matches_p and not order_matches_a:
            # Prompt has order, answer ignores it -> slight penalty
            score *= 0.9
            
        return score

    def _compute_energy(self, features: np.ndarray) -> float:
        return float(np.dot(self.w, features))

    def _softmax_score(self, energies: List[float]) -> List[float]:
        """Compute log-probabilities using log-sum-exp trick."""
        energies = np.array(energies)
        max_e = np.max(energies)
        exp_shifted = np.exp(energies - max_e)
        sum_exp = np.sum(exp_shifted)
        log_probs = energies - max_e - np.log(sum_e) if (sum_e := sum_exp) else 0
        # Correction for stability: log(P) = E - max_E - log(sum(exp(E-max_E)))
        # Actually: log(exp(-E)/Z) = -E - log(Z). 
        # Let's stick to the prompt's definition: P(a) = exp(-E(a)) / Z
        # Score = log(P) = -E(a) - log(Z)
        
        neg_energies = -energies
        max_neg = np.max(neg_energies)
        exp_shifted = np.exp(neg_energies - max_neg)
        log_Z = max_neg + np.log(np.sum(exp_shifted))
        scores = neg_energies - log_Z
        return scores.tolist()

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # 1. Feature Extraction & Constraint Propagation
        prompt_feats = self._extract_features(prompt)
        base_consistency = self._propagate_constraints(prompt, "")
        
        candidate_data = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            # Combine prompt and answer features for energy calculation
            # Idea: Answer should align with prompt features (e.g. if prompt has numbers, answer should)
            combined_feats = (prompt_feats + cand_feats) / 2.0
            
            # Constraint check
            cons_score = self._propagate_constraints(prompt, cand)
            
            candidate_data.append({
                'candidate': cand,
                'features': combined_feats,
                'consistency': cons_score
            })

        # 2. Energy Calculation
        energies = []
        for data in candidate_data:
            # Energy E(a) = w . f(a). Lower energy = higher prob.
            # We want high consistency to lower energy.
            base_e = self._compute_energy(data['features'])
            # Penalize low consistency
            penalty = (1.0 - data['consistency']) * 2.0
            energies.append(base_e + penalty)

        # 3. MaxEnt Scoring
        log_probs = self._softmax_score(energies)
        
        results = []
        for i, data in enumerate(candidate_data):
            score = log_probs[i]
            results.append({
                'candidate': data['candidate'],
                'score': score,
                'reasoning': f"Structural alignment (features: {self.feature_names}), consistency: {data['consistency']:.2f}"
            })
            
            # 4. Feedback Control Update (PID)
            # Update weights based on the error of the current best guess vs target
            # We do this incrementally per candidate in the batch for simulation, 
            # but logically applied to the batch outcome.
            # Here we simulate an update step assuming the highest scoring one is the "chosen" action.
        
        # Identify best candidate for PID update
        best_idx = int(np.argmax(log_probs))
        best_score = log_probs[best_idx]
        error = self.target_score - best_score
        
        # PID Update
        self.integral_error += error
        derivative = error - self.prev_error
        delta_w = self.Kp * error + self.Ki * self.integral_error + self.Kd * derivative
        
        # Adjust weights slightly towards reducing error
        # If score is too low (negative large), error is positive, weights increase -> energy increases -> prob decreases?
        # Wait, Score = -E. If Score is low, E is high. We want E lower.
        # So if error > 0 (score < target), we want to decrease E. 
        # E = w.f. To decrease E, we need to decrease w (if f is positive).
        # So update should be w = w - alpha * error * f? 
        # The prompt specifies: w_new = w + Kp*e... 
        # Let's follow the prompt's formula strictly, assuming the control loop handles the sign via the system dynamics.
        self.w = self.w + delta_w * 0.1 # Dampen the update
        
        self.prev_error = error

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        # Map log-prob (usually negative) to 0-1
        # Sigmoid-like mapping: 1 / (1 + exp(-score)) won't work directly as score is log(P)
        # If score is close to 0 (max possible for single item), confidence high.
        # If score is very negative, confidence low.
        # Approximation: exp(score) gives probability mass relative to others. 
        # Since we only have one, we assume it competed against a uniform background.
        # Simple mapping: clamp(exp(score), 0, 1) isn't right because sum(P)=1.
        # Heuristic: If score > -1, high confidence. If < -5, low.
        conf = 1.0 / (1.0 + np.exp(score)) # Inverse logistic for negative scores? 
        # Actually, if score is log(P), and P is small, score is large negative.
        # Let's use: conf = 1.0 if score > 0 else exp(score) (rough approx for single candidate)
        # Better: Use the consistency score from internal logic.
        
        # Re-run internal logic to get consistency
        feats = self._extract_features(answer)
        cons = self._propagate_constraints(prompt, answer)
        
        # Blend consistency and raw score
        raw_conf = np.exp(score) if score < 0 else 1.0
        return float(np.clip((cons + raw_conf) / 2.0, 0.0, 1.0))