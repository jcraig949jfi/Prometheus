# Feedback Control + Multi-Armed Bandits + Maximum Entropy

**Fields**: Control Theory, Game Theory, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:36:11.855533
**Report Generated**: 2026-03-27T06:37:39.723708

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as an arm of a multi‑armed bandit. For every answer we first parse a fixed‑length structural feature vector **x** ∈ ℝⁿ (see §2). The belief about the arm’s latent correctness θᵢ is modeled as a Beta distribution Beta(αᵢ,βᵢ), which is the maximum‑entropy distribution on [0,1] given the constraints E[θᵢ]=αᵢ/(αᵢ+βᵢ) and Var[θᵢ]=αᵢβᵢ/[(αᵢ+βᵢ)²(αᵢ+βᵢ+1)]. The prior is Beta(1,1) (uniform), the maximum‑entropy choice with no information.

When an arm is selected, we compute a **reward** rᵢ = w·xᵢ, where w is a weight vector learned online by minimizing squared error between rᵢ and a provisional ground‑truth signal (e.g., agreement with a reference answer or internal consistency checks). The weight update is a simple stochastic gradient step: w ← w − η ∇‖rᵢ−y‖², using only numpy.

After observing rᵢ we update the Beta posterior: αᵢ←αᵢ+rᵢ, βᵢ←βᵢ+(1−rᵢ). This is the Bayesian update that preserves maximum entropy under the new constraint.

To decide which arm to evaluate next we use **Thompson sampling**: draw θ̃ᵢ∼Beta(αᵢ,βᵢ) for all i and pick i* = argmax θ̃ᵢ. This implements the explore‑exploit trade‑off of a bandit.

Finally, a **feedback‑control** loop regulates the exploration temperature τ that scales the Beta variance: τₖ₊₁ = τₖ + Kₚ·eₖ + Kᵢ·∑eⱼ + K𝒹·(eₖ−eₖ₋₁), where eₖ = r̂ₖ − rₖ is the prediction error between the expected reward (mean of Beta) and the observed reward. The PID gains (Kₚ,Kᵢ,K𝒹) are fixed scalars; τ directly influences the spread of the Beta distribution, making the sampler more exploratory when error is large and more exploitative when error shrinks.

