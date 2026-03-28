import numpy as np
import re
import math

class ReasoningTool:
    """
    A differentiable gene-regulatory reasoning engine.
    Maps logical propositions to nodes, constraints to weights/biases,
    and uses gradient descent on variational free energy to score coherence.
    """
    
    def __init__(self):
        self.tau = 0.1  # Entropy weight for epistemic foraging
        self.steps = 50
        self.lr = 0.1   # Learning rate

    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _parse_structure(self, text):
        """Extracts logical features: negations, conditionals, comparatives, numbers."""
        features = {
            'negations': [], 'conditionals': [], 'comparatives': [], 
            'numbers': [], 'tokens': []
        }
        lower = text.lower()
        
        # Tokenize simple words
        features['tokens'] = re.findall(r'\b\w+\b', lower)
        
        # Negations
        if re.search(r'\b(not|no|never|neither|nobody|nothing)\b', lower):
            features['negations'] = [m.start() for m in re.finditer(r'\b(not|no|never|neither|nobody|nothing)\b', lower)]
            
        # Conditionals (if A then B, A causes B)
        if re.search(r'\b(if|then|causes|implies|therefore|so)\b', lower):
            features['conditionals'] = [m.start() for m in re.finditer(r'\b(if|then|causes|implies|therefore|so)\b', lower)]
            
        # Comparatives
        if re.search(r'(>|<|=|greater|less|equal|before|after)', lower):
            features['comparatives'] = [m.start() for m in re.finditer(r'(>|<|=|greater|less|equal|before|after)', lower)]
            
        # Numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        
        return features

    def _build_grn(self, prompt, candidate):
        """Constructs the GRN matrix W and bias b from parsed features."""
        # Create a synthetic node set: [Prompt_Context, Candidate_Truth, Logic_Check, Number_Check]
        # Size 4 for minimal viable graph representing the interaction
        n = 4
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        # Node 0: Prompt Context (Fixed high activation)
        # Node 1: Candidate Assertion (Variable)
        # Node 2: Logical Consistency (Derived from conditionals/negations)
        # Node 3: Numeric Consistency
        
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        # Bias: Prompt presence forces Node 0 to 1
        b[0] = 10.0 
        
        # Interaction: Prompt activates Candidate exploration
        W[1, 0] = 1.0
        
        # Logical Constraints (Active Inference synergy)
        # If prompt has conditionals, candidate must reflect logical flow or contradiction
        if p_feat['conditionals']:
            # Strong coupling between context and logic check
            W[2, 0] = 1.5
            W[2, 1] = 1.0 # Candidate must align with logic
            
            # Negation handling: If prompt has negation and candidate ignores it, penalty
            if p_feat['negations'] and not c_feat['negations']:
                W[2, 1] = -1.0 # Repress candidate if it misses negation context
        
        # Numeric Constraints
        if p_feat['numbers'] and c_feat['numbers']:
            p_nums = sorted(p_feat['numbers'])
            c_nums = sorted(c_feat['numbers'])
            # Simple consistency check: do numbers match or follow trend?
            if len(p_nums) == len(c_nums):
                match = all(abs(p_nums[i] - c_nums[i]) < 1e-6 for i in range(len(p_nums)))
                if match:
                    b[3] = 2.0 # Boost for numeric match
                else:
                    W[3, 1] = -2.0 # Repress if numbers differ significantly
            elif c_nums[0] in p_nums:
                 b[3] = 1.0 # Partial credit for presence

        # Active Inference Loop: Minimize Free Energy
        # Initialize state s
        s = np.array([0.9, 0.5, 0.5, 0.5]) 
        
        for _ in range(self.steps):
            s_pred = self._sigmoid(np.dot(W, s) + b)
            
            # Prediction Error Term
            error = s - s_pred
            
            # Entropy Term Gradient (d/ds [s log s + (1-s) log (1-s)])
            # Derivative is log(s) - log(1-s) = log(s/(1-s))
            # Avoid log(0)
            s_clip = np.clip(s, 1e-9, 1-1e-9)
            entropy_grad = np.log(s_clip) - np.log(1 - s_clip)
            
            # Total Gradient
            grad = error + self.tau * entropy_grad
            
            # Gradient Descent Step
            s -= self.lr * grad
            s = np.clip(s, 0.0, 1.0)
            
        # Calculate Final Free Energy (Negative score = better)
        pred_error = np.sum((s - self._sigmoid(np.dot(W, s) + b))**2)
        entropy_val = np.sum(s_clip * np.log(s_clip) + (1-s_clip) * np.log(1-s_clip))
        free_energy = pred_error + self.tau * entropy_val
        
        # Return inverse free energy as coherence score, plus specific logic bonuses
        logic_bonus = 0.0
        if p_feat['conditionals'] and c_feat['conditionals']:
            logic_bonus = 0.2
        if p_feat['negations'] and c_feat['negations']:
            logic_bonus += 0.1
            
        return float(-free_energy + logic_bonus), s

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        def zlib_len(s): return len(zlib.compress(s.encode()))
        l1, l2, l12 = zlib_len(s1), zlib_len(s2), zlib_len(s1 + s2)
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score, _ = self._build_grn(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": "GRN-ActiveInference"})
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within 0.01)
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < 0.01:
                ncd_i = self._ncd_score(prompt, results[i]['candidate'])
                ncd_next = self._ncd_score(prompt, results[i+1]['candidate'])
                if ncd_i < ncd_next: # Lower NCD is better similarity
                    pass # Keep order
                else:
                    # Swap
                    results[i], results[i+1] = results[i+1], results[i]
                    
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, state = self._build_grn(prompt, answer)
        # Normalize score to 0-1 range roughly based on typical free energy magnitudes
        # High negative free energy (low error) -> high confidence
        # Heuristic mapping: score > 0 -> 0.5+, score < -1 -> 0.0
        conf = 1.0 / (1.0 + math.exp(-score)) 
        return min(1.0, max(0.0, conf))

# Import zlib inside function to avoid top-level dependency issues if restricted, 
# but standard lib allows it. Added here for the NCD helper.
import zlib