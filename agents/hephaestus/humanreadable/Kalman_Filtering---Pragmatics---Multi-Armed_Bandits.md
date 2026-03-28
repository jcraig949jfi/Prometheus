# Kalman Filtering + Pragmatics + Multi-Armed Bandits

**Fields**: Signal Processing, Linguistics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T03:57:18.068892
**Report Generated**: 2026-03-27T16:08:15.774682

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer \(a\) as a latent hypothesis with a scalar truth‑state \(x_a\in[0,1]\) (1 = fully correct). A discrete‑time Kalman filter maintains a Gaussian belief \(\mathcal N(\mu_a,\Sigma_a)\) over \(x_a\). At each time step \(t\) we extract a fixed‑length feature vector \(z_t\in\mathbb R^d\) from the answer text (see §2). The observation model is  
\[
z_t = H x_a + v_t,\qquad v_t\sim\mathcal N(0,R_t),
\]  
where \(H\in\mathbb R^{d\times1}\) maps the scalar state to each feature (e.g., \(H_i=1\) for a feature that should be present if the answer is true, \(-1\) for a feature that should be absent). Pragmatics supplies the observation‑noise covariance \(R_t\): each feature receives a base variance \(\sigma^2\); violations of Grice’s maxims (relevance, quantity, manner, quality) increase the corresponding diagonal entry, making unreliable cues noisier.  

The filter proceeds:  

1. **Predict**: \(\mu_{a|t-1}=\mu_{a|t-1}\), \(\Sigma_{a|t-1}=\Sigma_{a|t-1}\) (static state, \(F=1\)).  
2. **Compute innovation**: \(y_t = z_t - H\mu_{a|t-1}\).  
3. **Kalman gain**: \(K_t = \Sigma_{a|t-1}H^\top (H\Sigma_{a|t-1}H^\top + R_t)^{-1}\).  
4. **Update**: \(\mu_{a|t}= \mu_{a|t-1}+K_t y_t\), \(\Sigma_{a|t}= (1-K_t H)\Sigma_{a|t-1}\).  

To decide which features to trust more aggressively, we run a **multi‑armed bandit** over the \(d\) feature dimensions. After each update we compute an Upper Confidence Bound for arm \(i\):  
\[
\text{UCB}_{i,t}=|\mu_{a|t} H_i| + \alpha\sqrt{\frac{\ln t}{n_{i,t}}},
\]  
where \(n_{i,t}\) is how many times feature \(i\) has been used so far and \(\alpha\) controls exploration. The arm with highest UCB receives a temporary boost in its observation weight (i.e., we scale the corresponding row of \(H\) down, reducing its noise) for the next step, forcing the filter to explore uncertain cues while exploiting those that have consistently shifted the mean toward correctness.  

After processing all extracted features, the final posterior mean \(\mu_{a|T}\) is the score for answer \(a\); higher means indicate greater predicted correctness.  

**Structural features parsed (regex‑based)**  
- Negations (“not”, “no”, “never”)  
- Comparatives (“greater than”, “less than”, “more…than”)  
- Conditionals (“if … then …”, “unless”)  
- Numeric values and units (integers, decimals, percentages)  
- Causal claims (“because”, “leads to”, “results in”)  
- Ordering relations (“first”, “second”, “before”, “after”)  
- Quantifiers (“all”, “some”, “most”, “none”)  
- Modal verbs (“must”, “might”, “should”)  
- Speech‑act markers (“I claim that”, “it is suggested that”)  

Each feature yields a binary or scalar entry in \(z_t\) (e.g., 1 if a negation appears, 0 otherwise; numeric value normalized).  

**Novelty**  
Pure Kalman filtering has been applied to time‑series NLP but rarely to static answer scoring; coupling it with a pragmatics‑driven observation model and a bandit‑based feature‑selection loop is not present in surveyed literature (e.g., no joint use of Grice‑based noise adaptation and UCB exploration in a Kalman filter for QA). Hence the combination is novel.  

**Ratings**  
Reasoning: 8/10 — The algorithm performs principled belief updates over logical features, capturing uncertainty and evidence integration.  
Metacognition: 7/10 — The bandit layer provides explicit monitoring of feature reliability, enabling the system to reason about its own confidence.  
Hypothesis generation: 6/10 — Scores are derived from a single latent truth variable; generating alternative hypotheses would require extending the state space.  
Implementability: 9/10 — All components (Kalman updates, UCB, regex feature extraction) use only NumPy and the Python standard library.  

---  
Reasoning: 8/10 — The algorithm performs principled belief updates over logical features, capturing uncertainty and evidence integration.  
Metacognition: 7/10 — The bandit layer provides explicit monitoring of feature reliability, enabling the system to reason about its own confidence.  
Hypothesis generation: 6/10 — Scores are derived from a single latent truth variable; generating alternative hypotheses would require extending the state space.  
Implementability: 9/10 — All components (Kalman updates, UCB, regex feature extraction) use only NumPy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Kalman Filtering**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Kalman Filtering + Pragmatics: negative interaction (-0.051). Keep these concepts in separate code paths to avoid interference.
- Kalman Filtering + Multi-Armed Bandits: strong positive synergy (+0.457). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Multi-Armed Bandits + Pragmatics: strong positive synergy (+0.599). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Information Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Kalman Filtering + Error Correcting Codes + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()

