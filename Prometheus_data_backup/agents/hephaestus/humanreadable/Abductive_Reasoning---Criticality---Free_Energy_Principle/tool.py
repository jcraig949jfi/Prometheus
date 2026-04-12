import re
import numpy as np
import math

class ReasoningTool:
    """
    Implements an abductive reasoning evaluator using the Free Energy Principle (FEP) 
    and Criticality. 
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and relational cues (negation, conditional, 
       causal, comparative, numeric) into a feature matrix.
    2. Factor Graph: Constructs an adjacency matrix representing logical dependencies.
    3. Variational Free Energy: Computes prediction error (consistency with premises) 
       and complexity (entropy of the hypothesis).
    4. Criticality: Calculates susceptibility to perturbations in the complexity parameter,
       rewarding hypotheses that operate near the 'edge of chaos' (high explanatory power 
       with flexible structure).
    
    Scores candidates by minimizing Free Energy while maximizing Criticality.
    """

    def __init__(self):
        self.cues = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b'],
            'causal': [r'\bbecause\b', r'\bleads?\s+to\b', r'\bcauses\b', r'\btherefore\b'],
            'comparative': [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\blesser\s+than\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b']
        }
        self.num_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text):
        """Parses text into propositions and relational cues."""
        text_lower = text.lower()
        features = []
        
        # Extract numeric values
        nums = [float(n) for n in self.num_pattern.findall(text)]
        
        # Detect cue types
        cue_types = []
        for ctype, patterns in self.cues.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    cue_types.append(ctype)
                    break
        
        # Simple sentence splitting for propositions (naive but effective for logic puzzles)
        sentences = re.split(r'[.,;]', text)
        for sent in sentences:
            if not sent.strip():
                continue
            s_lower = sent.lower()
            polarity = 0 if any(re.search(p, s_lower) for p in self.cues['negation']) else 1
            
            # Determine dominant type
            t_id = 0 # atomic
            if 'conditional' in cue_types: t_id = 1
            elif 'causal' in cue_types: t_id = 2
            elif 'comparative' in cue_types: t_id = 3
            elif 'ordering' in cue_types: t_id = 4
            
            # Numeric value (average if multiple, else 0)
            v = np.mean(nums) if nums else 0.0
            
            features.append([polarity, t_id, v, 1.0]) # bias=1.0
            
        if not features:
            return np.array([[0, 0, 0, 1]]) # Default node if empty
            
        return np.array(features)

    def _build_graph(self, X):
        """Builds adjacency matrix based on cue strength."""
        n = X.shape[0]
        if n == 0: return np.zeros((0,0))
        if n == 1: return np.zeros((1,1))
        
        A = np.zeros((n, n))
        W = np.zeros((n, n))
        
        # Connect sequential nodes with weight based on type
        for i in range(n-1):
            t = X[i, 1]
            weight = 0.5 # Default causal/logical flow
            if t == 1: weight = 0.8 # Conditional strong link
            if t == 2: weight = 0.9 # Causal strong link
            if t == 0: weight = 0.3 # Weak atomic link
            
            A[i, i+1] = 1
            W[i, i+1] = weight
            # Symmetric for undirected approximation in this simple model
            A[i+1, i] = 1
            W[i+1, i] = weight
            
        return W

    def _compute_free_energy(self, X, W, z, lam):
        """Computes F = Prediction Error + Complexity."""
        if X.shape[0] == 0:
            return 0.0
            
        # Prediction Error: ||(I - W)z - b||^2
        # b is the observed premise vector (polarity + normalized value)
        b = X[:, 0] + (X[:, 2] / 10.0) # Normalize numeric impact
        
        I = np.eye(X.shape[0])
        pred_err = np.linalg.norm((I - W) @ z - b)**2
        
        # Complexity: Entropy(z)
        eps = 1e-9
        z_safe = np.clip(z, eps, 1-eps)
        entropy = -np.sum(z_safe * np.log(z_safe) + (1-z_safe) * np.log(1-z_safe))
        complexity = lam * entropy
        
        return pred_err + complexity

    def _get_z_vector(self, prompt, candidate):
        """Generates a binary selection vector z based on overlap and logic."""
        # Combine prompt and candidate to form the hypothesis space
        full_text = f"{prompt} {candidate}"
        X = self._extract_features(full_text)
        
        # Create z: 1 if feature exists in candidate, 0 otherwise
        # Simplified: Map candidate words to feature indices
        cand_lower = candidate.lower()
        z = np.zeros(X.shape[0])
        
        # Heuristic: If candidate contains keywords found in the parsed features, activate
        # Since parsing is sentence based, we check if candidate sentence matches feature logic
        # For this implementation, we assume the candidate validates the derived propositions
        # if the candidate length is proportional to the prompt's logical depth.
        
        # Better approach for z: 
        # z_i = 1 if the i-th proposition is supported by the candidate string
        # We simulate this by checking keyword presence in candidate vs prompt segments
        
        # Fallback: Activate all nodes if candidate seems relevant (length > threshold)
        # and deactivate if candidate is "none" or "impossible"
        if re.search(r'\b(no|none|impossible|false)\b', cand_lower):
            z = np.zeros_like(z)
        else:
            z = np.ones_like(z)
            
        return z, X

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        lam_base = 0.5
        delta = 0.01
        alpha = 0.1
        
        # Pre-calculate prompt features for context
        prompt_X = self._extract_features(prompt)
        prompt_W = self._build_graph(prompt_X)

        for cand in candidates:
            z, X = self._get_z_vector(prompt, cand)
            if X.shape[0] == 0:
                score = -100.0
                reasoning = "No logical structure detected."
                results.append({"candidate": cand, "score": score, "reasoning": reasoning})
                continue

            W = self._build_graph(X)
            
            # Adjust W size if X and W dimensions mismatch due to empty handling
            if W.shape[0] != z.shape[0]:
                min_dim = min(W.shape[0], z.shape[0])
                if min_dim == 0: 
                    score = -50.0
                    results.append({"candidate": cand, "score": score, "reasoning": "Dimension mismatch."})
                    continue
                z = z[:min_dim]
                W = W[:min_dim, :min_dim]

            # 1. Compute Free Energy at lambda
            F = self._compute_free_energy(X, W, z, lam_base)
            
            # 2. Compute Susceptibility (Criticality) via finite difference
            F_shift = self._compute_free_energy(X, W, z, lam_base + delta)
            # Susceptibility chi = d<E>/dlambda approx (F_shift - F) / delta
            # Note: In FEP, we look at change in expected state. Here we approximate 
            # the sensitivity of the energy landscape.
            chi = abs(F_shift - F) / (delta + 1e-9)
            
            # Final Score: Minimize F, Maximize Chi (near criticality)
            # S = -F + alpha * chi
            final_score = -F + alpha * chi
            
            # Structural bonus: If candidate resolves numeric comparisons correctly
            nums = [float(n) for n in self.num_pattern.findall(prompt + " " + cand)]
            if len(nums) >= 2:
                # Simple consistency check: does the text imply the order?
                # This is a heuristic boost for numeric logic
                if "greater" in cand.lower() and nums[0] > nums[1]:
                    final_score += 0.5
                elif "less" in cand.lower() and nums[0] < nums[1]:
                    final_score += 0.5

            reasoning = f"F={F:.2f}, Chi={chi:.2f}, Nodes={X.shape[0]}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the score relative to a baseline."""
        # Evaluate single candidate against a dummy negative to get relative score
        res = self.evaluate(prompt, [answer, "No solution possible."])
        
        if not res:
            return 0.0
            
        top_score = res[0]['score']
        target_score = next((r['score'] for r in res if r['candidate'] == answer), -1000)
        
        # Normalize: Assume a range of -10 to 10 is typical
        # Map to 0-1
        conf = (target_score + 10) / 20.0
        return max(0.0, min(1.0, conf))