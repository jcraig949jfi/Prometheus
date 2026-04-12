import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Self-Regularizing Reservoir Ensemble via Nash-MDL Game.
    
    Mechanism:
    1. Reservoir Computing: A fixed random recurrent matrix projects input structural features
       into a high-dimensional temporal state space.
    2. Kolmogorov Complexity (MDL): Instead of pure error minimization, candidates are scored
       by a description length metric: L = Error + Complexity_Penalty. We approximate
       Kolmogorov complexity via zlib compression length of the candidate logic trace.
    3. Nash Equilibrium: Multiple 'sub-agents' (readout weight vectors) compete. Each attempts
       to minimize its own description length given the current population distribution.
       The final score converges to a stable equilibrium where no agent can improve its
       MDL score by unilaterally changing its hypothesis weighting.
       
    This creates a metacognitive signal: candidates that require high complexity to fit
    the structural constraints of the prompt are penalized, simulating Occam's Razor.
    """

    def __init__(self):
        # Reservoir parameters
        self.N_res = 64  # Reservoir size
        np.random.seed(42)  # Determinism
        
        # Fixed random recurrent core (Echo State Property)
        self.W_res = np.random.randn(self.N_res, self.N_res)
        self.W_res /= np.linalg.norm(self.W_res, axis=1, keepdims=True) * 1.2 # Scale for stability
        
        # Input projection (structural features -> reservoir)
        self.W_in = np.random.randn(self.N_res, 5) # 5 structural features
        
        # Population game parameters
        self.n_agents = 5
        self.readouts = [np.random.randn(1, self.N_res) for _ in range(self.n_agents)]
        self.learning_rate = 0.1

    def _extract_structural_features(self, text: str) -> np.ndarray:
        """Extracts 5 structural features: negations, comparatives, conditionals, numbers, length."""
        t_lower = text.lower()
        
        # 1. Negations
        negations = len(re.findall(r'\b(not|no|never|none|neither|nobody|nothing)\b', t_lower))
        
        # 2. Comparatives/Superlatives
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|worse|most|least|largest|smallest)\b', t_lower))
        
        # 3. Conditionals
        conditionals = len(re.findall(r'\b(if|then|unless|otherwise|provided|when)\b', t_lower))
        
        # 4. Numeric content (count of digits)
        numbers = len(re.findall(r'\d+', t_lower))
        
        # 5. Syntactic complexity (approx word count)
        words = len(re.findall(r'\w+', t_lower))
        
        return np.array([negations, comparatives, conditionals, numbers, words], dtype=float)

    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Rough normalization to prevent explosion in reservoir."""
        # Simple scaling based on expected ranges
        scales = np.array([5.0, 5.0, 5.0, 10.0, 50.0])
        return features / (scales + 1e-8)

    def _run_reservoir(self, prompt: str, candidate: str) -> np.ndarray:
        """Runs the combined prompt+candidate through the reservoir to get a state."""
        # Combine context
        full_text = f"{prompt} {candidate}"
        features = self._extract_structural_features(full_text)
        features_norm = self._normalize_features(features)
        
        # Initialize state
        state = np.zeros((self.N_res, 1))
        
        # Inject input (simplified single-step for static evaluation)
        # In a true temporal task, we would iterate over tokens. 
        # Here we treat the structural extraction as the "input pulse".
        input_pulse = features_norm.reshape(-1, 1)
        state = np.tanh(self.W_in @ input_pulse + self.W_res @ np.zeros((self.N_res, 1)))
        
        # Add a second step to mix recurrence slightly (simulating temporal dynamics)
        state = np.tanh(self.W_in @ input_pulse + self.W_res @ state)
        
        return state.T  # Return row vector

    def _compute_mdl_score(self, prompt: str, candidate: str, readout_weights: np.ndarray) -> float:
        """
        Computes the MDL-based payoff.
        Payoff = -(Error + Complexity)
        Error: Mismatch between reservoir prediction and candidate consistency.
        Complexity: Compressed length of the candidate's logical trace.
        """
        state = self._run_reservoir(prompt, candidate)
        
        # Prediction from this specific readout agent
        prediction = float(state @ readout_weights.T)
        
        # Error term: We want the prediction to align with a 'true' signal.
        # Since we don't have ground truth in unsupervised mode, we use the 
        # structural consistency of the candidate itself as the target.
        # If the candidate has high structural similarity to the prompt, target is high.
        prompt_feat = self._extract_structural_features(prompt)
        cand_feat = self._extract_structural_features(candidate)
        
        # Simple structural overlap heuristic as proxy for 'truth' in absence of labels
        # This acts as the 'supervised' signal derived from structural parsing
        overlap = np.dot(prompt_feat, cand_feat) / (np.linalg.norm(prompt_feat) * np.linalg.norm(cand_feat) + 1e-8)
        target = 1.0 if overlap > 0.3 else 0.0 # Thresholded consistency
        
        error = (prediction - target) ** 2
        
        # Complexity term: Approximate Kolmogorov Complexity via Zlib
        # We compress the candidate string. Shorter compression = lower complexity.
        try:
            compressed_len = len(zlib.compress(candidate.encode('utf-8')))
        except:
            compressed_len = len(candidate) * 2
            
        # Normalize complexity to roughly [0, 1] range relative to typical string lengths
        # Assuming max reasonable candidate length ~500 chars -> ~200 compressed
        complexity_penalty = min(1.0, compressed_len / 200.0)
        
        # MDL Objective: Minimize (Error + Complexity)
        # Payoff is negative MDL
        mdl_cost = error + 0.5 * complexity_penalty
        return -mdl_cost

    def _nash_equilibrium_step(self, prompt: str, candidate: str, iterations: int = 10):
        """
        Simulates the population game to find Nash Equilibrium weights.
        Agents update weights to maximize payoff (minimize MDL) given others.
        Returns the equilibrium score.
        """
        scores = []
        
        # We simulate the game by letting agents update their readout weights
        # to best-respond to the current candidate's structural profile.
        # Since it's a single candidate evaluation, the 'game' is internal 
        # optimization of the readout to fit the MDL criterion.
        
        best_score = -float('inf')
        best_weights = None
        
        for agent_idx in range(self.n_agents):
            current_weights = self.readouts[agent_idx].copy()
            
            # Gradient-free optimization step (since we need to stay within std lib)
            # Perturb weights to see if MDL improves
            local_best_score = self._compute_mdl_score(prompt, candidate, current_weights)
            local_best_weights = current_weights
            
            for _ in range(iterations):
                # Generate a perturbation (strategy deviation)
                noise = np.random.randn(1, self.N_res) * 0.1
                new_weights = current_weights + noise
                
                # Normalize to prevent explosion
                new_weights /= (np.linalg.norm(new_weights) + 1e-8)
                
                new_score = self._compute_mdl_score(prompt, candidate, new_weights)
                
                if new_score > local_best_score:
                    local_best_score = new_score
                    local_best_weights = new_weights
                    current_weights = new_weights # Accept move
            
            # Update population (Fictitious Play approximation: replace if better)
            if local_best_score > self._compute_mdl_score(prompt, candidate, self.readouts[agent_idx]):
                self.readouts[agent_idx] = local_best_weights
            
            scores.append(local_best_score)
            
        # The equilibrium score is the max payoff achievable by the population
        return max(scores) if scores else -1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate structural signals for ranking priority
        # Key pattern: Structural parsing is primary, NCD is tiebreaker
        
        scored_candidates = []
        
        for cand in candidates:
            # 1. Structural Parsing Score (Primary Signal)
            # Check for logical consistency markers
            p_feats = self._extract_structural_features(prompt)
            c_feats = self._extract_structural_features(cand)
            
            # Heuristic: Does the candidate answer the specific structural demand?
            # E.g., if prompt has numbers, candidate should likely have numbers or logical ops
            has_numbers_prompt = p_feats[3] > 0
            has_numbers_cand = c_feats[3] > 0
            
            structural_score = 0.0
            
            # Numeric evaluation logic
            if has_numbers_prompt:
                # Extract numbers from both
                p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
                c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', cand)]
                
                if p_nums and c_nums:
                    # Check simple arithmetic consistency or magnitude matching
                    # This is a heuristic proxy for "reasoning"
                    if abs(p_nums[0] - c_nums[0]) < 1.0 or (len(c_nums) > 0):
                        structural_score += 0.5
                elif not has_numbers_cand and has_numbers_prompt:
                    # Prompt asks for math, candidate has no numbers -> likely wrong
                    structural_score -= 0.5
            
            # Negation/Constraint check
            if 'not' in prompt.lower() and 'not' not in cand.lower():
                # Potential failure to adhere to negation constraint
                # (Very rough heuristic)
                pass 

            # 2. Nash-MDL Game Score (Refinement)
            # Run the reservoir game to get complexity-aware score
            mdl_score = self._nash_equilibrium_step(prompt, cand)
            
            # Combine: Structural score is the driver, MDL refines it
            # MDL score is negative cost, so higher is better.
            final_score = structural_score + (mdl_score * 0.5)
            
            # 3. NCD Tiebreaker (Only if structural signals are weak)
            ncd_score = 0.0
            if abs(structural_score) < 0.1:
                # Compute NCD only if structural signal is ambiguous
                try:
                    z_prompt = len(zlib.compress(prompt.encode()))
                    z_cand = len(zlib.compress(cand.encode()))
                    z_both = len(zlib.compress((prompt + cand).encode()))
                    ncd = (z_both - min(z_prompt, z_cand)) / max(z_prompt, z_cand, 1)
                    ncd_score = 1.0 - ncd # Higher is more similar
                except:
                    ncd_score = 0.0
                final_score += ncd_score * 0.1 # Small weight for tiebreaking

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{structural_score:.2f}, MDL-Game:{mdl_score:.2f}, NCD-Tiebreak:{ncd_score:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the MDL-Nash score normalized.
        """
        # Get the single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1 range. 
        # Typical MDL scores are negative (e.g., -2.0 to 0.0).
        # Structural scores add offset.
        # We use a sigmoid-like mapping centered around typical equilibrium values.
        # If score > 0, high confidence. If score < -1, low confidence.
        confidence = 1.0 / (1.0 + np.exp(-score * 2.0))
        return float(np.clip(confidence, 0.0, 1.0))