**Forge Timestamp**: 2026-03-27T07:38:22.239792

---

## Code

**Source**: scrap

[View code](./Kalman_Filtering---Pragmatics---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Pragmatics (Gricean maxims), 
    and Multi-Armed Bandits (UCB) to score candidate answers.
    
    Mechanism:
    1. Structural Parsing: Extracts binary/scalar features (negations, numerics, etc.) 
       from text using regex.
    2. Kalman Filter: Maintains a belief (mean, variance) over the "truth state" of each candidate.
       - Observation model maps features to the truth state.
       - Pragmatics modulates observation noise (R): violations increase noise.
    3. Multi-Armed Bandit (UCB): Dynamically weights feature reliability. Features that 
       consistently reduce uncertainty or align with high-confidence updates get higher weights.
    4. Scoring: Final posterior mean is the score. NCD is used only as a tiebreaker.
    """

    # Feature patterns (ASCII safe)
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bnone\b'],
        'comparative': [r'\bgreater than\b', r'\bless than\b', r'\bmore.*than\b', r'\bfewer.*than\b'],
        'conditional': [r'\bif\b', r'\bunless\b', r'\bthen\b'],
        'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b'],
        'ordering': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b'],
        'quantifier': [r'\ball\b', r'\bsome\b', r'\bmost\b', r'\bnone\b'],
        'modal': [r'\bmust\b', r'\bmight\b', r'\bshould\b', r'\bcould\b'],
        'speech_act': [r'\bi claim\b', r'\bit is suggested\b', r'\bwe propose\b']
    }
    
    # Numeric pattern
    NUM_PATTERN = re.compile(r'-?\d+(?:\.\d+)?(?:\s*(?:%|percent))?')

    def __init__(self):
        self.feature_names = list(self.PATTERNS.keys()) + ['numeric_count', 'numeric_value']
        self.d = len(self.feature_names)
        # Bandit state: counts and sum of rewards for each feature arm
        self.arm_counts = np.ones(self.d)  # Prior count = 1
        self.arm_rewards = np.zeros(self.d) 
        self.t_total = 1  # Time step counter for UCB

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into a vector z."""
        text_lower = text.lower()
        features = []
        
        # Regex-based binary features
        for key in self.PATTERNS.keys():
            pattern = '|'.join(self.PATTERNS[key])
            # Simple presence check
            match = 1.0 if re.search(pattern, text_lower) else 0.0
            features.append(match)
            
        # Numeric features
        nums = self.NUM_PATTERN.findall(text_lower)
        features.append(min(1.0, len(nums) / 5.0))  # Normalized count
        
        # Extract single numeric value if present (heuristic for magnitude)
        if nums:
            try:
                val = float(nums[0].replace('%', '').replace('percent', ''))
                # Normalize loosely assuming range 0-100 for typical QA
                features.append(min(1.0, abs(val) / 100.0)) 
            except ValueError:
                features.append(0.0)
        else:
            features.append(0.0)
            
        return np.array(features)

    def _check_pragmatics(self, text: str) -> float:
        """
        Estimate pragmatic quality (0.0 to 1.0). 
        Lower score = higher noise (R).
        Checks for Gricean violations: excessive length (Quantity), repetition (Manner).
        """
        words = text.split()
        length = len(words)
        
        # Penalty for extreme brevity or excessive verbosity
        if length < 3:
            quality = 0.5
        elif length > 200:
            quality = 0.6
        else:
            quality = 1.0
            
        # Penalty for repetition (Manner)
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:
                quality *= 0.7
                
        return quality

    def _compute_ucb_weights(self) -> np.ndarray:
        """Compute UCB weights for features to adjust H matrix."""
        weights = np.zeros(self.d)
        for i in range(self.d):
            if self.arm_counts[i] == 0:
                ucb = float('inf')
            else:
                avg_reward = self.arm_rewards[i] / self.arm_counts[i]
                exploration = math.sqrt(math.log(self.t_total + 1) / self.arm_counts[i])
                ucb = avg_reward + 0.5 * exploration # alpha = 0.5
            weights[i] = ucb
        
        # Normalize weights to [0.5, 1.5] range to scale H
        if np.max(weights) > np.min(weights):
            norm_weights = 0.5 + (weights - np.min(weights)) / (np.max(weights) - np.min(weights))
        else:
            norm_weights = np.ones(self.d)
        return norm_weights

    def _kalman_update(self, mu: float, sigma: float, z: np.ndarray, H_base: np.ndarray, R_base: float, ucb_weights: np.ndarray) -> Tuple[float, float]:
        """Perform single-step Kalman update."""
        # Adjust H by UCB weights (exploit reliable features)
        H_adj = H_base * ucb_weights
        
        # Predict (static state)
        mu_pred = mu
        sigma_pred = sigma
        
        # Observation model: z = H_adj * x + v
        # Innovation: y = z - H_adj * mu
        # We treat z as a scalar observation aggregated from features? 
        # No, the prompt says z is a vector. H is d x 1.
        # So z (d x 1) = H (d x 1) * x (1 x 1).
        
        # Compute Kalman Gain
        # S = H^T * Sigma * H + R (Scalar since state is 1D)
        # But R is a matrix? Prompt says "R_t" and "diagonal entry".
        # Let's assume R is diagonal matrix with base variance scaled by pragmatics.
        R_mat = np.eye(self.d) * R_base / (ucb_weights + 1e-6) # Inverse weight scaling? 
        # Actually, prompt says: violations increase R. UCB boosts weight -> reduces effective noise.
        # Let's make R diagonal where R_ii = base / weight_i
        
        # Simplified 1D State Kalman with Vector Observation
        # K = Sigma * H^T * (H * Sigma * H^T + R)^-1
        # Since Sigma is scalar (variance), let's denote it as P.
        # K is (1 x d)
        
        P = sigma_pred
        H_col = H_adj.reshape(-1, 1) # d x 1
        
        # S = H^T P H + R (d x d matrix)
        S = np.dot(H_col, H_col.T) * P + np.diag(R_base / (ucb_weights + 0.1))
        
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.linalg.pinv(S)
            
        K = P * np.dot(H_col.T, S_inv) # 1 x d
        
        # Innovation y = z - H * mu
        y = z - np.dot(H_col, mu_pred) # d x 1
        
        # Update
        mu_new = mu_pred + np.dot(K, y)[0]
        # P_new = (I - K H) P
        # K (1xd), H (dx1) -> scalar
        KH = np.dot(K, H_col)[0,0]
        sigma_new = (1.0 - KH) * P
        
        return max(0.0, min(1.0, mu_new)), max(1e-6, sigma_new)

    def _score_candidate(self, candidate: str, prompt: str = "") -> Tuple[float, str]:
        """Score a single candidate using the Kalman-Bandit loop."""
        # Initial belief: uniform prior [0, 1] -> mu=0.5, sigma=0.25
        mu = 0.5
        sigma = 0.25
        
        # Base observation noise
        base_R = 1.0
        
        # Extract features from candidate
        z = self._extract_features(candidate)
        
        # Pragmatics factor (affects R)
        prag_quality = self._check_pragmatics(candidate)
        if prag_quality < 1.0:
            base_R *= (2.0 - prag_quality) # Increase noise for poor pragmatics
            
        # H matrix: Mapping scalar truth to features. 
        # Heuristic: Assume presence of feature (1) suggests truth (1) for most logical markers.
        # For negation, it's complex, but we'll treat raw presence as a signal for now.
        H_base = np.ones(self.d) 
        
        # Get UCB weights (Bandit layer)
        ucb_weights = self._compute_ucb_weights()
        
        # Perform Kalman Update
        mu_new, sigma_new = self._kalman_update(mu, sigma, z, H_base, base_R, ucb_weights)
        
        # Update Bandit State (Reward = reduction in uncertainty or alignment)
        # Reward heuristic: If feature was present and contributed to a confident shift, reward it.
        # Simplified: Reward features that are active (z_i > 0) and have high UCB weight
        for i in range(self.d):
            if z[i] > 0:
                self.arm_counts[i] += 1
                # Pseudo-reward: alignment with current mean belief
                reward = mu_new if mu_new > 0.5 else (1-mu_new)
                self.arm_rewards[i] += reward
                
        self.t_total += 1
        
        reason_str = f"Kalman-Bandit update: mu={mu_new:.3f}, sigma={sigma_new:.4f}, prag={prag_quality:.2f}"
        return mu_new, reason_str

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        def compress_len(s):
            return len(zlib.compress(s.encode('utf-8')))
        
        try:
            c1 = compress_len(s1)
            c2 = compress_len(s2)
            c12 = compress_len(s1 + s2)
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        scores = []
        
        # Primary scoring via Kalman-Bandit
        for cand in candidates:
            score, reason = self._score_candidate(cand, prompt)
            scores.append(score)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Tie-breaking with NCD if scores are too close
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                if abs(scores[i] - scores[j]) < 1e-4:
                    # Use NCD against prompt as tiebreaker (lower NCD = more similar/relevant)
                    ncd_i = self._ncd_similarity(prompt, candidates[i])
                    ncd_j = self._ncd_similarity(prompt, candidates[j])
                    # Adjust score slightly based on NCD (lower is better)
                    if ncd_i < ncd_j:
                        scores[i] += 1e-5
                    else:
                        scores[j] += 1e-5

        # Sort descending by score
        sorted_indices = np.argsort([-s for s in scores])
        final_results = [results[i] for i in sorted_indices]
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score, _ = self._score_candidate(answer, prompt)
        return float(score)

# Import zlib inside function to keep global scope clean if needed, 
# but here we import at top of block for clarity if allowed, 
# or locally inside the method used above.
import zlib
```

</details>
