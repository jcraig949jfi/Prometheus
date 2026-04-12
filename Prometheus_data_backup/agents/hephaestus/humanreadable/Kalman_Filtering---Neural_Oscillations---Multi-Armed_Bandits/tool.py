import numpy as np

class ReasoningTool:
    """
    Kalman Filter x Neural Oscillations x Multi-Armed Bandit reasoning tool.
    
    Treats each candidate as a bandit arm with evolving belief state tracked by a Kalman filter.
    Neural oscillation bands (theta/alpha/gamma) modulate observation noise. Structural features
    are extracted and drive state updates. UCB selection picks the best candidate.
    
    Dynamics tracking: monitors state trajectory stability and convergence.
    Meta-confidence: detects ambiguity, presuppositions, unanswerable questions.
    """
    
    def __init__(self):
        self.feature_dim = 8  # Number of structural features
        self.q = 0.01  # Process noise
        self.sigma0 = 1.0  # Base measurement noise
        
    def _extract_features(self, prompt, candidate):
        """Extract binary structural feature vector from prompt+candidate."""
        text = (prompt + " " + candidate).lower()
        features = np.zeros(self.feature_dim, dtype=float)
        
        # Feature 0: Numeric values/units
        features[0] = 1.0 if re.search(r'\d+\.?\d*\s*(km|m|kg|miles|years|%)?', text) else 0.0
        
        # Feature 1: Comparatives
        features[1] = 1.0 if re.search(r'(greater|less|more|fewer|higher|lower|than|>=?|<=?)', text) else 0.0
        
        # Feature 2: Negations
        features[2] = 1.0 if re.search(r'\b(not|no|never|none|neither)\b', text) else 0.0
        
        # Feature 3: Conditionals
        features[3] = 1.0 if re.search(r'\b(if|then|unless|provided|when|whenever)\b', text) else 0.0
        
        # Feature 4: Causal cues
        features[4] = 1.0 if re.search(r'\b(because|since|thus|therefore|leads to|results in|causes)\b', text) else 0.0
        
        # Feature 5: Temporal/ordering
        features[5] = 1.0 if re.search(r'\b(first|second|before|after|then|next|subsequently|finally)\b', text) else 0.0
        
        # Feature 6: Quantifiers
        features[6] = 1.0 if re.search(r'\b(all|some|most|many|few|none|every|each|any)\b', text) else 0.0
        
        # Feature 7: Propositional atoms (named entities - capitalized words)
        features[7] = 1.0 if re.search(r'\b[A-Z][a-z]+\b', prompt + " " + candidate) else 0.0
        
        return features
    
    def _compute_oscillation_weights(self, text):
        """Extract oscillatory band weights via FFT on token stream."""
        tokens = re.findall(r'\w+', text.lower())
        if len(tokens) < 4:
            return 1.0, 1.0, 1.0
        
        # Convert tokens to numeric signal (ASCII sum per token)
        signal = np.array([sum(ord(c) for c in tok) for tok in tokens], dtype=float)
        signal = signal - np.mean(signal)
        
        # FFT and power spectrum
        fft = np.fft.fft(signal)
        power = np.abs(fft[:len(fft)//2])**2
        
        if len(power) < 3:
            return 1.0, 1.0, 1.0
        
        # Divide spectrum into theta/alpha/gamma bands
        n_bands = len(power) // 3
        theta_power = np.sum(power[:n_bands]) if n_bands > 0 else 1.0
        alpha_power = np.sum(power[n_bands:2*n_bands]) if n_bands > 0 else 1.0
        gamma_power = np.sum(power[2*n_bands:]) if len(power) > 2*n_bands else 1.0
        
        # Normalize to weights (higher power = lower noise = higher weight)
        total = theta_power + alpha_power + gamma_power + 1e-6
        w_theta = max(theta_power / total, 0.1)
        w_alpha = max(alpha_power / total, 0.1)
        w_gamma = max(gamma_power / total, 0.1)
        
        return w_theta, w_alpha, w_gamma
    
    def _kalman_update(self, mu, Sigma, H, z, R, Q):
        """Single Kalman filter update step."""
        # Prediction
        mu_pred = mu
        Sigma_pred = Sigma + Q
        
        # Update
        S = H @ Sigma_pred @ H.T + R
        K = Sigma_pred @ H.T / (S + 1e-6)
        innovation = z - H @ mu_pred
        mu_new = mu_pred + K * innovation
        Sigma_new = (np.eye(len(mu)) - np.outer(K, H)) @ Sigma_pred
        
        return mu_new, Sigma_new
    
    def _compute_observation(self, prompt, candidate):
        """Compute observation signal from structural match and numeric evaluation."""
        z = 0.0
        
        # Numeric comparison parsing
        nums_prompt = re.findall(r'\d+\.?\d*', prompt)
        nums_candidate = re.findall(r'\d+\.?\d*', candidate)
        
        if nums_prompt and nums_candidate:
            try:
                p_val = float(nums_prompt[0])
                c_val = float(nums_candidate[0])
                # Reward numeric consistency
                z += 0.5 if abs(p_val - c_val) / (abs(p_val) + 1) < 0.1 else -0.2
            except:
                pass
        
        # Negation consistency
        neg_prompt = len(re.findall(r'\b(not|no|never)\b', prompt.lower()))
        neg_cand = len(re.findall(r'\b(not|no|never)\b', candidate.lower()))
        z += 0.3 if (neg_prompt > 0) == (neg_cand > 0) else -0.3
        
        # Comparative direction match
        if re.search(r'\b(greater|more|higher)\b', prompt.lower()):
            if re.search(r'\b(greater|more|higher|increase)\b', candidate.lower()):
                z += 0.4
        
        # NCD component (small weight)
        ncd = self._ncd(prompt, candidate)
        z += 0.15 * (1.0 - ncd)
        
        return z
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _track_dynamics(self, trajectory):
        """Analyze trajectory stability and convergence (Frame C dynamics)."""
        if len(trajectory) < 2:
            return 0.5
        
        traj = np.array(trajectory)
        # Convergence: decreasing variance over time
        early_var = np.var(traj[:len(traj)//2]) if len(traj) > 2 else 1.0
        late_var = np.var(traj[len(traj)//2:]) if len(traj) > 2 else 1.0
        
        convergence_score = max(0, 1.0 - late_var / (early_var + 1e-6))
        
        # Stability: smooth trajectory (low derivative variance)
        if len(traj) > 2:
            diffs = np.diff(traj)
            stability_score = 1.0 / (1.0 + np.var(diffs))
        else:
            stability_score = 0.5
        
        return 0.6 * convergence_score + 0.4 * stability_score
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity, presuppositions, unanswerable questions (Tier B)."""
        p = prompt.lower()
        
        # Presupposition triggers
        if re.search(r'\b(have you stopped|did you stop|why did.*fail|when did.*end)\b', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity with question
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p):
            return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(because|since|based on)\b', p):
            return 0.3
        
        # Unanswerability: question about missing info
        if re.search(r'\b(what|when|where|who|how much|how many)\b', p) and len(p.split()) < 10:
            return 0.35
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt, candidates):
        """Evaluate candidates via Kalman-bandit framework."""
        N = len(candidates)
        if N == 0:
            return []
        
        # Extract oscillation weights
        w_theta, w_alpha, w_gamma = self._compute_oscillation_weights(prompt)
        
        # Initialize Kalman states for each arm
        arms = []
        for cand in candidates:
            mu = np.zeros(self.feature_dim)
            Sigma = np.eye(self.feature_dim)
            trajectory = []
            arms.append({'mu': mu, 'Sigma': Sigma, 'candidate': cand, 'trajectory': trajectory})
        
        # Process timesteps (tokens) - simulate temporal evolution
        tokens = re.findall(r'\w+', prompt)
        timesteps = min(len(tokens), 10)  # Limit for efficiency
        
        Q = self.q * np.eye(self.feature_dim)
        
        for t in range(max(timesteps, 1)):
            for arm in arms:
                # Extract features
                x = self._extract_features(prompt, arm['candidate'])
                H = x.reshape(1, -1)
                
                # Oscillation-modulated noise
                R = self.sigma0**2 * np.array([[1.0 / (w_theta + w_alpha + w_gamma)]])
                
                # Observation
                z = self._compute_observation(prompt, arm['candidate'])
                
                # Kalman update
                arm['mu'], arm['Sigma'] = self._kalman_update(arm['mu'], arm['Sigma'], H, z, R, Q)
                arm['trajectory'].append(arm['mu'][0])
        
        # UCB selection and scoring
        beta = np.sqrt(2 * np.log(N + 1))
        results = []
        
        for arm in arms:
            ucb = arm['mu'][0] + beta * np.sqrt(arm['Sigma'][0, 0])
            dynamics_score = self._track_dynamics(arm['trajectory'])
            final_score = 0.5 * arm['mu'][0] + 0.3 * dynamics_score + 0.2 * ucb
            
            reasoning = f"Kalman posterior={arm['mu'][0]:.3f}, UCB={ucb:.3f}, dynamics={dynamics_score:.3f}"
            results.append({
                'candidate': arm['candidate'],
                'score': float(final_score),
                'reasoning': reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Compute confidence based on question properties and answer quality."""
        # Meta-confidence check (Tier B epistemic honesty)
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.35:
            return meta_conf
        
        # Structural parsing confidence
        features = self._extract_features(prompt, answer)
        structural_match = np.sum(features) / self.feature_dim
        
        # Observation quality
        obs = self._compute_observation(prompt, answer)
        obs_conf = 1.0 / (1.0 + np.exp(-2 * obs))  # Sigmoid
        
        # Combine with meta-confidence cap
        base_conf = 0.5 * structural_match + 0.5 * obs_conf
        capped_conf = min(base_conf * meta_conf, 0.85)  # Never exceed 0.85 unless definitive
        
        return float(np.clip(capped_conf, 0.0, 1.0))