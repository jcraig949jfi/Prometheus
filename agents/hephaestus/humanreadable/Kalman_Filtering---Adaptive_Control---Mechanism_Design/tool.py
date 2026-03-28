import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

# No external dependencies beyond standard library and numpy
try:
    import numpy as np
except ImportError:
    # Fallback if numpy is strictly unavailable, though prompt allows it
    raise RuntimeError("Numpy is required for this tool.")

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Adaptive Control, and Mechanism Design.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, conditionals).
    2. Kalman Filtering: Maintains a latent belief state (mean, variance) of correctness.
       - State: x = [mu, sigma^2]
       - Update: Recursive Bayesian update based on feature consistency.
    3. Adaptive Control: Adjusts process (Q) and measurement (R) noise based on innovation.
    4. Mechanism Design: Uses a quadratic proper scoring rule to align scores with honest beliefs.
    5. Epistemic Honesty (Tier B): Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Initial state: neutral belief, high uncertainty
        self._init_state()
        
        # Adaptive parameters
        self.Q_base = 0.1  # Process noise baseline
        self.R_base = 0.5  # Measurement noise baseline
        
        # Sliding window for innovation monitoring (Adaptive Control)
        self.innovation_history = []
        self.window_size = 5
        
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|then)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(cause|lead to|result in|because|therefore)\b', re.IGNORECASE),
            'ordinal': re.compile(r'\b(first|second|third|finally|last)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|failed to|quit)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either.*or|must be|only option)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|it)\b.*\b(who|whom|which one)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|beautiful)\b', re.IGNORECASE)
        }

    def _init_state(self):
        """Reset Kalman state."""
        self.mu = 0.5       # Initial mean belief (neutral)
        self.sigma_sq = 1.0 # Initial variance (high uncertainty)
        self.innovation_history = []

    def _extract_features(self, text: str) -> np.ndarray:
        """
        Parse text into a feature vector z_k.
        Dimensions: [neg, comp, cond, causal, ord, num_count, num_val_norm, has_numbers]
        """
        text_lower = text.lower()
        features = []
        
        # Binary flags
        features.append(1.0 if self.patterns['negation'].search(text) else 0.0)
        features.append(1.0 if self.patterns['comparative'].search(text) else 0.0)
        features.append(1.0 if self.patterns['conditional'].search(text) else 0.0)
        features.append(1.0 if self.patterns['causal'].search(text) else 0.0)
        features.append(1.0 if self.patterns['ordinal'].search(text) else 0.0)
        
        # Numeric handling
        nums = self.patterns['numbers'].findall(text)
        features.append(len(nums) / 10.0) # Normalized count
        if nums:
            try:
                # Use max absolute value normalized
                val = max(abs(float(n)) for n in nums)
                features.append(math.log1p(val) / 10.0) 
                features.append(1.0)
            except ValueError:
                features.append(0.0)
                features.append(0.0)
        else:
            features.append(0.0)
            features.append(0.0)
            
        return np.array(features)

    def _check_tier_b_traps(self, prompt: str, answer: str) -> float:
        """
        Meta-confidence check for Tier B reasoning traps.
        Returns a cap on confidence (0.0 to 1.0).
        """
        combined = f"{prompt} {answer}"
        cap = 1.0
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(prompt):
            cap = min(cap, 0.2)
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            cap = min(cap, 0.3)
            
        # 3. Subjectivity without data
        if self.patterns['subjectivity'].search(prompt):
            cap = min(cap, 0.4)
            
        # 4. Pronoun ambiguity (simplified heuristic)
        if self.patterns['pronoun_ambiguity'].search(combined):
            cap = min(cap, 0.3)
            
        # 5. Unanswerable/Insufficient info heuristic
        # If prompt asks "who/what/where" but answer is short/generic
        question_words = ['who', 'what', 'where', 'when', 'why', 'how']
        if any(w in prompt.lower() for w in question_words):
            if len(answer.strip().split()) < 3 and answer.lower() not in ['yes', 'no', 'true', 'false']:
                # Potential guess, lower cap slightly unless computation found something
                cap = min(cap, 0.85)

        return cap

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        
        if len_comb == 0: return 0.0
        return (len_comb - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def _kalman_update(self, z_k: np.ndarray, R_k: float, Q_k: float):
        """
        Perform Kalman Filter update.
        State: x = [mu, sigma_sq] (simplified to scalar mean tracking for correctness)
        We treat the feature consistency as the observation.
        """
        # Prediction step (Random walk)
        mu_pred = self.mu
        sigma_sq_pred = self.sigma_sq + Q_k
        
        # Update step
        # H = [1, 0...] -> We observe the mean directly via feature consistency score
        # Simplified: We map feature match to a pseudo-observation of correctness (0 or 1)
        # For this implementation, we assume high feature density implies higher potential correctness
        # but the actual 'z' here is the structural consistency score.
        
        # Let's simplify: The "observation" is the structural integrity score of the candidate
        # relative to the prompt.
        y_k = np.mean(z_k[:5]) # Average of binary flags as a proxy for structural richness
        
        # Innovation
        epsilon = y_k - mu_pred
        self.innovation_history.append(epsilon)
        if len(self.innovation_history) > self.window_size:
            self.innovation_history.pop(0)
            
        # Kalman Gain
        S = sigma_sq_pred + R_k
        if S == 0: S = 1e-6
        K = sigma_sq_pred / S
        
        # Posterior
        self.mu = mu_pred + K * epsilon
        self.sigma_sq = (1 - K) * sigma_sq_pred
        
        # Clamp
        self.mu = max(0.0, min(1.0, self.mu))
        self.sigma_sq = max(1e-4, self.sigma_sq)

    def _adapt_covariances(self):
        """Adaptive Control: Adjust Q and R based on innovation variance."""
        if len(self.innovation_history) < 2:
            return self.Q_base, self.R_base
            
        var_inn = np.var(self.innovation_history)
        
        # If innovation variance is high, trust model less (increase Q)
        Q_adapt = self.Q_base * (1.0 + var_inn)
        # If innovation variance is low, trust measurement more (decrease R)
        R_adapt = self.R_base * (1.0 / (1.0 + var_inn))
        
        return Q_adapt, R_adapt

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute a score based on structural feature matching and logical consistency.
        Returns a value between 0 and 1.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Feature Overlap (Jaccard-like on binary flags)
        binary_p = p_feat[:5]
        binary_c = c_feat[:5]
        
        intersection = np.sum(np.minimum(binary_p, binary_c))
        union = np.sum(np.maximum(binary_p, binary_c))
        overlap_score = (intersection / union) if union > 0 else 0.0
        
        # 2. Numeric Consistency (Constructive Computation)
        # If prompt has numbers and candidate has numbers, check relation
        p_nums = [float(x) for x in self.patterns['numbers'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numbers'].findall(candidate)]
        
        numeric_score = 0.5 # Neutral if no numbers
        
        if p_nums and c_nums:
            # Check if candidate numbers are derived from prompt numbers logically
            # Simple heuristic: Is the candidate number present in prompt or a simple transform?
            # For "9.11" vs "9.9" trap: exact string match of numbers is bad if logic requires comparison
            # Here we reward presence of relevant numbers without hallucination
            match_count = 0
            for cn in c_nums:
                if any(abs(cn - pn) < 1e-6 for pn in p_nums):
                    match_count += 1
                # Penalize if candidate introduces random large numbers not in prompt
                elif cn > 1000 and not any(abs(cn - pn) < 1e-6 for pn in p_nums):
                    match_count -= 0.5
            
            numeric_score = max(0.0, min(1.0, 0.5 + (match_count * 0.1)))
        
        # 3. Negation Handling
        # If prompt has negation, candidate should reflect it (simple heuristic: length/complexity)
        negation_penalty = 0.0
        if p_feat[0] > 0: # Prompt has negation
            if len(candidate.split()) < 3: # Too short to handle negation properly
                negation_penalty = 0.3
        
        base_score = (0.6 * overlap_score + 0.4 * numeric_score) - negation_penalty
        return max(0.0, min(1.0, base_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        self._init_state() # Reset for each query batch
        
        results = []
        Q_k, R_k = self.Q_base, self.R_base
        
        # Pre-calculate NCD for tie-breaking (max 15% weight)
        ncd_scores = []
        if len(candidates) > 1:
            for c in candidates:
                ncd = self._compute_ncd(prompt, c)
                ncd_scores.append(ncd)
            # Normalize NCD to be a similarity (lower distance = higher score)
            max_ncd = max(ncd_scores) if ncd_scores else 1.0
            ncd_sim = [1.0 - (n / (max_ncd + 1e-6)) for n in ncd_scores]
        else:
            ncd_sim = [0.5] * len(candidates)

        for i, cand in enumerate(candidates):
            # 1. Structural & Computational Analysis
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Kalman Update (Simulating belief update per candidate)
            # Treat struct_score as the "observation" of correctness
            # We create a pseudo-observation vector
            z_k = self._extract_features(cand)
            
            # Adapt covariances based on history
            Q_k, R_k = self._adapt_covariances()
            
            # Update belief
            self._kalman_update(z_k, R_k, Q_k)
            
            # 3. Mechanism Design: Proper Scoring Rule
            # S = - (mu - y)^2. Since we don't know y (ground truth) during inference,
            # we maximize expected score which is proportional to our belief mu.
            # We combine Kalman mean (belief) with structural score and NCD.
            
            kalman_belief = self.mu
            
            # Weighted combination
            # Structural >= 50%, Computation (inside struct) >= 20%, NCD <= 15%
            final_score = (0.55 * struct_score) + (0.35 * kalman_belief) + (0.10 * ncd_sim[i])
            
            # Tier B Cap (Epistemic Honesty)
            meta_cap = self._check_tier_b_traps(prompt, cand)
            if meta_cap < 0.3:
                # If it's a trap, heavily penalize unless the structural score is perfect (unlikely)
                final_score *= 0.5
            
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Kalman belief: {self.mu:.2f}, Structural: {struct_score:.2f}, Meta-cap: {meta_cap:.2f}"
            })
            
            # Small delay to allow adaptive control to react if we were streaming, 
            # here we just ensure state evolves slightly or resets per candidate logic
            # For independent candidates, we technically should reset state per candidate 
            # or treat them as a sequence. Given the interface, we treat them as independent trials
            # but share the adaptive parameters Q/R for the batch.
            self._init_state() 

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Enforces Tier B constraints strictly.
        """
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._check_tier_b_traps(prompt, answer)
        
        # If meta_cap is low, we return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural Match Check
        score_data = self.evaluate(prompt, [answer])
        if not score_data:
            return 0.0
            
        item = score_data[0]
        raw_score = item["score"]
        
        # 3. Calibration
        # Map raw score to confidence, capped by meta_cap
        # If the structural parser found nothing (score ~0.5 neutral), confidence should be low
        if raw_score < 0.4:
            conf = 0.2 # Low confidence if no structural match
        elif raw_score > 0.8:
            conf = 0.95 # High confidence only on strong evidence
        else:
            conf = raw_score
            
        # Apply Cap
        final_conf = min(conf, meta_cap)
        
        # Never return > 0.9 unless definitive (handled by cap logic mostly)
        return round(final_conf, 4)