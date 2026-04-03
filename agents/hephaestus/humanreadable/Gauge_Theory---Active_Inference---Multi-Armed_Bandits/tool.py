from dataclasses import field
from typing import Dict

"""
Gauge-Bandit Active Inference Scorer (GBAIS)

Combines gauge theory (invariant feature representation), active inference 
(expected free energy minimization), and multi-armed bandits (UCB exploration).

Architecture:
1. Parse structural features (negations, comparatives, conditionals, etc.)
2. Apply gauge transformation C*f -> z (learned invariant representation)
3. Maintain Beta beliefs over arm correctness
4. Select arms via EFE = ambiguity + risk - lambda*UCB
5. Update beliefs and gauge field based on structural rewards
"""

import re
import numpy as np
from typing import List, Dict
from forge_primitives import (
    bayesian_update, entropy, confidence_from_agreement,
    information_sufficiency, solve_constraints, modus_ponens
)


class ReasoningTool:
    def __init__(self):
        self.feature_dim = 10  # Number of structural features
        self.latent_dim = 5    # Latent gauge space dimension
        # Initialize gauge connection matrix
        self.C = np.random.randn(self.latent_dim, self.feature_dim) * 0.1
        self.w = np.ones(self.latent_dim) / self.latent_dim  # Prediction weights
        self.eta = 0.01  # Learning rate for gauge field
        self.lambda_ucb = 0.5  # Exploration parameter
        
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features via regex parsing"""
        f = np.zeros(self.feature_dim)
        text_lower = text.lower()
        
        # 0: Negations
        f[0] = len(re.findall(r'\b(not|no|never|n\'t|neither|nor)\b', text_lower))
        # 1: Comparatives
        f[1] = len(re.findall(r'\b(more|less|greater|fewer|higher|lower|er than)\b', text_lower))
        # 2: Conditionals
        f[2] = len(re.findall(r'\b(if|unless|when|whenever|provided)\b', text_lower))
        # 3: Numeric values
        f[3] = len(re.findall(r'\b\d+\.?\d*\b', text_lower))
        # 4: Causal cues
        f[4] = len(re.findall(r'\b(because|since|leads to|results in|causes)\b', text_lower))
        # 5: Ordering
        f[5] = len(re.findall(r'\b(before|after|first|last|then|next)\b', text_lower))
        # 6: Quantifiers
        f[6] = len(re.findall(r'\b(all|some|none|every|any|each)\b', text_lower))
        # 7: Modality
        f[7] = len(re.findall(r'\b(must|should|could|might|may|can)\b', text_lower))
        # 8: Conjunctions
        f[8] = len(re.findall(r'\b(and|or|but|yet|however)\b', text_lower))
        # 9: Text length (normalized)
        f[9] = min(len(text) / 100.0, 10.0)
        
        return f + 0.01  # Avoid zeros
    
    def _gauge_transform(self, f: np.ndarray) -> np.ndarray:
        """Apply gauge transformation: z = C * f"""
        return self.C @ f
    
    def _structural_reward(self, prompt: str, candidate: str) -> float:
        """Compute reward via structural matching and primitive composition"""
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Extract numbers for numeric comparisons
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        reward = 0.0
        
        # Numeric matching
        if p_nums and c_nums:
            if any(abs(pn - cn) < 0.01 for pn in p_nums for cn in c_nums):
                reward += 0.3
        
        # Negation consistency via modus_ponens
        p_neg = bool(re.search(r'\b(not|no|never)\b', p_lower))
        c_neg = bool(re.search(r'\b(not|no|never)\b', c_lower))
        if 'true' in p_lower or 'false' in p_lower:
            # Use logical inference
            if p_neg == c_neg:
                reward += 0.2
        
        # Comparative matching
        if re.search(r'\b(more|greater|higher)\b', p_lower):
            if re.search(r'\b(more|greater|higher|yes|increase)\b', c_lower):
                reward += 0.25
        
        # Feature alignment (gauge invariance)
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        p_z = self._gauge_transform(p_feat)
        c_z = self._gauge_transform(c_feat)
        
        # Cosine similarity in gauge space
        cos_sim = np.dot(p_z, c_z) / (np.linalg.norm(p_z) * np.linalg.norm(c_z) + 1e-9)
        reward += 0.25 * max(0, cos_sim)
        
        return min(reward, 1.0)
    
    def _compute_efe(self, alpha: float, beta: float, n_pulls: int, N: int, z: np.ndarray) -> float:
        """Compute Expected Free Energy = ambiguity + risk - lambda*UCB"""
        # Ambiguity: entropy of predictive distribution
        mean = alpha / (alpha + beta)
        var = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))
        ambiguity = entropy([mean, 1 - mean])
        
        # Risk: KL from prior Beta(2,1) favoring correctness
        prior_alpha, prior_beta = 2.0, 1.0
        risk = (alpha - prior_alpha) * (np.log(alpha) - np.log(prior_alpha)) if alpha > 0 else 0
        risk += (beta - prior_beta) * (np.log(beta) - np.log(prior_beta)) if beta > 0 else 0
        risk = abs(risk)  # Simplified KL
        
        # UCB
        if n_pulls == 0:
            ucb = float('inf')
        else:
            ucb = mean + np.sqrt(2 * np.log(N + 1) / (n_pulls + 1))
        
        return ambiguity + 0.1 * risk - self.lambda_ucb * ucb
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect question properties that warrant low confidence"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did.*fail|when did.*stop)\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.3
        
        # Information sufficiency check
        unknowns = len(re.findall(r'\b(unknown|unclear|ambiguous|\?)\b', p_lower))
        if information_sufficiency(unknowns, 1):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Bandit-based active inference scoring"""
        K = len(candidates)
        # Initialize Beta beliefs
        alphas = np.ones(K)
        betas = np.ones(K)
        n_pulls = np.zeros(K)
        
        # Extract prompt features
        prompt_feat = self._extract_features(prompt)
        
        # Active inference loop
        budget = min(20, K * 3)
        N = 0
        
        for _ in range(budget):
            # Compute EFE for each arm
            efes = []
            for i in range(K):
                cand_feat = self._extract_features(candidates[i])
                z = self._gauge_transform(cand_feat)
                efe = self._compute_efe(alphas[i], betas[i], n_pulls[i], N, z)
                efes.append(efe)
            
            # Select arm with minimum EFE
            arm = int(np.argmin(efes))
            
            # Observe reward
            reward = self._structural_reward(prompt, candidates[arm])
            
            # Update Beta belief (Bayesian update)
            alphas[arm] += reward
            betas[arm] += (1 - reward)
            n_pulls[arm] += 1
            N += 1
            
            # Update gauge field (gradient step)
            cand_feat = self._extract_features(candidates[arm])
            z = self._gauge_transform(cand_feat)
            y_pred = 1 / (1 + np.exp(-np.dot(self.w, z)))
            error = reward - y_pred
            self.C -= self.eta * error * np.outer(self.w, cand_feat)
        
        # Compute final scores
        scores = alphas / (alphas + betas)
        
        # Agreement-based confidence calibration
        meta_conf = confidence_from_agreement(scores.tolist())
        scores = scores * meta_conf
        
        # Rank results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                'candidate': cand,
                'score': float(scores[i]),
                'reasoning': f'Beta({alphas[i]:.1f},{betas[i]:.1f}) EFE-bandit pulls={n_pulls[i]:.0f}'
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence based on question properties"""
        # Check meta-level question properties first
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.5:
            return meta_cap
        
        # Run single-candidate evaluation
        result = self.evaluate(prompt, [answer])
        base_score = result[0]['score']
        
        # Cap by meta-confidence
        final_conf = min(base_score, meta_cap)
        
        # Never return > 0.9 unless structural evidence is very strong
        if final_conf > 0.9:
            reward = self._structural_reward(prompt, answer)
            if reward < 0.8:
                final_conf = 0.85
        
        return float(final_conf)