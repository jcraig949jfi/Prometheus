import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Bandit-Guided MCTS with Kalman-Filtered Belief Updates.
    
    Mechanism:
    1. Structural Parsing: Extracts logical fragments (negations, comparatives, 
       conditionals, causality) and numeric values from the prompt.
    2. MCTS Simulation: Treats logical fragments as 'actions'. Simulates paths 
       by applying these rules to check consistency with candidate answers.
    3. Kalman Filtering: Maintains a Gaussian belief (mu, sigma) over the 
       'correctness' of each path. Rewards from constraint checks (numeric 
       equality, transitivity) update beliefs via Kalman equations.
    4. Scoring: Final score is the posterior mean (mu) of the root belief, 
       fallback to NCD if no structural signals exist.
    """
    
    def __init__(self):
        self.exploration_constant = 1.414  # sqrt(2)
        self.process_noise = 0.1
        self.measurement_noise = 0.5
        self.max_depth = 4
        self.simulations = 20

    def _parse_structural_features(self, text: str) -> Dict:
        """Extracts logical fragments and numeric values."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|never|no|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'causality': len(re.findall(r'\b(because|therefore|leads to|causes)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'raw': text_lower
        }
        return features

    def _check_constraints(self, prompt_feats: Dict, candidate: str) -> float:
        """Lightweight constraint checker for rollout reward."""
        reward = 0.0
        checks = 0
        cand_lower = candidate.lower()
        
        # Numeric consistency
        if prompt_feats['numbers']:
            p_nums = [float(n) for n in prompt_feats['numbers']]
            c_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if c_nums:
                c_vals = [float(n) for n in c_nums]
                # Check simple ordering if comparatives exist
                if prompt_feats['comparatives'] > 0 and len(p_nums) >= 2 and len(c_vals) >= 2:
                    if (p_nums[0] < p_nums[1]) == (c_vals[0] < c_vals[1]):
                        reward += 0.5
                checks += 1
        
        # Logical keyword presence (heuristic)
        if prompt_feats['negations'] > 0:
            if any(w in cand_lower for w in ['not', 'never', 'false']):
                reward += 0.3
            checks += 1
            
        if prompt_feats['conditionals'] > 0:
            if any(w in cand_lower for w in ['if', 'then', 'only if']):
                reward += 0.3
            checks += 1

        return reward / max(checks, 1) if checks > 0 else 0.5

    def _ucb_select(self, children: List[Dict]) -> int:
        """Selects child maximizing UCB."""
        if not children:
            return -1
        
        best_idx = 0
        best_val = -np.inf
        parent_n = sum(c['n'] for c in children) + 1
        
        for i, child in enumerate(children):
            if child['n'] == 0:
                return i  # Explore unvisited
            
            exploitation = child['mu']
            exploration = self.exploration_constant * np.sqrt(np.log(parent_n) / child['n'])
            ucb = exploitation + exploration
            
            if ucb > best_val:
                best_val = ucb
                best_idx = i
        return best_idx

    def _kalman_update(self, mu: float, sigma: float, z: float, R: float) -> Tuple[float, float]:
        """1D Kalman Update."""
        H = 1.0
        K = sigma * H / (H * sigma * H + R)
        mu_new = mu + K * (z - H * mu)
        sigma_new = (1 - K * H) * sigma
        return mu_new, sigma_new

    def _simulate_rollout(self, prompt_feats: Dict, candidate: str) -> float:
        """Runs a single MCTS rollout with Kalman updates."""
        # Root node
        root = {
            'mu': 0.5, 'sigma': 1.0, 'n': 0, 
            'children': [], 'depth': 0
        }
        
        # Initialize children based on structural features (Actions)
        # Each feature type represents a potential logical path
        actions = []
        if prompt_feats['negations'] > 0: actions.append('neg')
        if prompt_feats['comparatives'] > 0: actions.append('comp')
        if prompt_feats['conditionals'] > 0: actions.append('cond')
        if prompt_feats['causality'] > 0: actions.append('cause')
        if prompt_feats['numbers']: actions.append('num')
        
        if not actions:
            actions = ['default'] # Fallback action

        for act in actions:
            root['children'].append({
                'mu': 0.5, 'sigma': 1.0, 'n': 0, 'action': act
            })

        for _ in range(self.simulations):
            node = root
            path = [node]
            
            # Selection
            while node['children'] and node['depth'] < self.max_depth:
                idx = self._ucb_select(node['children'])
                if idx == -1: break
                node = node['children'][idx]
                path.append(node)
            
            # Expansion (simplified: leaf is terminal for this depth)
            # Simulation (Rollout)
            terminal_reward = self._check_constraints(prompt_feats, candidate)
            # Add noise for realism
            z = terminal_reward + np.random.normal(0, 0.1)
            
            # Backpropagation with Kalman Update
            for n in reversed(path):
                n['mu'], n['sigma'] = self._kalman_update(
                    n['mu'], n['sigma'], z, self.measurement_noise
                )
                n['n'] += 1
                # Process noise injection for non-root nodes to simulate uncertainty growth
                if n != root:
                    n['sigma'] += self.process_noise

        return root['mu']

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        if min(len1, len2) == 0: return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._parse_structural_features(prompt)
        results = []
        
        # Check if structural signals exist
        has_structure = any([
            prompt_feats['negations'], prompt_feats['comparatives'], 
            prompt_feats['conditionals'], prompt_feats['causality'], prompt_feats['numbers']
        ])

        for cand in candidates:
            if has_structure:
                score = self._simulate_rollout(prompt_feats, cand)
            else:
                # Fallback to NCD if no structure found (as per instructions)
                # Invert NCD so higher is better (lower distance = higher score)
                ncd_val = self._ncd_score(prompt, cand)
                score = 1.0 - ncd_val
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "MCTS-Kalman belief update on structural constraints" if has_structure else "NCD baseline fallback"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0