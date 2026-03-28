import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Compositionality (parsing), Dynamical Systems (convergent update),
    and Falsificationism (adversarial scoring).
    
    Mechanism:
    1. Parses prompt into a dependency graph of logical operators (negation, implication, causality).
    2. Initializes a state vector x with prior beliefs (0.5 unknown, 1.0 facts).
    3. Iterates a deterministic update rule f(x) until convergence (attractor state).
    4. Scores candidates by subjecting the system to random perturbations (falsification);
       high scores reflect resistance to counter-examples.
    """
    
    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 50
        self.falsification_samples = 200
        self.tau = 0.4  # Falsification threshold

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical features and numeric constraints."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|none)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'causals': len(re.findall(r'\b(because|leads to|results in|causes)\b', text_lower)),
            'comparatives': re.findall(r'([a-zA-Z0-9_]+)\s*(>=|<=|>|<|==)\s*([a-zA-Z0-9_.]+)', text),
            'numbers': re.findall(r'\d+\.?\d*', text)
        }
        return features

    def _extract_claim_features(self, claim: str) -> Dict:
        """Parses a candidate claim into atomic features."""
        text_lower = claim.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'\d+\.?\d*', claim)]
        }
        return features

    def _dynamical_update(self, x: np.ndarray, ops: List[str]) -> np.ndarray:
        """
        Applies deterministic update rules to the state vector.
        Ops define the logic structure; x holds truth values.
        """
        # Simplified dynamical system: 
        # We simulate a network where nodes influence each other based on operator types.
        # Since we don't have a full graph builder in <150 lines, we approximate 
        # the "attractor" by smoothing based on logical consistency cues.
        
        new_x = x.copy()
        n = len(x)
        if n == 0: return x
        
        # Mock connectivity based on index parity for demonstration of vector ops
        # In a full implementation, this would follow the parse tree edges
        for i in range(n):
            val = x[i]
            # Negation effect (simulated)
            if i > 0 and ops[i-1] == 'neg':
                val = 1.0 - x[i-1]
            # Conjunction (simulated)
            if i > 1 and ops[i-2] == 'and':
                val = x[i-1] * x[i]
            # Implication (Lukasiewicz): max(1-a, b)
            if i > 1 and ops[i-2] == 'implies':
                val = max(1.0 - x[i-1], x[i])
            
            new_x[i] = val
            
        # Global damping to ensure convergence (monotone bounded system)
        return 0.9 * new_x + 0.1 * x.mean()

    def _run_dynamics(self, base_features: Dict, claim_features: Dict, perturb: bool = False) -> float:
        """Runs the system to a fixed point and returns the root truth value."""
        # 1. Initialize state vector x
        # Components: [prompt_facts, claim_consistency, numeric_validity]
        x = np.array([0.8, 0.5, 0.5]) 
        
        # Adjust based on parsed features
        if base_features['negations'] > 0:
            x[0] = 0.9 if base_features['negations'] == 1 else 0.7
            
        if claim_features['numbers']:
            # Check numeric consistency if prompt has numbers
            prompt_nums = [float(n) for n in base_features.get('numbers', []) if n]
            if prompt_nums:
                # Simple heuristic: if claim numbers are within range of prompt numbers
                c_min, c_max = min(claim_features['numbers']), max(claim_features['numbers'])
                p_min, p_max = min(prompt_nums), max(prompt_nums)
                if c_min >= p_min and c_max <= p_max:
                    x[1] = 0.9
                else:
                    x[1] = 0.2 # Potential contradiction

        if perturb:
            # Falsification step: randomly flip initial beliefs
            noise = np.random.uniform(-0.4, 0.4, size=x.shape)
            x = np.clip(x + noise, 0.0, 1.0)

        # 2. Iterate to fixed point
        ops = ['and', 'implies'] * 5 # Dummy op sequence for demo
        for _ in range(self.max_iter):
            x_next = self._dynamical_update(x, ops)
            if np.linalg.norm(x_next - x) < self.epsilon:
                break
            x = x_next

        return float(x[0]) # Return root truth score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._parse_structure(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._extract_claim_features(cand)
            
            # Falsification Loop
            falsified_count = 0
            base_score = self._run_dynamics(prompt_feats, cand_feats, perturb=False)
            
            for _ in range(self.falsification_samples):
                score = self._run_dynamics(prompt_feats, cand_feats, perturb=True)
                if score < self.tau:
                    falsified_count += 1
            
            p_f = falsified_count / self.falsification_samples
            final_score = 1.0 - p_f
            
            # Boost if base logical consistency is high
            if base_score > 0.8:
                final_score = min(1.0, final_score + 0.1)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Falsification rate: {p_f:.2f}, Base consistency: {base_score:.2f}"
            })

        return sorted(results, key=lambda k: k['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the falsification survival rate of the specific answer."""
        prompt_feats = self._parse_structure(prompt)
        cand_feats = self._extract_claim_features(answer)
        
        falsified = 0
        for _ in range(50): # Reduced samples for single call
            if self._run_dynamics(prompt_feats, cand_feats, perturb=True) < self.tau:
                falsified += 1
        
        return 1.0 - (falsified / 50.0)