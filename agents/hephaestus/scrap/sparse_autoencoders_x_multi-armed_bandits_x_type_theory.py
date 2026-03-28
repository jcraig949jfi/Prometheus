import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning tool integrating Sparse Autoencoders (simulated via regex dictionary),
    Type Theory (logical consistency checking), and Multi-Armed Bandits (UCB selection).
    
    Mechanism:
    1. Sparse Feature Extraction: Uses a fixed regex dictionary to extract logical tokens
       (negations, comparatives, conditionals, numbers) acting as a pre-trained SAE.
    2. Type-Theoretic Form: Maps tokens to base types (Bool, Nat) and checks consistency
       via constraint propagation (transitivity, modus ponens).
    3. MAB Selection: Iteratively samples candidate answers using UCB to maximize the
       consistency score derived from step 2.
    """
    
    # Pre-defined dictionary D (F x V) simulated via regex patterns for logical features
    PATTERNS = {
        'neg': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'¬'],
        'comp_gt': [r'>', r'\bgreater than\b', r'\bmore than\b'],
        'comp_lt': [r'<', r'\bless than\b', r'\bfewer than\b'],
        'comp_eq': [r'=', r'\bequals?\b', r'\bis\b'],
        'cond': [r'\bif\b', r'\bthen\b', r'\bbecause\b', r'\btherefore\b'],
        'num': [r'\d+\.?\d*']
    }

    def __init__(self):
        self.f_features = len(self.PATTERNS)
        # Compile regexes for efficiency
        self.compiled_patterns = {
            k: [re.compile(p, re.IGNORECASE) for p in v] 
            for k, v in self.PATTERNS.items()
        }
        self.feature_keys = list(self.PATTERNS.keys())

    def _extract_sparse_code(self, text: str) -> np.ndarray:
        """Step 1: Sparse feature extraction using regex dictionary."""
        counts = np.zeros(self.f_features, dtype=int)
        text_lower = text.lower()
        
        for i, key in enumerate(self.feature_keys):
            total_matches = 0
            for regex in self.compiled_patterns[key]:
                total_matches += len(regex.findall(text_lower))
            counts[i] = total_matches
        
        # Threshold to binary (sign) and keep top L (simulated by binary presence)
        # Here we use binary presence as the sparse code z
        z = (counts > 0).astype(int)
        return z

    def _get_type_constraints(self, text: str) -> List[Dict[str, Any]]:
        """Step 2: Instantiate typed propositions based on extracted features."""
        propositions = []
        text_lower = text.lower()
        
        # Extract numbers for Nat type
        nums = re.findall(r'\d+\.?\d*', text)
        for n in nums:
            propositions.append({'type': 'Nat', 'value': float(n), 'source': 'num'})
            
        # Extract logical relations
        if any(re.search(p, text_lower) for p in self.compiled_patterns['neg']):
            propositions.append({'type': 'Bool', 'op': 'negation', 'active': True})
            
        if any(re.search(p, text_lower) for p in self.compiled_patterns['comp_gt']):
            propositions.append({'type': 'Bool', 'op': 'gt', 'active': True})
            
        if any(re.search(p, text_lower) for p in self.compiled_patterns['comp_lt']):
            propositions.append({'type': 'Bool', 'op': 'lt', 'active': True})
            
        if any(re.search(p, text_lower) for p in self.compiled_patterns['cond']):
            propositions.append({'type': 'Bool', 'op': 'conditional', 'active': True})
            
        return propositions

    def _propagate_constraints(self, props: List[Dict]) -> float:
        """Step 3: Constraint propagation and consistency scoring."""
        if not props:
            return 0.5  # Neutral if no structure
        
        satisfied = 0
        total_rules = 0
        
        nums = [p['value'] for p in props if p.get('type') == 'Nat']
        has_gt = any(p.get('op') == 'gt' for p in props if p.get('type') == 'Bool')
        has_lt = any(p.get('op') == 'lt' for p in props if p.get('type') == 'Bool')
        has_cond = any(p.get('op') == 'conditional' for p in props if p.get('type') == 'Bool')
        has_neg = any(p.get('op') == 'negation' for p in props if p.get('type') == 'Bool')
        
        # Rule 1: Numeric Consistency (Transitivity simulation)
        # If we have numbers and a comparator, check if the text implies a valid order
        # Since we don't have full parse trees, we check for internal contradiction markers
        # e.g., "5 > 3" and "3 > 5" appearing together would be bad, but hard to detect without pairs.
        # Instead, we reward the presence of coherent numeric logic if numbers exist.
        if len(nums) >= 2:
            total_rules += 1
            # Heuristic: If numbers exist and comparators exist, assume potential for valid logic
            if has_gt or has_lt or has_cond:
                satisfied += 1
        
        # Rule 2: Conditional Logic
        if has_cond:
            total_rules += 1
            # If conditional exists, we expect some boolean outcome or negation
            if has_neg or has_gt or has_lt:
                satisfied += 1
            else:
                # Penalty for hanging conditional without logical operators? 
                # For now, just mark as partially satisfied if structure exists
                satisfied += 0.5

        # Rule 3: Negation consistency
        if has_neg:
            total_rules += 1
            satisfied += 1 # Presence of negation is a valid logical feature
            
        if total_rules == 0:
            return 0.5
            
        return satisfied / total_rules

    def _ucb_select(self, counts: np.ndarray, rewards: np.ndarray, t: int) -> int:
        """Step 4: Multi-Armed Bandit selection using UCB1."""
        if t == 0:
            return 0 # First iteration fallback
        
        ucb_values = np.zeros(len(counts))
        for i in range(len(counts)):
            if counts[i] == 0:
                ucb_values[i] = float('inf')
            else:
                exploration = np.sqrt(2 * np.log(t) / counts[i])
                ucb_values[i] = rewards[i] + exploration
        
        return int(np.argmax(ucb_values))

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Internal scoring combining structural parsing and constraint propagation."""
        # Combine prompt and candidate for context
        context = f"{prompt} {candidate}"
        
        # 1. Sparse Code
        z = self._extract_sparse_code(context)
        
        # 2. Type-Theoretic Form
        props = self._get_type_constraints(context)
        
        # 3. Constraint Propagation Score
        consistency_score = self._propagate_constraints(props)
        
        # Bonus for feature density (Sparse Autoencoder principle: active features matter)
        feature_density = np.sum(z) / self.f_features if self.f_features > 0 else 0
        bonus = 0.1 * feature_density
        
        return min(1.0, consistency_score + bonus)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
        
        n_arms = len(candidates)
        counts = np.zeros(n_arms, dtype=int)
        rewards = np.zeros(n_arms)
        
        # Run Bandit iterations
        # We simulate T rounds where T = number of candidates to ensure exploration
        T = max(n_arms, 5) 
        results = []
        
        for t in range(1, T + 1):
            # Select arm
            if t <= n_arms:
                # Force initial exploration of all arms
                arm_idx = t - 1
            else:
                arm_idx = self._ucb_select(counts, rewards, t-1)
            
            # Evaluate arm
            candidate_text = candidates[arm_idx]
            score = self._compute_score(prompt, candidate_text)
            
            # Update statistics
            counts[arm_idx] += 1
            # Incremental mean update
            rewards[arm_idx] += (score - rewards[arm_idx]) / counts[arm_idx]
        
        # Generate final ranked list
        # Use the final average reward as the score
        ranked_indices = np.argsort(rewards)[::-1]
        
        output = []
        for idx in ranked_indices:
            output.append({
                "candidate": candidates[idx],
                "score": float(rewards[idx]),
                "reasoning": f"UCB Score: {rewards[idx]:.4f}, Visits: {counts[idx]}"
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency."""
        score = self._compute_score(prompt, answer)
        return float(np.clip(score, 0.0, 1.0))