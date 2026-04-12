import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Neuromodulatory Gain, and Falsificationism.
    
    Mechanism:
    1. Representation: The latent truth state 'x' is a binary vector of elementary propositions.
    2. Observation: Text is parsed into feature vectors 'y' encoding negations, comparatives, and causality.
    3. Dynamics: A Kalman Filter updates belief (mu, Sigma) over 'x'.
    4. Neuromodulation: Observation noise 'R' is dynamically scaled by current uncertainty (trace(Sigma)),
       mimicking dopamine-mediated learning rates (high uncertainty -> high gain).
    5. Scoring: Candidates are scored by posterior sharpness (-log det Sigma) and 
       Falsification Score (sum of squared innovations). High innovation = strong evidence against hypothesis.
    6. Epistemic Honesty: Meta-analysis detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        self.d = 20  # Dimension of latent proposition space
        self.m = 10  # Dimension of feature space
        self.H = self._build_projection_matrix()
        self.alpha = 2.0  # Neuromodulatory sensitivity
        self.R0 = np.eye(self.m) * 0.5  # Base observation noise
        self.lambda_fals = 0.5  # Weight for falsification score

    def _build_projection_matrix(self) -> np.ndarray:
        """Creates a random but fixed projection matrix H mapping propositions to features."""
        np.random.seed(42)
        return np.random.randn(self.m, self.d)

    def _extract_features(self, text: str) -> np.ndarray:
        """
        Parses text into a feature vector y.
        Handles negations, comparatives, numbers, and structural markers.
        """
        y = np.zeros(self.m)
        text_lower = text.lower()
        
        # 1. Negation features (Sign flip logic encoded as negative activation)
        negations = ["not", "no", "never", "none", "neither", "without"]
        if any(w in text_lower for w in negations):
            y[0] = -1.0  # Negation flag
            
        # 2. Comparative features
        comparatives = ["greater", "less", "more", "fewer", "before", "after"]
        if any(w in text_lower for w in comparatives):
            y[1] = 1.0
            
        # 3. Causal/Conditional features
        if any(w in text_lower for w in ["because", "therefore", "if", "then", "unless"]):
            y[2] = 1.0
            
        # 4. Numeric magnitude (simplified)
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if numbers:
            try:
                val = float(numbers[0])
                y[3] = np.tanh(val / 10.0)  # Normalize magnitude
                if len(numbers) > 1:
                    diff = float(numbers[1]) - val
                    y[4] = np.tanh(diff / 10.0)
            except ValueError:
                pass

        # 5. Quantifiers
        if any(w in text_lower for w in ["all", "every", "some", "any"]):
            y[5] = 1.0
            
        # 6. Length/Complexity proxy
        y[6] = np.tanh(len(text) / 100.0)
        
        return y

    def _run_kalman_filter(self, prompt: str, candidate: str) -> Tuple[float, float, np.ndarray]:
        """
        Executes the Kalman Predict-Update cycle with Neuromodulatory Gain.
        Returns: (falsification_score, posterior_uncertainty, innovations)
        """
        # Initialize State: Max uncertainty
        mu = 0.5 * np.ones(self.d)
        Sigma = np.eye(self.d)
        
        # Combine prompt and candidate as the "evidence stream"
        # We treat the prompt as context (t=0) and candidate as hypothesis (t=1)
        # In a full sequence, we would tokenize sentence by sentence.
        # Here we simulate a sequence: [Prompt Context, Candidate Assertion]
        sentences = [prompt, candidate]
        
        total_falsification = 0.0
        innovations_log = []

        for i, sentence in enumerate(sentences):
            y_t = self._extract_features(sentence)
            
            # 1. Predict (Static state assumption)
            mu_hat = mu.copy()
            Sigma_hat = Sigma.copy()
            
            # 2. Neuromodulatory Gain
            # Uncertainty u_t = trace(Sigma)
            u_t = np.trace(Sigma_hat)
            # Gain g_t = sigmoid(alpha * u_t)
            g_t = 1.0 / (1.0 + np.exp(-self.alpha * u_t))
            # Inflate noise: R_t = R0 / g_t^2 
            # (High uncertainty -> high gain -> small effective noise -> large update step)
            R_t = self.R0 / (g_t ** 2 + 1e-6)
            
            # 3. Update
            epsilon_t = y_t - self.H @ mu_hat  # Innovation
            S_t = self.H @ Sigma_hat @ self.H.T + R_t  # Innovation covariance
            
            try:
                S_inv = np.linalg.inv(S_t)
                K_t = Sigma_hat @ self.H.T @ S_inv  # Kalman Gain
                mu = mu_hat + K_t @ epsilon_t
                Sigma = (np.eye(self.d) - K_t @ self.H) @ Sigma_hat
            except np.linalg.LinAlgError:
                # Fallback if singular
                mu = mu_hat
                Sigma = Sigma_hat

            # Accumulate Falsification Score (Squared Mahalanobis distance approx)
            # Using simple Euclidean norm of innovation for stability in low-dim
            inst_fals = np.dot(epsilon_t, epsilon_t)
            total_falsification += inst_fals
            innovations_log.append(inst_fals)

        # Posterior Uncertainty: -log det(Sigma) (Information gain)
        try:
            log_det = np.linalg.slogdet(Sigma)[1]
            uncertainty_score = -log_det
        except:
            uncertainty_score = 0.0
            
        return total_falsification, uncertainty_score, np.array(innovations_log)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "have you quit", "why did", "when did", "how often did"]
        if any(t in p for t in presupposition_triggers):
            # Check if it implies a past event that might not exist
            if "stopped" in p or "quit" in p or "fail" in p:
                return 0.25

        # 2. Scope/Pronoun Ambiguity
        if re.search(r"\b(every|all)\s+\w+\s+\w+\s+a\s+\w+", p):
            # "Every X did a Y" ambiguity
            return 0.4 
        if re.search(r"\b(told|said|asked)\s+\w+\s+he\s+", p) and "who" in p:
            return 0.3

        # 3. False Dichotomy
        if "either" in p and "or" in p and "possible" not in p:
            # Heuristic: if it forces a choice without "possibly"
            if re.search(r"either\s+\w+\s+or\s+\w+", p):
                return 0.5 # Moderate penalty, depends on context

        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly", "moral"]
        if any(w in p for w in subjective_words):
            if "measure" not in p and "data" not in p:
                return 0.4

        # 5. Unanswerability (Missing info)
        if "calculate" in p or "solve" in p:
            if not re.search(r"\d", p): # No numbers to calculate with
                return 0.2
        
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate NCD for tie-breaking (max 15% influence logic handled in scoring)
        prompt_len = len(prompt)
        
        for cand in candidates:
            # Run Kalman-Falsification engine
            fals_score, unc_score, _ = self._run_kalman_filter(prompt, cand)
            
            # Structural Score: Based on how well the candidate reduces uncertainty
            # We want low uncertainty (high info) but also consistent falsification of WRONG hypotheses.
            # However, the prompt says: "Large innovations... successful attempts to falsify".
            # If the candidate IS the hypothesis, large innovations means the prompt contradicts it.
            # So for the CORRECT candidate, we expect LOW innovations (consistent with prompt).
            # Wait, the algorithm description says: "score = -log det + lambda * S_fals".
            # And "Lower score -> better answer".
            # If S_fals is high, the hypothesis was contradicted (bad).
            # So we want LOW S_fals (consistency) and LOW -log det (high certainty/sharp posterior).
            
            raw_score = unc_score + self.lambda_fals * fals_score
            
            # NCD Tiebreaker (Small influence)
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to be comparable scale (approx)
            ncd_penalty = ncd_val * 0.5 
            
            final_score = raw_score + ncd_penalty
            
            results.append({
                "candidate": cand,
                "score": -final_score, # Invert so higher is better
                "reasoning": f"Uncertainty: {unc_score:.2f}, Falsification: {fals_score:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Confidence
        # Run the filter to see how consistent the answer is
        fals, unc, innovations = self._run_kalman_filter(prompt, answer)
        
        # If innovations are huge, the answer contradicts the prompt -> Low confidence
        # If uncertainty remains high, the answer doesn't resolve the state -> Low confidence
        consistency = 1.0 / (1.0 + fals)  # Map falsification to 0-1
        certainty = 1.0 / (1.0 + np.exp(unc)) # Map uncertainty to 0-1
        
        # Base confidence from model
        base_conf = 0.6 * consistency + 0.4 * certainty
        
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Ensure strict bounds
        return float(np.clip(final_conf, 0.0, 1.0))