**Structural features parsed**  
- Numeric values (integers, decimals) via regex `\d+(?:\.\d+)?`  
- Negations (`not`, `no`, `n’t`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if`, `then`, `unless`)  
- Causal claims (`because`, `therefore`, `leads to`)  
- Ordering relations (`before`, `after`, `first`, `last`)  
Each feature contributes one dimension to **x** (count or binary presence).

**Novelty**  
The trio has been used separately: maximum‑entropy priors in Bayesian bandits, UCB/Thompson sampling for exploration, and PID controllers for adaptive step‑size in optimization. Combining them to dynamically temper bandit exploration via a feedback loop on prediction error is not documented in the literature; thus the approach is novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty, but relies on hand‑crafted feature weights.  
Metacognition: 7/10 — PID loop provides self‑regulation of exploration, yet limited to scalar error.  
Hypothesis generation: 6/10 — Thompson sampling yields diverse hypotheses, but hypothesis space is confined to linear feature combinations.  
Implementability: 9/10 — only numpy and stdlib needed; all operations are explicit vector arithmetic and sampling.

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

- **Feedback Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Feedback Control + Maximum Entropy: strong positive synergy (+0.222). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Maximum Entropy + Multi-Armed Bandits: strong positive synergy (+0.159). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Chaos Theory + Feedback Control + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Epistemology + Feedback Control + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Network Science + Multi-Armed Bandits + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=67% cal=40% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T01:21:41.112047

---

## Code

**Source**: scrap

[View code](./Feedback_Control---Multi-Armed_Bandits---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Multi-Armed Bandits, Maximum Entropy priors, 
    and Feedback Control to evaluate candidate answers.
    
    Mechanism:
    1. Structural Parsing: Extracts features (negations, comparatives, numbers) 
       from candidates to form a feature vector x.
    2. Bandit Model: Each candidate is an arm with a Beta-distributed belief 
       about correctness (MaxEnt prior Beta(1,1)).
    3. Reward & Update: Rewards are linear combinations of structural features. 
       Weights are updated via online SGD. Beta parameters update based on rewards.
    4. Feedback Control: A PID controller adjusts the exploration temperature 
       based on prediction error, dynamically balancing explore/exploit.
    5. Selection: Thompson Sampling draws from the tempered Beta distribution 
       to rank candidates.
    """

    def __init__(self):
        # Hyperparameters
        self.learning_rate = 0.1
        self.kp = 0.5  # Proportional gain
        self.ki = 0.1  # Integral gain
        self.kd = 0.1  # Derivative gain
        
        # State
        self.w = None  # Weight vector for features
        self.feature_dim = 6  # Count, Negation, Comparative, Conditional, Causal, Order
        self.integral_error = 0.0
        self.prev_error = 0.0
        self.temperature = 1.0
        
        # Feature regexes
        self.patterns = [
            r'\d+(?:\.\d+)?',          # 0: Numeric
            r'\b(not|no|n\'t|never)\b', # 1: Negation
            r'\b(greater|less|more|fewer|>=|<=|>|<)\b', # 2: Comparative
            r'\b(if|then|unless|else)\b', # 3: Conditional
            r'\b(because|therefore|thus|hence)\b', # 4: Causal
            r'\b(before|after|first|last|next)\b'  # 5: Ordering
        ]

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural feature vector x from text."""
        text_lower = text.lower()
        features = np.zeros(self.feature_dim)
        
        # 0. Numeric density (normalized by length)
        nums = re.findall(self.patterns[0], text_lower)
        features[0] = len(nums) / (len(text.split()) + 1)
        
        # 1-5. Binary presence of logical markers
        for i in range(1, self.feature_dim):
            if re.search(self.patterns[i], text_lower):
                features[i] = 1.0
                
        return features

    def _compute_reward(self, x: np.ndarray, candidate: str, prompt: str) -> float:
        """
        Compute reward based on structural consistency.
        Uses learned weights for general structure, plus specific logical checks.
        """
        # Base reward from linear model
        if self.w is None:
            self.w = np.ones(self.feature_dim) / self.feature_dim
            
        r_linear = np.dot(self.w, x)
        
        # Specific logical boost: Numeric consistency check if both prompt and candidate have numbers
        prompt_nums = re.findall(r'\d+(?:\.\d+)?', prompt.lower())
        cand_nums = re.findall(r'\d+(?:\.\d+)?', candidate.lower())
        
        logic_bonus = 0.0
        if prompt_nums and cand_nums:
            try:
                # Simple heuristic: if candidate numbers are a subset or match prompt logic
                # This is a placeholder for complex constraint propagation
                p_val = float(prompt_nums[-1])
                c_val = float(cand_nums[-1])
                if abs(p_val - c_val) < 1e-6:
                    logic_bonus = 0.5
                elif "less" in candidate.lower() and c_val < p_val:
                    logic_bonus = 0.3
                elif "greater" in candidate.lower() and c_val > p_val:
                    logic_bonus = 0.3
            except ValueError:
                pass
                
        return r_linear + logic_bonus

    def _update_weights(self, x: np.ndarray, reward: float):
        """Online SGD update for weight vector w."""
        if self.w is None:
            self.w = np.ones(self.feature_dim) / self.feature_dim
            
        # Predicted reward
        pred = np.dot(self.w, x)
        error = reward - pred
        
        # Gradient step
        gradient = -2 * error * x
        self.w -= self.learning_rate * gradient
        
        return error

    def _pid_control(self, error: float):
        """Update exploration temperature using PID control on prediction error."""
        self.integral_error += error
        derivative = error - self.prev_error
        
        adjustment = (self.kp * error + 
                      self.ki * self.integral_error + 
                      self.kd * derivative)
        
        self.temperature = max(0.1, self.temperature + adjustment)
        self.prev_error = error

    def _sample_beta(self, alpha: float, beta: float) -> float:
        """Sample from Beta distribution using numpy."""
        # Ensure parameters are valid
        a = max(1e-6, alpha)
        b = max(1e-6, beta)
        return np.random.beta(a, b)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        n_arms = len(candidates)
        # Initialize Bandit State (Alpha, Beta) for each arm
        # Prior is Beta(1,1) -> MaxEnt
        alphas = np.ones(n_arms)
        betas = np.ones(n_arms)
        rewards = np.zeros(n_arms)
        features = []
        
        # 1. Parse features and compute initial rewards
        for i, cand in enumerate(candidates):
            x = self._extract_features(cand)
            features.append(x)
            r = self._compute_reward(x, cand, prompt)
            rewards[i] = r
            
            # Update weights based on this observation
            err = self._update_weights(x, r)
            
            # Update Beta parameters
            # Alpha increases with reward, Beta increases with (1-reward)
            alphas[i] += r
            betas[i] += (1.0 - r)
            
            # Feedback control on error
            self._pid_control(err)

        # 2. Thompson Sampling with Temperature
        sampled_values = []
        for i in range(n_arms):
            # Scale variance by temperature? 
            # Approximation: Scale the parameters towards mean by temperature
            # High temp -> closer to prior (1,1), Low temp -> closer to posterior
            # Simplified: Sample directly but scale the result's influence or sample multiple times?
            # Implementation: Sample from Beta(alpha/tau, beta/tau) effectively widens/narrows
            # But standard PID on variance suggests scaling the spread.
            # Let's sample and add noise scaled by temperature for exploration
            base_sample = self._sample_beta(alphas[i], betas[i])
            
            # Apply temperature to the sample (simulating variance scaling)
            # If tau > 1 (high error), we want more variance. 
            # We can achieve this by mixing with uniform or scaling params.
            # Approach: Effective Alpha = Alpha / tau, Effective Beta = Beta / tau
            eff_alpha = alphas[i] / self.temperature
            eff_beta = betas[i] / self.temperature
            final_sample = self._sample_beta(eff_alpha, eff_beta)
            
            sampled_values.append(final_sample)

        # 3. Rank by sampled value
        ranked_indices = np.argsort(sampled_values)[::-1]
        
        results = []
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": float(sampled_values[idx]),
                "reasoning": f"Bandit arm {idx} sampled {sampled_values[idx]:.4f} via Thompson Sampling with temp {self.temperature:.2f}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence based on structural feature density and consistency.
        Uses the learned weights to determine if the answer 'looks' correct structurally.
        """
        x = self._extract_features(answer)
        
        if self.w is None:
            self.w = np.ones(self.feature_dim) / self.feature_dim
            
        # Base score from linear model
        base_score = np.dot(self.w, x)
        
        # Bonus for numeric consistency if present
        prompt_nums = re.findall(r'\d+(?:\.\d+)?', prompt.lower())
        ans_nums = re.findall(r'\d+(?:\.\d+)?', answer.lower())
        
        if prompt_nums and ans_nums:
            try:
                if float(prompt_nums[-1]) == float(ans_nums[-1]):
                    base_score += 0.4
            except:
                pass
                
        # Clamp to [0, 1]
        return float(np.clip(base_score, 0.0, 1.0))
```

</details>
