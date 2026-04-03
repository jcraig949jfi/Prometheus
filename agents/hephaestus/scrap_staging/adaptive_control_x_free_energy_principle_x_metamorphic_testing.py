import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Adaptive Control, Free Energy Principle, and Metamorphic Testing
    with a Dynamical Systems tracker (Lyapunov-style stability) for epistemic honesty.
    
    Mechanism:
    1. Parses atomic propositions and structural features (negation, causality, numbers).
    2. Constructs a state vector evolving through the text (Dynamical System).
    3. Applies metamorphic transformations to test invariant robustness.
    4. Uses Free Energy minimization to adaptively weight features against prediction errors.
    5. Scores based on trajectory stability (convergence) and low free energy.
    """

    def __init__(self):
        # Structural patterns
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b|\b[<>]=?\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if|provided that)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|causes|results in|due to)\b', re.I),
            'ordering': re.compile(r'\b(first|second|next|before|after|preceding|following)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|every|each|any|no)\b', re.I),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|why did .+ fail|why is .+ true)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or|must be .+ or)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believes)\b', re.I)
        }
        
        # Metamorphic transformations config
        self.metamorphs = ['neg_swap', 'num_double', 'order_reverse']
        
        # Adaptive Control Params
        self.alpha = 0.01  # Learning rate
        self.lambda_reg = 0.001  # Regularization
        self.W = None  # Weight matrix, initialized on first use
        self.n_features = 7  # Number of structural features tracked

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural feature vector f ∈ ℝ^7"""
        text_lower = text.lower()
        features = np.zeros(self.n_features)
        
        # 1. Negation
        features[0] = len(self.patterns['negation'].findall(text))
        # 2. Comparative
        features[1] = len(self.patterns['comparative'].findall(text))
        # 3. Conditional
        features[2] = len(self.patterns['conditional'].findall(text))
        # 4. Causal
        features[3] = len(self.patterns['causal'].findall(text))
        # 5. Ordering
        features[4] = len(self.patterns['ordering'].findall(text))
        # 6. Numeric density
        nums = self.patterns['numeric'].findall(text)
        features[5] = sum(float(n) for n in nums) if nums else 0.0
        # 7. Quantifier
        features[6] = len(self.patterns['quantifier'].findall(text))
        
        return features

    def _dynamical_tracker(self, text: str) -> Tuple[float, float]:
        """
        Simulate state evolution as a dynamical system.
        Returns (stability_score, convergence_rate).
        High stability = robust reasoning. High divergence = fragile/ambiguous.
        """
        # Split into logical chunks (sentences/clauses)
        chunks = re.split(r'[.,;!?]', text)
        chunks = [c.strip() for c in chunks if c.strip()]
        
        if not chunks:
            return 0.0, 0.0

        state = np.zeros(self.n_features)
        trajectory = []
        epsilon = 1e-6

        for chunk in chunks:
            delta = self._extract_features(chunk)
            # State update rule: x_t = tanh(A * x_{t-1} + B * u_t)
            # Simplified reservoir dynamics
            state = np.tanh(state + delta) 
            trajectory.append(state.copy())
        
        if len(trajectory) < 2:
            return 1.0, 1.0

        # Lyapunov-like stability: Measure average deviation from mean state
        traj_matrix = np.array(trajectory)
        mean_state = np.mean(traj_matrix, axis=0)
        deviations = np.linalg.norm(traj_matrix - mean_state, axis=1)
        
        # Stability: Inverse of average deviation (normalized)
        # Low deviation -> High stability
        avg_dev = np.mean(deviations) + epsilon
        stability = 1.0 / (1.0 + avg_dev)
        
        # Convergence: Difference between first half and second half means
        mid = len(trajectory) // 2
        if mid == 0: mid = 1
        first_half = np.mean(traj_matrix[:mid], axis=0)
        second_half = np.mean(traj_matrix[mid:], axis=0)
        convergence_dist = np.linalg.norm(second_half - first_half)
        convergence_rate = 1.0 / (1.0 + convergence_dist)
        
        return stability, convergence_rate

    def _apply_metamorph(self, text: str, m_type: str) -> str:
        """Apply metamorphic transformation to text"""
        if m_type == 'neg_swap':
            # Simple toggle: add 'not' if missing, remove if present (heuristic)
            if ' not ' in text.lower():
                return text.replace(' not ', ' ').replace('Not ', ' ')
            else:
                return text.replace(' is ', ' is not ').replace(' are ', ' are not ')
        elif m_type == 'num_double':
            def double_num(match):
                val = float(match.group(0))
                return str(val * 2)
            return self.patterns['numeric'].sub(double_num, text)
        elif m_type == 'order_reverse':
            # Reverse list-like structures (simple heuristic)
            return " ".join(text.split()[::-1])
        return text

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Free Energy F = 1/2 ||Wf - e||^2 + lambda||W||^2
        Where e is the error between predicted and actual metamorphic changes.
        """
        f = self._extract_features(prompt + " " + candidate)
        
        # Initialize weights if needed
        if self.W is None:
            self.W = np.random.randn(len(self.metamorphs), self.n_features) * 0.1
            
        errors = []
        for m in self.metamorphs:
            # Predicted change (heuristic model: we expect specific features to change)
            delta_hat = np.zeros(self.n_features)
            if m == 'neg_swap': delta_hat[0] = 1.0 # Expect negation change
            if m == 'num_double': delta_hat[5] = 1.0 # Expect numeric change
            if m == 'order_reverse': delta_hat[4] = 1.0 # Expect ordering change
            
            # Actual change
            transformed = self._apply_metamorph(prompt + " " + candidate, m)
            f_prime = self._extract_features(transformed)
            delta_actual = f_prime - f
            
            # Error vector for this metamorph
            err_vec = delta_actual - delta_hat
            errors.append(err_vec)
            
            # Adaptive Update (Gradient Descent step on W)
            # W <- W - alpha * ( (Wf - e)f^T + 2lambda*W )
            # Here 'e' is approximated by the error in prediction logic
            # Simplified update for online adaptation
            pred = self.W @ f
            # We treat the metamorphic error as the surprise signal
            surprise = np.linalg.norm(err_vec) 
            # Update weights to minimize surprise
            self.W -= self.alpha * (np.outer((pred - err_vec[:len(self.metamorphs)]), f) + 2 * self.lambda_reg * self.W)

        # Stack errors
        E = np.array(errors) # Shape: (M, Features)
        # Project to weight space dimension for F calculation
        # F = 0.5 * || W*f - E_flat ||^2 ... simplified for scalar score
        # We sum squared errors across metamorphs as the energy
        total_error = np.sum(np.square(E))
        F = 0.5 * total_error + self.lambda_reg * np.sum(np.square(self.W))
        return -F # Score is negative free energy

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity/traps.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            return 0.3
            
        # 3. Subjectivity without data
        if self.patterns['subjectivity'].search(prompt) and 'data' not in p_lower:
            return 0.4
            
        # 4. Pronoun/Scope ambiguity (Heuristic: presence of 'who', 'which' with multiple subjects)
        if re.search(r'\b(who|which|he|she|they)\b', p_lower) and len(prompt.split()) > 10:
            # If it asks for resolution of ambiguity without context
            if 'who' in p_lower or 'which one' in p_lower:
                return 0.3

        # Default: No strong ambiguity detected
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0-1, lower is more similar)"""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        len_max = max(len(z1), len(z2))
        if len_max == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / len_max

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Pre-check prompt ambiguity
        prompt_cap = self._meta_confidence(prompt)
        
        # Dynamical system baseline for the prompt
        prompt_stab, prompt_conv = self._dynamical_tracker(prompt)
        
        for cand in candidates:
            full_text = f"{prompt} {cand}"
            
            # 1. Structural & Dynamical Analysis
            stab, conv = self._dynamical_tracker(full_text)
            
            # 2. Free Energy Score (Adaptive/Metamorphic)
            fe_score = self._compute_free_energy(prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            
            # Composite Score Construction
            # Dynamics (40%) + Structural/FE (45%) + NCD (15%)
            # Note: FE is negative energy, so higher is better. NCD is distance, lower is better.
            
            dyn_score = (stab + conv) / 2.0
            struct_score = (fe_score + 10) / 20.0 # Normalize FE roughly to 0-1 range
            ncd_contrib = (1.0 - ncd) * 0.15
            
            # Weighted sum
            raw_score = (dyn_score * 0.40) + (struct_score * 0.45) + ncd_contrib
            
            # Apply Epistemic Cap (Tier B)
            # If prompt is ambiguous, max score is capped
            if prompt_cap < 0.5:
                raw_score = min(raw_score, prompt_cap)
                
            # Generate reasoning string
            reason_parts = []
            if stab < 0.5: reason_parts.append("Unstable reasoning trajectory")
            if prompt_cap < 0.5: reason_parts.append("Potential logical trap/ambiguity detected")
            if not reason_parts: reason_parts.append("Structurally consistent")
            
            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": "; ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta Confidence Cap (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Compute raw confidence based on stability and FE
        stab, conv = self._dynamical_tracker(f"{prompt} {answer}")
        fe_score = self._compute_free_energy(prompt, answer)
        
        # Normalize FE to ~0-1 (heuristic)
        norm_fe = 1.0 / (1.0 + np.exp(-fe_score)) 
        
        raw_conf = (stab * 0.4 + norm_fe * 0.4 + conv * 0.2)
        
        # Apply cap
        final_conf = min(raw_conf, cap)
        
        # Hard floor for "I don't know" scenarios
        if cap < 0.3:
            return 0.2 # Explicitly low confidence
            
        return float(np.clip(final_conf, 0.0, 0.95)) # Never 1.0 to allow uncertainty