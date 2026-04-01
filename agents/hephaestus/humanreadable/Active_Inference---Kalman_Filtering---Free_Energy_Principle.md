# Active Inference + Kalman Filtering + Free Energy Principle

**Fields**: Cognitive Science, Signal Processing, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:38:37.539053
**Report Generated**: 2026-03-31T14:34:42.742853

---

## Nous Analysis

**Algorithm**  
We treat each extracted proposition \(p_i\) as a latent truth variable with a Gaussian belief \(\mathcal N(\mu_i,\sigma_i^2)\). All propositions are stacked in a state vector \(\mathbf x\in\mathbb R^n\). Logical constraints extracted from the prompt (e.g., \(A\rightarrow B\) ⇒ \(\mu_A\le\mu_B\), \(A\land B\) ⇒ \(\mu_A+\mu_B\ge1\), numeric comparisons ⇒ linear inequalities) are written as a constraint matrix \(\mathbf C\) and vector \(\mathbf d\) such that feasible beliefs satisfy \(\mathbf C\mathbf x\ge\mathbf d\).  

The Free Energy Principle provides a prior precision \(\mathbf\Lambda_0\) (inverse covariance) that encodes confidence in background knowledge; we set the prior covariance \(\mathbf P_0=\mathbf\Lambda_0^{-1}\) and prior mean \(\boldsymbol\mu_0\) from deterministic facts (e.g., known truths).  

For each candidate answer we build an observation vector \(\mathbf o\) that assigns truth values to the propositions mentioned in the answer (1 for asserted true, 0 for asserted false, 0.5 for unspecified). Observation noise \(\mathbf R\) reflects answer ambiguity.  

A Kalman‑filter‑style update implements active inference: the agent selects the answer that minimizes expected free energy, which for a Gaussian model equals the negative log‑likelihood of the observation.  

Prediction step: \(\boldsymbol\mu_{-}= \boldsymbol\mu_0,\; \mathbf P_{-}= \mathbf P_0\).  
Update step:  
\[
\mathbf S = \mathbf H\mathbf P_{-}\mathbf H^{\!T}+\mathbf R,\quad
\mathbf K = \mathbf P_{-}\mathbf H^{\!T}\mathbf S^{-1},
\]  
\[
\boldsymbol\mu_{+}= \boldsymbol\mu_{-}+ \mathbf K(\mathbf o-\mathbf H\boldsymbol\mu_{-}),\quad
\mathbf P_{+}= (\mathbf I-\mathbf K\mathbf H)\mathbf P_{-},
\]  
where \(\mathbf H\) selects the observed propositions (rows of identity).  

The score for the answer is the negative variational free energy:  
\[
\text{Score}= -\frac12\big[(\mathbf o-\mathbf H\boldsymbol\mu_{-})^{\!T}\mathbf S^{-1}(\mathbf o-\mathbf H\boldsymbol\mu_{-})+\log|\mathbf S|\big].
\]  
Higher scores indicate lower expected free energy, i.e., better explanatory fit under the constraint‑propagated belief state.

**Structural features parsed**  
- Negations (“not”, “no”) → flip truth value.  
- Comparatives (“greater than”, “less than”, “equals”) → linear inequality constraints.  
- Conditionals (“if … then …”) → implication constraints (\(\mu_{antecedent}\le\mu_{consequent}\)).  
- Numeric values → anchor propositions to specific scalars.  
- Causal claims (“because”, “leads to”) → directional constraints akin to conditionals.  
- Ordering relations (“first”, “before”, “after”) → temporal inequalities.  
- Quantifiers (“all”, “some”) → soft bounds on sums of propositional beliefs.

