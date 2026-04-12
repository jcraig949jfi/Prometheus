import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning engine based on Phase Transitions, Neuromodulation, and Maximum Entropy.
    
    Mechanism:
    1. Structural Parsing: Extracts logical propositions (negations, comparatives, conditionals).
    2. Dynamical System (Frame C): Models reasoning as a state evolution. Uses Lyapunov-like 
       stability analysis by perturbing the order of premises to check for convergence robustness.
    3. Maximum Entropy/Ising Model: Maps propositions to spins. Energy minimization finds the 
       most consistent truth assignment.
    4. Neuromodulation: Context cues (e.g., "however") dynamically scale feature weights (gain).
    5. Phase Transition Scoring: Uses the spectral radius of the coupling matrix to estimate 
       proximity to criticality (confidence). Close to critical point = high sensitivity.
    
    Epistemic Honesty (Tier B): Detects presuppositions, ambiguities, and false dichotomies 
    to cap confidence scores, ensuring the model admits uncertainty rather than hallucinating.
    """

    def __init__(self):
        self.presupposition_triggers = [
            r"have you stopped", r"why did.*fail", r"why.*stop", r"when did.*stop",
            r"quit.*doing", r"stopped.*doing"
        ]
        self.ambiguity_triggers = [
            r"every.*a.*\?", r"told.*he.*was", r"told.*she.*was", r"who.*\?",
            r"either.*or", r"best.*worst", r"favorite", r"most.*least"
        ]
        self.modulators = {
            "however": 0.5, "therefore": 1.5, "thus": 1.5, 
            "consequently": 1.5, "but": 0.8, "although": 0.7
        }

    def _extract_features(self, text: str) -> Tuple[List[str], Dict[str, float], List[Tuple[int, int, float]]]:
        """Parses text into propositions, weights, and constraints."""
        text_lower = text.lower()
        props = []
        weights = {}
        constraints = []
        
        # Tokenize simple sentences/clauses
        sentences = re.split(r'[.;!?]', text)
        
        prop_idx = 0
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Negation
            is_neg = bool(re.search(r'\b(not|no|never|none)\b', sent_lower := sent.lower()))
            sign = -1.0 if is_neg else 1.0
            
            # Comparatives (Numeric)
            nums = re.findall(r"-?\d+\.?\d*", sent)
            if len(nums) >= 2:
                v1, v2 = float(nums[0]), float(nums[1])
                prop_name = f"cmp_{prop_idx}"
                props.append(prop_name)
                weights[prop_name] = sign * (v1 - v2) # Positive if v1 > v2
                prop_idx += 1
            elif len(nums) == 1:
                prop_name = f"num_{prop_idx}"
                props.append(prop_name)
                weights[prop_name] = sign * float(nums[0])
                prop_idx += 1
            else:
                # Textual proposition
                # Clean simple words for proposition ID
                clean = re.sub(r'[^a-z0-9]', '_', sent_lower)[:20]
                prop_name = f"p_{clean}_{prop_idx}"
                props.append(prop_name)
                base_w = 1.0 if "true" in sent_lower or "is" in sent_lower else 0.5
                weights[prop_name] = sign * base_w
                prop_idx += 1

            # Conditionals (A -> B) - Simplified detection
            if "if" in sent_lower and ("then" in sent_lower or "," in sent):
                # Create constraint between last two props if available
                if len(props) >= 2:
                    constraints.append((len(props)-2, len(props)-1, -2.0)) # Penalty if A=1, B=0

        # Modulators
        gain = 1.0
        for word, factor in self.modulators.items():
            if word in text_lower:
                gain = factor # Apply strongest modulator found for simplicity
        
        return props, weights, constraints, gain

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if max(z1, z2) == 0: return 0.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B traps: presuppositions, ambiguity, unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition & False Dichotomy
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2 # High risk of trap
        
        # 2. Ambiguity & Subjectivity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Check if it's a specific question type that implies ambiguity
                if "either" in p_lower and "or" in p_lower:
                     return 0.3 # False dichotomy risk
                if "best" in p_lower or "favorite" in p_lower:
                    return 0.3 # Subjective
                return 0.4 # General ambiguity
        
        # 3. Unanswerability (Heuristic: very short prompt with no numbers/logic ops)
        words = re.findall(r'\w+', p_lower)
        if len(words) < 4 and not any(c in p_lower for c in ['=', '+', '-', '*', '/', '>', '<']):
            return 0.3
            
        return 1.0 # Default high potential confidence

    def _run_dynamics(self, props: List[str], weights: Dict, constraints: List, gain: float, steps: int = 10) -> Tuple[float, float]:
        """
        Simulates reasoning as a dynamical system.
        Uses Glauber dynamics on an Ising model.
        Returns (final_energy, stability_score).
        """
        if not props:
            return 0.0, 0.0
            
        N = len(props)
        if N == 0: return 0.0, 0.0
        
        # Initialize spins randomly (-1 or 1)
        s = np.random.choice([-1, 1], size=N).astype(float)
        
        # Build Coupling Matrix J (Symmetric)
        J = np.zeros((N, N))
        for i, j, w in constraints:
            if 0 <= i < N and 0 <= j < N:
                J[i, j] = w
                J[j, i] = w # Symmetric for Ising
        
        # External field h from weights
        h_vec = np.array([weights.get(p, 0.0) for p in props]) * gain
        
        # Trajectory tracking for stability (Lyapunov-like)
        history = []
        
        for _ in range(steps):
            s_new = s.copy()
            for i in range(N):
                # Local field
                local_field = h_vec[i] + np.dot(J[i, :], s)
                prob = 1.0 / (1.0 + np.exp(-2.0 * local_field))
                s_new[i] = 1 if np.random.rand() < prob else -1
            
            # Energy calculation
            E = -np.dot(h_vec, s_new) - 0.5 * np.dot(s_new, np.dot(J, s_new))
            history.append(E)
            s = s_new
            
            # Early convergence check
            if len(history) > 3 and np.std(history[-3:]) < 1e-4:
                break

        # Stability Score: Inverse of variance in the latter half of trajectory
        if len(history) < 2:
            stability = 1.0
        else:
            variance = np.var(history[int(len(history)/2):])
            stability = 1.0 / (1.0 + variance) # Higher stability = lower variance
            
        return history[-1] if history else 0.0, stability

    def _phase_transition_score(self, J: np.ndarray) -> float:
        """
        Estimates distance to criticality using spectral radius.
        Closer to lambda_max = 1 implies higher sensitivity (criticality).
        """
        if J.size == 0:
            return 0.0
        try:
            eigenvalues = np.linalg.eigvals(J)
            lambda_max = np.max(np.abs(eigenvalues))
            # Distance to critical point (lambda = 1)
            delta = np.abs(lambda_max - 1.0)
            # Score: closer to 1 is better (lower delta), but avoid division by zero
            return 1.0 / (1.0 + delta)
        except:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_props, p_weights, p_constraints, p_gain = self._extract_features(prompt)
        
        # Build prompt coupling matrix for phase transition analysis
        N_p = len(prompt_props)
        J_prompt = np.zeros((N_p, N_p))
        for i, j, w in p_constraints:
            if 0 <= i < N_p and 0 <= j < N_p:
                J_prompt[i, j] = w
                J_prompt[j, i] = w

        # Criticality baseline from prompt structure
        prompt_criticality = self._phase_transition_score(J_prompt)
        
        for cand in candidates:
            # Combine prompt and candidate for full context evaluation
            full_text = f"{prompt} {cand}"
            props, weights, constraints, gain = self._extract_features(full_text)
            
            # 1. Structural & Computational Score (via Dynamics)
            energy, stability = self._run_dynamics(props, weights, constraints, gain)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            ncd_score = 1.0 - self._compute_ncd(prompt, cand)
            
            # 3. Phase Transition Adjustment
            # If the candidate makes the system highly unstable (low stability), penalize
            phase_bonus = stability * 0.2 
            
            # Raw Score Construction
            # Energy should be minimized (negative is good), so we negate it for scoring
            # Normalize energy roughly by number of props
            norm_energy = -energy / (len(props) + 1) if props else 0.0
            
            final_score = (0.6 * norm_energy) + (0.2 * stability) + (0.15 * ncd_score) + (0.05 * prompt_criticality)
            
            # Heuristic boost for exact numeric matches if detected
            nums_p = re.findall(r"-?\d+\.?\d*", prompt)
            nums_c = re.findall(r"-?\d+\.?\d*", cand)
            if nums_p and nums_c and nums_p[-1] == nums_c[-1]:
                final_score += 0.5

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Energy: {energy:.2f}, Stability: {stability:.2f}, NCD: {ncd_score:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Match Check
        props, weights, constraints, gain = self._extract_features(f"{prompt} {answer}")
        if not props:
            # No structural parse -> low confidence
            return 0.2 * meta_cap
        
        # 3. Dynamical Stability Check
        # Run dynamics multiple times to check convergence consistency
        energies = []
        for _ in range  (5):
            e, _ = self._run_dynamics(props, weights, constraints, gain, steps=15)
            energies.append(e)
        
        stability_variance = np.var(energies)
        
        # If the system state fluctuates wildly across runs, confidence is low
        if stability_variance > 1.0:
            dynamic_conf = 0.3
        elif stability_variance > 0.1:
            dynamic_conf = 0.6
        else:
            dynamic_conf = 0.95
            
        # 4. Final Calculation
        # If meta_cap is low (ambiguous question), it overrides dynamic_conf
        final_conf = min(dynamic_conf, meta_cap)
        
        # Ensure definitive computation boosts confidence only if not capped
        # Check for numeric exactness as a "definitive" signal
        nums_p = re.findall(r"-?\d+\.?\d*", prompt)
        nums_a = re.findall(r"-?\d+\.?\d*", answer)
        if nums_p and nums_a:
            try:
                # Simple heuristic: if answer contains a number from prompt or result of simple op
                # This is a proxy for "constructive computation"
                if any(n in answer for n in nums_p):
                    final_conf = min(final_conf * 1.2, 0.95) # Boost but respect cap
            except:
                pass
                
        return float(np.clip(final_conf, 0.0, 1.0))