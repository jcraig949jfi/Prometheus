import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ecologically-Regulated Embodied Reservoir (ERER) Approximation.
    
    Mechanism:
    Instead of a full differential equation solver (too slow/complex for this constraint),
    we simulate the 'Ecological Reservoir' using a fixed random recurrent matrix (Echo State).
    The 'Ecosystem Dynamics' are modeled by modulating the reservoir's effective gain based on
    structural parsing of the prompt (treating logical operators as 'species' interacting).
    
    1. Embodiment: The input string is parsed into a vector of structural features (negations, comparatives, numbers).
    2. Reservoir: A fixed random recurrent matrix projects these features into a high-dimensional space.
    3. Ecological Regulation: We apply a Lotka-Volterra inspired gain modulation. If 'conflict' (negation + affirmation)
       is detected, the system enters a 'high-variance' state (simulating ecosystem disturbance), widening the 
       search space for hypothesis testing.
    4. Readout: Candidates are projected into the same space. The score is the cosine similarity between the 
       prompt's ecological state and the candidate's state, adjusted by structural constraint satisfaction.
    """

    def __init__(self):
        # Fixed topology reservoir (Echo State Network style)
        np.random.seed(42)
        self.reservoir_size = 64
        self.W = np.random.randn(self.reservoir_size, self.reservoir_size) * 0.5
        # Normalize for stability (spectral radius < 1)
        self.W *= 0.9 / np.max(np.abs(np.linalg.eigvals(self.W)))
        self.input_map = np.random.randn(self.reservoir_size, 10) # Map 10 features to reservoir
        
        # Ecological interaction matrix (Lotka-Volterra coefficients approximation)
        # Represents how logical features inhibit/facilitate each other
        self.eco_matrix = np.random.randn(self.reservoir_size, self.reservoir_size) * 0.1
        np.fill_diagonal(self.eco_matrix, -0.5) # Self-regulation (logistic growth limit)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = np.zeros(10)
        
        # 1. Negations (Inhibition)
        negations = ['not', 'no', 'never', 'none', 'neither', 'without', 'fail']
        features[0] = sum(1 for w in negations if w in text_lower.split()) / 5.0
        
        # 2. Comparatives (Relation)
        comparatives = ['greater', 'less', 'more', 'fewer', 'better', 'worse', '>', '<', 'than']
        features[1] = sum(1 for w in comparatives if w in text_lower) / 5.0
        
        # 3. Conditionals (Causality)
        conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when']
        features[2] = sum(1 for w in conditionals if w in text_lower.split()) / 5.0
        
        # 4. Numeric presence
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        features[3] = min(len(nums) / 5.0, 1.0)
        
        # 5. Logical connectors
        logic = ['and', 'or', 'but', 'however', 'therefore', 'because']
        features[4] = sum(1 for w in logic if w in text_lower.split()) / 5.0
        
        # 6. Question markers (Hypothesis trigger)
        questions = ['?', 'what', 'which', 'how', 'why', 'is it', 'does it']
        features[5] = sum(1 for w in questions if w in text_lower) / 5.0
        
        # 7. Certainty markers
        certainty = ['must', 'always', 'certainly', 'definitely', 'impossible']
        features[6] = sum(1 for w in certainty if w in text_lower.split()) / 5.0
        
        # 8. Length complexity (proxy for cognitive load)
        features[7] = min(len(text.split()) / 50.0, 1.0)
        
        # 9. Boolean keywords
        booleans = ['true', 'false', 'yes', 'no']
        features[8] = sum(1 for w in booleans if w in text_lower.split()) / 5.0
        
        # 10. Action verbs (Embodiment proxy)
        actions = ['move', 'run', 'push', 'pull', 'calculate', 'compute', 'change']
        features[9] = sum(1 for w in actions if w in text_lower.split()) / 5.0
        
        return features

    def _run_ecological_reservoir(self, features: np.ndarray, steps: int = 10) -> np.ndarray:
        """
        Simulate the ERER dynamics.
        The reservoir state evolves under fixed topology, modulated by ecological gains.
        """
        state = np.zeros(self.reservoir_size)
        input_drive = np.dot(self.input_map, features).flatten()
        
        # Initial kick
        state = np.tanh(input_drive + np.random.randn(self.reservoir_size) * 0.01)
        
        for _ in range(steps):
            # Linear dynamics
            new_state = np.tanh(np.dot(self.W, state) + input_drive)
            
            # Ecological Modulation (Lotka-Volterra style interaction)
            # dx/dt = x * (r - Ax) -> Here approximated as element-wise modulation
            # If features indicate high conflict (negation + affirmation), increase variance
            conflict = features[0] * features[8] # Negation * Boolean
            gain = 1.0 + (conflict * 0.5) 
            
            state = new_state * gain
            
            # Homeostatic plasticity approximation (slow regulation)
            state = state - 0.1 * (state ** 3) # Prevent explosion
            
        return state

    def _numeric_check(self, prompt: str, candidate: str) -> float:
        """Explicitly handle numeric comparisons if present."""
        nums_p = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        nums_c = re.findall(r"[-+]?\d*\.\d+|\d+", candidate)
        
        if not nums_p or not nums_c:
            return 0.0 # No numeric overlap to check
            
        try:
            # Simple heuristic: if prompt asks for greater/less, check candidate relation
            p_val = float(nums_p[-1])
            c_val = float(nums_c[-1])
            
            if 'greater' in prompt.lower() or '>' in prompt:
                return 1.0 if c_val > p_val else 0.0
            if 'less' in prompt.lower() or '<' in prompt:
                return 1.0 if c_val < p_val else 0.0
            if 'equal' in prompt.lower() or '=' in prompt:
                return 1.0 if abs(c_val - p_val) < 1e-6 else 0.0
                
        except ValueError:
            return 0.0
        return 0.0

    def _structural_match(self, prompt: str, candidate: str) -> float:
        """Check for constraint propagation (negation flipping, etc)."""
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 0.0
        
        # If prompt has 'not', candidate should reflect negation or opposite
        if ' not ' in p_low or ' no ' in p_low:
            # Heuristic: if prompt denies X, and candidate affirms X without qualification, lower score?
            # Hard to do without NLP, so we check for explicit contradiction markers
            if 'yes' in c_low and 'no' not in c_low:
                score -= 0.2
            if 'true' in c_low and 'false' not in c_low:
                score -= 0.2
                
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        prompt_state = self._run_ecological_reservoir(prompt_feats)
        
        results = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            cand_state = self._run_ecological_reservoir(cand_feats)
            
            # Cosine similarity as primary "resonance" score
            norm_p = np.linalg.norm(prompt_state)
            norm_c = np.linalg.norm(cand_state)
            if norm_p == 0 or norm_c == 0:
                similarity = 0.0
            else:
                similarity = float(np.dot(prompt_state, cand_state) / (norm_p * norm_c))
            
            # Structural bonuses
            struct_score = self._structural_match(prompt, cand)
            numeric_bonus = 0.0
            
            # Only apply numeric check if numbers exist
            if re.search(r'\d', prompt):
                numeric_bonus = self._numeric_check(prompt, cand)
                if numeric_bonus != 0.0:
                    # Strong signal override
                    similarity = numeric_bonus 
                else:
                    # Penalty for mismatched numbers if prompt had specific constraints
                    pass 
            
            final_score = similarity + struct_score
            
            # Reasoning string generation
            reason = f"Resonance: {similarity:.2f}"
            if numeric_bonus != 0:
                reason = f"Numeric constraint {'satisfied' if numeric_bonus > 0 else 'violated'}"
            elif struct_score < 0:
                reason = "Logical contradiction detected"
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        # Normalize score to 0-1 range roughly
        # Similarity is -1 to 1, shift to 0-1
        raw_score = ranked[0]['score']
        conf = (raw_score + 1.0) / 2.0
        return max(0.0, min(1.0, conf))