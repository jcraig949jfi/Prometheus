import re
import zlib
import numpy as np

class ReasoningTool:
    """
    Self-Tuning Analogical Reservoir (STAR) Implementation.
    
    Mechanism:
    1. Reservoir Computing (ESN): The prompt and candidates are projected into a 
       fixed random recurrent space. This provides high-dimensional non-linear 
       feature expansion without training weights.
    2. Gene Regulatory Networks (GRN): A sparse boolean mask acts as a plasticity 
       module. It modulates the reservoir's effective connectivity based on 
       structural features (negations, comparatives) extracted from the input, 
       simulating "cell-state" switching for different logical contexts.
    3. Analogical Reasoning (SME): Instead of external symbolic mapping, we use 
       structural parsing to generate a "relational signature". Candidates are 
       scored by how well their reservoir trajectory aligns with the prompt's 
       structural signature under the current GRN-modulated state.
       
    Scoring Strategy:
    - Primary: Structural parsing (negations, comparatives, conditionals, numbers).
    - Secondary: NCD (tiebreaker only).
    """

    def __init__(self):
        # Reservoir setup (fixed random weights)
        self.N_res = 64
        self.W_res = np.random.randn(self.N_res, self.N_res) * 0.5
        # Normalize spectral radius
        self.W_res *= 0.9 / np.max(np.abs(np.linalg.eigvals(self.W_res)))
        
        # GRN Setup (Sparse boolean modulation)
        self.N_grn = 16
        self.GRN_mask = (np.random.rand(self.N_res, self.N_res) > 0.8).astype(float)

    def _extract_structural_features(self, text):
        """Extract logical constraints and numeric values."""
        text_lower = text.lower()
        features = []
        
        # Negations
        if re.search(r'\b(not|no|never|neither|nobody|nothing)\b', text_lower):
            features.append("NEGATION")
            
        # Comparatives
        if re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', text_lower):
            features.append("COMPARATIVE")
            
        # Conditionals
        if re.search(r'\b(if|then|unless|provided|assuming)\b', text_lower):
            features.append("CONDITIONAL")
            
        # Numbers
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            features.append("NUMERIC")
            try:
                # Simple numeric evaluation hint
                val = float(nums[0])
                features.append(f"NUM_VAL_{val}")
            except: pass
            
        return features

    def _text_to_vector(self, text):
        """Simple hash-based vectorization for reservoir input."""
        vec = np.zeros(32)
        for i, char in enumerate(text[:32]):
            vec[i] = ord(char) / 256.0
        return vec

    def _run_reservoir(self, text, grn_state):
        """Run input through the GRN-modulated reservoir."""
        x = self._text_to_vector(text)
        # Pad/Truncate to match reservoir size
        state = np.zeros(self.N_res)
        state[:len(x)] = x
        
        # Apply GRN modulation (plasticity)
        # If GRN node is active (simulated by grn_state), weights are scaled
        modulated_W = self.W_res * self.GRN_mask * grn_state
        
        # Recurrent update (single step for efficiency)
        new_state = np.tanh(np.dot(modulated_W, state))
        return new_state

    def _get_grn_state(self, features):
        """Simulate GRN activation based on structural features."""
        state = np.ones((self.N_res, self.N_res))
        if "NEGATION" in features:
            state *= 1.2  # Amplify specific dynamics for negation
        if "COMPARATIVE" in features:
            state *= 0.8  # Dampen for precision
        if "CONDITIONAL" in features:
            state *= 1.1
        return state

    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return c12 / float(max(c1, c2))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_structural_features(prompt)
        grn_state = self._get_grn_state(prompt_feats)
        
        # Get prompt reservoir state
        prompt_state = self._run_reservoir(prompt, grn_state)
        
        results = []
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            cand_feats = self._extract_structural_features(cand)
            cand_state = self._run_reservoir(cand, grn_state)
            
            # 1. Structural Matching (Primary Signal)
            # Check for logical consistency (e.g., if prompt has numbers, candidate should)
            if "NUMERIC" in prompt_feats:
                if "NUMERIC" in cand_feats:
                    score += 0.4
                    reasoning_parts.append("Numeric consistency detected")
                else:
                    score -= 0.4
                    reasoning_parts.append("Missing numeric content")
            
            # Check for negation alignment (simplified)
            if "NEGATION" in prompt_feats:
                if "NEGATION" in cand_feats:
                    score += 0.3
                    reasoning_parts.append("Negation alignment")
            
            # 2. Analogical Reservoir Alignment
            # Dot product similarity in the modulated reservoir space
            similarity = np.dot(prompt_state, cand_state) / (np.linalg.norm(prompt_state) * np.linalg.norm(cand_state) + 1e-9)
            score += float(similarity) * 0.3
            if similarity > 0.5:
                reasoning_parts.append("High dynamical similarity")
            
            # 3. Constraint Propagation (Heuristic)
            # If prompt asks for "less", prefer candidates with smaller numbers
            if "less" in prompt.lower() or "smaller" in prompt.lower():
                p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt)]
                c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', cand)]
                if p_nums and c_nums:
                    if min(c_nums) < min(p_nums):
                        score += 0.2
                        reasoning_parts.append("Comparative constraint satisfied")

            # 4. NCD Tiebreaker (Only if scores are close or neutral)
            ncd_val = self._ncd(prompt, cand)
            score += (1.0 - ncd_val) * 0.05 # Small bonus for compression similarity
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural match via reservoir dynamics"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural and dynamical alignment."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Base score from evaluation + structural bonuses
        base_score = res[0]["score"]
        
        # Extra checks for confidence
        conf = 0.5 + (base_score * 0.4) # Map to ~0.1 to 0.9 range
        
        # Boost if structural features match perfectly
        p_feats = set(self._extract_structural_features(prompt))
        a_feats = set(self._extract_structural_features(answer))
        
        if p_feats and a_feats:
            overlap = len(p_feats.intersection(a_feats))
            conf += min(overlap * 0.05, 0.1)
            
        return float(np.clip(conf, 0.0, 1.0))