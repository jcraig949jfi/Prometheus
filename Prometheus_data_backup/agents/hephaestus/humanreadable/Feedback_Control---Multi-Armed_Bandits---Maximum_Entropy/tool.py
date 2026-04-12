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