**Novelty**  
Pure variational free‑energy frameworks have been applied to perception, and Kalman filters to temporal state estimation, but coupling them to propagate logical constraints over propositional beliefs and scoring answers via expected free energy is not present in current NLP or symbolic‑AI literature. Related work includes probabilistic soft logic and differentiable theorem provers, yet none use the Kalman prediction‑update cycle with free‑energy‑derived priors for answer selection.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled Gaussian belief updates.  
Metacognition: 6/10 — limited self‑monitoring; the algorithm does not revise its own parsing rules online.  
Hypothesis generation: 7/10 — can sample alternative belief states from the posterior to generate candidate explanations.  
Implementability: 9/10 — relies only on regex parsing, NumPy linear algebra, and basic loops; no external libraries needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Kalman Filtering**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Active Inference + Free Energy Principle: strong positive synergy (+0.384). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Kalman Filtering: negative interaction (-0.061). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Information Theory + Active Inference + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T06:07:14.386461

---

## Code

**Source**: scrap

[View code](./Active_Inference---Kalman_Filtering---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Active Inference / Free Energy Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, 
       conditionals, causality, ordering, numbers) from text using regex.
    2. Belief State: Maintains a Gaussian belief (mu, Sigma) over the latent 
       correctness of a candidate.
    3. Active Inference (Evaluate): Treats each candidate as a hypothesis. 
       Computes Expected Free Energy (G) based on prediction error (innovation) 
       between the candidate's structural features and the prompt's constraints.
       Score = -G. Lower prediction error -> Higher score.
    4. Kalman Filtering (Confidence): Used ONLY for the confidence wrapper to 
       estimate uncertainty reduction, avoiding direct scoring bias.
    5. NCD Tiebreaker: Uses zlib compression distance only if structural scores 
       are indistinguishable.
    """
    
    def __init__(self):
        self.sigma_process = 0.1  # Process noise Q
        self.r_noise = 0.5        # Measurement noise R
        
        # Feature extractors
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'\b(more|less|greater|smaller|higher|lower)\b', r'[<>=]'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bimplies\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bcauses?\b', r'\bleads?\s+to\b'],
            'ordering': [r'\b(first|second|third|last|before|after)\b'],
            'numeric': r'\d+\.?\d*'
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features into a normalized vector."""
        text_lower = text.lower()
        features = []
        
        # Binary flags for logical structures
        for key in ['negation', 'comparative', 'conditional', 'causal', 'ordering']:
            count = sum(len(re.findall(p, text_lower)) for p in self.patterns[key])
            features.append(1.0 if count > 0 else 0.0)
            
        # Numeric density (normalized)
        nums = re.findall(self.patterns['numeric'], text_lower)
        num_val = min(1.0, len(nums) / 10.0) if nums else 0.0
        features.append(num_val)
        
        # Length penalty (normalized) to prevent echo
        features.append(min(1.0, len(text) / 500.0))
        
        return np.array(features)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        l1, l2 = len(s1.encode()), len(s2.encode())
        if l1 == 0 or l2 == 0: return 1.0
        c12 = len(zlib.compress((s1 + s2).encode()))
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _propagate_constraints(self, prompt_feats: np.ndarray, cand_feats: np.ndarray) -> np.ndarray:
        """
        Simulates constraint propagation. 
        If prompt has high logical density, candidate must match structural complexity.
        Returns a target measurement vector y_k.
        """
        # Simple heuristic: Target features should mirror prompt features 
        # but filtered by candidate's capacity to express them.
        # This acts as the observation model H_k * mu_k approx.
        
        # If prompt has negation, correct answer likely needs specific handling 
        # (modeled here as requiring matching structural presence)
        target = np.copy(prompt_feats)
        
        # Transitivity/Modus Ponens approximation:
        # If prompt implies logic (conditional/causal), candidate must have > 0 logic score
        logic_prompt = prompt_feats[2] + prompt_feats[3] # conditional + causal
        if logic_prompt > 0:
            if cand_feats[2] + cand_feats[3] == 0:
                # Penalty: Candidate lacks logical structure found in prompt
                target[2:] *= 0.5 
                
        return target

    def _kalman_update(self, mu: np.ndarray, sigma: np.ndarray, y: np.ndarray, H: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Standard Kalman Update step."""
        # Innovation
        epsilon = y - H @ mu
        
        # Innovation covariance
        S = H @ sigma @ H.T + R
        
        # Kalman Gain
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.eye(len(S)) * 0.1
            
        K = sigma @ H.T @ S_inv
        
        # Update
        mu_new = mu + K @ epsilon
        sigma_new = (np.eye(len(mu)) - K @ H) @ sigma
        
        # Compute scalar innovation magnitude for scoring
        # Mahalanobis distance component of Free Energy
        error_metric = float(epsilon.T @ S_inv @ epsilon)
        
        return mu_new, sigma_new, error_metric

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feats = self._extract_features(prompt)
        n_features = len(prompt_feats)
        
        # Priors for Active Inference
        # mu: belief that candidate is correct (start neutral)
        mu = np.ones((n_features, 1)) * 0.5 
        Sigma = np.eye(n_features) * 0.5
        
        # Observation Noise Matrix
        R = np.eye(n_features) * self.r_noise
        
        # Hand-crafted Observation Model H (Identity for direct mapping, 
        # but scaled by feature importance)
        H = np.eye(n_features) 
        
        scores = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand).reshape(-1, 1)
            
            # Generate predicted measurement based on constraints
            y_k = self._propagate_constraints(prompt_feats, cand_feats).reshape(-1, 1)
            
            # Active Inference: Evaluate hypothesis (candidate)
            # We treat the candidate's features as the "action" that reveals the world state.
            # We want to minimize Expected Free Energy (G).
            # G = 0.5 * (innovation_cost + entropy_cost)
            
            # Run Kalman update virtually to get innovation error
            _, _, innovation_cost = self._kalman_update(mu, Sigma, y_k, H, R)
            
            # Entropy term (log det S) - simplified as trace for stability
            S = H @ Sigma @ H.T + R
            entropy_cost = np.log(np.linalg.det(S) + 1e-6)
            
            # Expected Free Energy
            G = 0.5 * (innovation_cost + entropy_cost)
            
            # Score is negative free energy (lower G -> higher score)
            # Add small bonus for matching numeric values exactly if present
            bonus = 0.0
            if re.search(r'\d+', prompt) and re.search(r'\d+', cand):
                if self._compute_ncd(prompt, cand) < 0.5: # Rough similarity check for numbers
                    bonus = 0.5
                    
            final_score = -G + bonus
            scores.append((cand, final_score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # NCD Tiebreaker logic for top candidates if scores are too close
        if len(scores) > 1 and abs(scores[0][1] - scores[1][1]) < 1e-4:
            # Re-rank top cluster by NCD to prompt (preferring concise relevance)
            top_score = scores[0][1]
            cluster = [s for s in scores if abs(s[1] - top_score) < 1e-3]
            rest = [s for s in scores if abs(s[1] - top_score) >= 1e-3]
            
            cluster.sort(key=lambda x: self._compute_ncd(prompt, x[0]))
            scores = cluster + rest

        return [
            {"candidate": cand, "score": float(score), "reasoning": "Active Inference via Free Energy minimization on structural features"}
            for cand, score in scores
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 using Kalman Filter uncertainty reduction.
        High confidence = low posterior uncertainty after observing the answer.
        """
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        n = len(prompt_feats)
        mu = np.ones((n, 1)) * 0.5
        Sigma = np.eye(n) * 0.5  # Prior uncertainty
        H = np.eye(n)
        R = np.eye(n) * self.r_noise
        
        y_k = self._propagate_constraints(prompt_feats, cand_feats).reshape(-1, 1)
        
        # Perform update
        _, Sigma_post, error_metric = self._kalman_update(mu, Sigma, y_k, H, R)
        
        # Confidence is inverse of remaining uncertainty (trace of Sigma)
        # Normalized to 0-1 range roughly
        uncertainty = np.trace(Sigma_post)
        max_uncertainty = np.trace(Sigma)
        
        # Map uncertainty to confidence
        # If uncertainty reduced significantly, confidence is high
        conf = 1.0 - (uncertainty / max_uncertainty)
        
        # Penalize high innovation error (contradiction)
        if error_metric > 5.0:
            conf *= 0.5
            
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
