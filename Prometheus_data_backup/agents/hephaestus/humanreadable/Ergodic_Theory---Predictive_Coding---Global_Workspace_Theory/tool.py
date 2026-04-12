import re
import numpy as np

class ReasoningTool:
    """
    Implements a reasoning engine based on Ergodic Theory, Predictive Coding, 
    and Global Workspace Theory.
    
    Mechanism:
    1. Parsing: Converts text into structured propositions (negations, comparatives, etc.).
    2. Predictive Coding Loop: Iteratively updates proposition confidence based on 
       prediction error (truth - confidence).
    3. Global Workspace Ignition: Propositions with low error ('stable' beliefs) 
       activate logically connected propositions via a sparse adjacency matrix.
    4. Ergodic Averaging: The final score is the time-average of activation states 
       over the simulation, representing the system's stabilized belief state.
    5. Scoring: Candidates are scored by the dot product of their proposition presence 
       and the ergodic activation vector.
    """

    def __init__(self):
        self.T = 20  # Iterations
        self.eta = 0.1  # Learning rate
        self.tau = 0.1  # Ignition threshold
        self.delta = 0.9  # Decay
        self.types = ['negation', 'comparative', 'conditional', 'numeric', 'causal', 'ordering']
        
        # Regex patterns for extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'(greater|less|higher|lower|more|fewer)\s+than', r'[><]=?', r'\bvs\b'],
            'conditional': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bonly if\b'],
            'numeric': [r'\d+\.?\d*'],
            'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b']
        }

    def _parse_text(self, text: str) -> list:
        """Parses text into a list of proposition dictionaries."""
        propositions = []
        text_lower = text.lower()
        pid = 0
        
        # Check each type
        for p_type, regex_list in self.patterns.items():
            found = False
            for pattern in regex_list:
                if re.search(pattern, text_lower):
                    found = True
                    break
            
            if found:
                # Extract specific payload if numeric or comparative for finer logic
                payload = None
                if p_type == 'numeric':
                    nums = re.findall(r'\d+\.?\d*', text_lower)
                    if len(nums) >= 2:
                        # Simple comparison logic for demo
                        try:
                            v1, v2 = float(nums[0]), float(nums[1])
                            payload = (v1, '<' if v1 < v2 else '>=', v2)
                        except: pass
                
                propositions.append({
                    'id': pid,
                    'type': p_type,
                    'payload': payload,
                    'truth': 1, # Assume extracted features are true premises initially
                    'conf': 0.5,
                    'act': 0.0
                })
                pid += 1
        
        # If no structured props found, create a dummy prop to allow scoring based on presence
        if not propositions:
            propositions.append({
                'id': 0, 'type': 'generic', 'payload': None, 'truth': 1, 'conf': 0.5, 'act': 0.0
            })
            
        return propositions

    def _build_adjacency(self, props: list) -> np.ndarray:
        """Builds a sparse adjacency matrix based on logical reachability."""
        n = len(props)
        if n == 0: return np.array([])
        A = np.zeros((n, n))
        
        # Heuristic connectivity: 
        # 1. Sequential chaining (i -> i+1)
        # 2. Type compatibility (causal links to causal, etc.)
        for i in range(n):
            for j in range(n):
                if i == j: continue
                # Connect sequential
                if abs(i - j) == 1:
                    A[i, j] = 0.5
                # Connect same types (reinforcement)
                if props[i]['type'] == props[j]['type']:
                    A[i, j] = 0.3
                # Causal specific: causal triggers ordering/comparative
                if props[i]['type'] == 'causal' and props[j]['type'] in ['ordering', 'comparative']:
                    A[i, j] = 0.4
                    
        return A

    def _run_simulation(self, prompt: str, candidate: str) -> float:
        """Runs the predictive coding + global workspace simulation."""
        full_text = f"{prompt} {candidate}"
        props = self._parse_text(full_text)
        n = len(props)
        if n == 0: return 0.0

        # Initialize vectors
        truth_vec = np.array([p['truth'] for p in props], dtype=float)
        conf_vec = np.array([p['conf'] for p in props], dtype=float)
        act_vec = np.zeros(n, dtype=float)
        
        A = self._build_adjacency(props)
        act_history = []

        # Predictive Coding Loop
        for t in range(self.T):
            # Prediction
            pred = conf_vec.copy()
            
            # Error calculation
            err = truth_vec - pred
            
            # Update confidence (Gradient step)
            conf_vec = conf_vec + self.eta * err
            conf_vec = np.clip(conf_vec, 0, 1)
            
            # Global Workspace Ignition
            # Select propositions where error is low (stable beliefs)
            ignition_mask = (np.abs(err) < self.tau).astype(float)
            
            if np.sum(ignition_mask) > 0:
                # Broadcast activation to neighbors
                new_act = A.T @ ignition_mask
                act_vec += new_act
            
            # Decay
            act_vec = act_vec * self.delta
            act_vec = np.clip(act_vec, 0, 1)
            
            act_history.append(act_vec.copy())

        # Ergodic Averaging
        if not act_history:
            return 0.0
            
        act_matrix = np.array(act_history)
        ergodic_act = np.mean(act_matrix, axis=0)
        
        # Score: Dot product of candidate presence and ergodic activation
        # Since we parsed the combined text, we assume the candidate contributes 
        # to the truth of the propositions found. 
        # Simplification: Score is the sum of stabilized activations.
        score = float(np.sum(ergodic_act))
        
        # Normalize by length to prevent bias towards longer texts having more props
        # But ensure we don't divide by zero
        norm_factor = max(1.0, float(n))
        return score / norm_factor

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        scores = []
        
        # Calculate scores
        for cand in candidates:
            sc = self._run_simulation(prompt, cand)
            scores.append(sc)
            results.append({
                "candidate": cand,
                "score": sc,
                "reasoning": f"Ergodic activation sum: {sc:.4f}"
            })
        
        # Rank by score descending
        sorted_indices = np.argsort(scores)[::-1]
        ranked_results = [results[i] for i in sorted_indices]
        
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns a confidence score 0-1."""
        sc = self._run_simulation(prompt, answer)
        # Map score to 0-1 range roughly. 
        # Since max activation per node is 1, and we average, 
        # a high score implies strong consistent activation.
        # Heuristic scaling:
        conf = min(1.0, max(0.0, sc * 0.8)) 
        return conf