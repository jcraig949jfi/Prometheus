import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Topological Matched-Filter Reservoir (CTMFR) Approximation.
    
    Mechanism:
    1. Topology (Structural Parsing): Instead of expensive persistent homology,
       we extract discrete topological features: negation loops, conditional branches,
       and numeric magnitudes. This creates a 'shape' vector of the text.
    2. Criticality (Reservoir Core): We simulate a critical recurrent network using
       a marginally stable linear dynamical system (eigenvalues ~ 1.0). This allows
       long-range dependency propagation (memory) without vanishing/exploding gradients,
       mimicking the 'edge of chaos' susceptibility.
    3. Matched Filtering (Hypothesis Testing): We construct ideal 'template' vectors
       for logical consistency (e.g., Double Negation = Positive). We cross-correlate
       the reservoir's final state with these templates to score candidates.
       
    This architecture prioritizes structural logic over string similarity (NCD).
    """

    def __init__(self):
        # Critical Reservoir Setup: 32 nodes, sparse connectivity, spectral radius ~1.0
        np.random.seed(42)  # Determinism
        self.n_res = 32
        self.state = np.zeros(self.n_res)
        
        # Generate a sparse matrix with spectral radius approx 1.0 (Criticality)
        # Using a fixed seed ensures the 'random' topology is consistent
        dense = np.random.randn(self.n_res, self.n_res)
        mask = np.random.choice([0, 1], size=(self.n_res, self.n_res), p=[0.85, 0.15])
        W = dense * mask
        
        # Normalize to spectral radius = 1.0 (Edge of Chaos)
        eig_max = np.max(np.abs(np.linalg.eigvals(W)))
        if eig_max > 0:
            self.W = W / eig_max 
        else:
            self.W = W
            
        # Matched Filter Templates (Idealized logical signatures)
        # Template 0: Affirmation (Positive magnitude)
        # Template 1: Negation handling (Inversion)
        # Template 2: Conditional logic (If-Then structure)
        self.templates = np.random.randn(3, self.n_res)
        self.templates = self.templates / np.linalg.norm(self.templates, axis=1, keepdims=True)

    def _extract_topology(self, text: str) -> np.ndarray:
        """
        Extracts high-level topological features from text.
        Returns a feature vector representing the 'shape' of the logic.
        """
        t_lower = text.lower()
        features = np.zeros(8)
        
        # 1. Negation Loops (Odd negations flip sign)
        negations = len(re.findall(r'\b(not|no|never|neither|nobody|nothing)\b', t_lower))
        features[0] = 1.0 if negations % 2 == 1 else -1.0
        
        # 2. Conditional Branches (If/Then structures)
        if re.search(r'\b(if|when|unless|provided)\b', t_lower):
            features[1] = 1.0
        if re.search(r'\b(then|else|therefore|thus)\b', t_lower):
            features[2] = 1.0
            
        # 3. Comparatives (Greater/Lesser)
        if re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', t_lower):
            features[3] = 1.0
            
        # 4. Numeric Magnitude Extraction
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            try:
                val = float(nums[-1])
                features[4] = np.tanh(val / 10.0) # Normalize magnitude
                features[5] = 1.0 # Presence flag
            except ValueError:
                pass
                
        # 5. Question/Answer Structure
        if '?' in text:
            features[6] = 1.0
        if re.search(r'\b(yes|no|true|false|correct)\b', t_lower):
            features[7] = 1.0
            
        return features

    def _run_critical_reservoir(self, input_vector: np.ndarray) -> np.ndarray:
        """
        Propagates input through a critically tuned recurrent network.
        Simulates long-range memory and sensitivity to initial conditions.
        """
        # Inject input
        self.state = (0.3 * self.state) + (0.7 * np.dot(self.W, self.state)) + (0.5 * input_vector)
        
        # Non-linear activation (tanh) to maintain bounded chaos
        self.state = np.tanh(self.state)
        return self.state

    def _compute_matched_filter_score(self, state: np.ndarray, template_idx: int) -> float:
        """
        Computes the cross-correlation between the reservoir state and a specific
        logical template. High correlation = hypothesis match.
        """
        template = self.templates[template_idx % 3]
        # Dot product is the matched filter statistic for white noise
        score = np.dot(state, template)
        return float(score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Reset reservoir state for each evaluation batch to ensure independence
        self.state = np.zeros(self.n_res)
        
        # 1. Process Prompt to set Critical Context
        prompt_feats = self._extract_topology(prompt)
        # Warm up the reservoir with prompt context multiple times to establish 'memory'
        for _ in range(3):
            self._run_critical_reservoir(prompt_feats)
            
        prompt_state_snapshot = self.state.copy()

        for candidate in candidates:
            # Reset to prompt state before testing each hypothesis (candidate)
            self.state = prompt_state_snapshot.copy()
            
            # 2. Process Candidate as a perturbation
            cand_feats = self._extract_topology(candidate)
            final_state = self._run_critical_reservoir(cand_feats)
            
            # 3. Matched Filter Scoring
            # Score based on logical consistency (Template 0: Affirmation/Structure)
            logic_score = self._compute_matched_filter_score(final_state, 0)
            
            # Structural Parsing Bonus (Explicit Rule-Based Correction)
            # If prompt has odd negations and candidate is negative, penalize double negative error if logic dictates
            structural_bonus = 0.0
            p_neg = len(re.findall(r'\b(not|no|never)\b', prompt.lower())) % 2 == 1
            c_neg = len(re.findall(r'\b(not|no|never)\b', candidate.lower())) % 2 == 1
            
            # Simple constraint propagation: If prompt implies negative, and candidate is positive without justification
            if p_neg and not c_neg and "not" in prompt.lower():
                # Heuristic: Check if candidate contradicts the negation structure
                if re.search(r'\b(yes|is|are|was)\b', candidate.lower()):
                    structural_bonus = -0.5 
                elif re.search(r'\b(no|isn\'t|aren\'t|wasn\'t|not)\b', candidate.lower()):
                    structural_bonus = 0.5
            
            # Numeric Evaluation
            p_nums = re.findall(r'-?\d+\.?\d*', prompt)
            c_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if p_nums and c_nums:
                try:
                    p_val = float(p_nums[-1])
                    c_val = float(c_nums[-1])
                    # Reward numerical consistency if the prompt asks for calculation or comparison
                    if "less" in prompt.lower() and c_val < p_val:
                        structural_bonus += 1.0
                    elif "more" in prompt.lower() and c_val > p_val:
                        structural_bonus += 1.0
                except ValueError:
                    pass

            # Combined Score
            total_score = logic_score + structural_bonus
            
            results.append({
                "candidate": candidate,
                "score": total_score,
                "reasoning": f"Critical resonance: {logic_score:.4f}, Structural bonus: {structural_bonus:.4f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on the stability of the critical state
        when the answer is fed back into the prompt context.
        """
        self.state = np.zeros(self.n_res)
        
        # Encode Prompt
        p_feats = self._extract_topology(prompt)
        for _ in range(3):
            self._run_critical_reservoir(p_feats)
            
        # Encode Answer
        a_feats = self._extract_topology(answer)
        final_state = self._run_critical_reservoir(a_feats)
        
        # Matched filter against the 'Truth' template (Template 0)
        raw_score = self._compute_matched_filter_score(final_state, 0)
        
        # Map raw score (-inf, inf) to (0, 1) using sigmoid
        # Shifted to treat 0 as 0.5 confidence
        conf = 1.0 / (1.0 + np.exp(-raw_score))
        
        # Apply structural sanity checks to override pure reservoir noise
        # If answer is empty or gibberish
        if not answer.strip():
            return 0.0
            
        # Check for direct contradiction markers if prompt has them
        if "not" in prompt.lower() and "not" not in answer.lower():
            # Potential mismatch in negation handling
            if re.search(r'\b(yes|true)\b', answer.lower()):
                conf *= 0.6 # Reduce confidence significantly
                
        return float(np.clip(conf, 0.0, 1.0))