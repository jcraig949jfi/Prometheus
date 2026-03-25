import numpy as np
import hashlib
from typing import List, Dict

class ReasoningTool:
    """
    Symbiotic Active Inference Swarm (SAIS) Implementation.
    
    Mechanism:
    1. Holobiont Encoding: Prompts and candidates are hashed into fixed-size vectors 
       representing the 'sensory input' for the swarm.
    2. Microbial Sub-agents: A fixed ensemble of 'sub-agents' (hypothesis testers) 
       exists within each node. Each sub-agent holds a random weight vector.
    3. Active Inference Loop: 
       - Prediction: Sub-agents project their weights onto the candidate vector.
       - Error Calculation: The difference between the candidate's intrinsic value 
         (derived from prompt-candidate semantic overlap via hash intersection) 
         and the prediction generates a 'prediction error'.
       - Free Energy Minimization: Scores are derived from minimizing this error 
         weighted by 'precision' (confidence).
    4. Stigmergy: Successful sub-agents (low free energy) deposit 'digital pheromones' 
       (score boosts) proportional to their precision. Poor performers are attenuated.
    5. Output: Final ranking is a consensus of the swarm's free-energy minimization.
    """

    def __init__(self):
        self.n_features = 64
        self.n_agents = 10
        # Initialize microbial sub-agents with random hypotheses (weights)
        # Deterministic seed for reproducibility if needed, but random is fine for diversity
        rng = np.random.default_rng(42) 
        self.agents = rng.standard_normal((self.n_agents, self.n_features))
        # Precision (confidence) for each agent, initialized to 1.0
        self.precisions = np.ones(self.n_agents)

    def _hash_to_vector(self, text: str) -> np.ndarray:
        """Convert string to a deterministic normalized vector."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        # Convert hex to bytes, then to int array
        vals = np.array([int(b) for b in bytes.fromhex(h)], dtype=np.float64)
        # Resize to n_features by averaging blocks if necessary
        if len(vals) > self.n_features:
            vals = vals[:self.n_features]
        else:
            vals = np.pad(vals, (0, self.n_features - len(vals)), mode='wrap')
        # Normalize to [-1, 1]
        vals = (vals / 128.0) - 1.0
        return vals

    def _compute_intrinsic_truth(self, prompt: str, candidate: str) -> float:
        """
        Simulate 'ground truth' signal based on semantic overlap.
        In a real system, this would be external validation. 
        Here, we use hash intersection similarity as a proxy for 'fit'.
        """
        p_vec = self._hash_to_vector(prompt)
        c_vec = self._hash_to_vector(candidate)
        # Cosine-like similarity as a proxy for hypothesis fit
        num = np.dot(p_vec, c_vec)
        denom = np.linalg.norm(p_vec) * np.linalg.norm(c_vec) + 1e-9
        return (num / denom + 1.0) / 2.0  # Scale to 0-1

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_vec = self._hash_to_vector(prompt)
        
        for cand in candidates:
            c_vec = self._hash_to_vector(cand)
            
            # 1. Parallel Epistemic Foraging: Agents predict based on candidate
            # Prediction = dot product of agent weights and candidate features
            predictions = np.dot(self.agents, c_vec)
            
            # 2. Active Inference: Calculate Prediction Error
            # Target is approximated by the alignment between prompt and candidate
            target_signal = np.dot(p_vec, c_vec) / (np.linalg.norm(p_vec) * np.linalg.norm(c_vec) + 1e-9)
            target_signal = (target_signal + 1.0) / 2.0 # Normalize to 0-1 range roughly
            
            # Error: Difference between agent prediction (scaled) and target
            # We treat the target_signal as the 'sensory input' the agents try to predict
            errors = target_signal - (predictions + 1.0) / 2.0
            
            # 3. Free Energy Minimization
            # Free Energy ~ -0.5 * precision * error^2 (simplified)
            # We want to minimize free energy, so high error = low score
            free_energy = -0.5 * self.precisions * (errors ** 2)
            
            # 4. Stigmergic Update & Consensus
            # Total free energy reduction potential (sum of agent contributions)
            # Agents with high precision and low error contribute most
            swarm_score = np.sum(free_energy)
            
            # Normalize score to 0-1 range loosely based on magnitude
            # Max theoretical free energy reduction is 0, min is negative
            # We invert and scale: higher (less negative) is better
            normalized_score = 1.0 / (1.0 + np.exp(-swarm_score * 10)) # Sigmoid
            
            # Update precisions (Metacognition): 
            # Increase precision for agents with low error (successful hypotheses)
            # This mimics endosymbiotic selection
            learning_rate = 0.1
            self.precisions *= np.exp(-0.5 * (errors ** 2) * learning_rate)
            self.precisions = np.clip(self.precisions, 0.1, 10.0) # Prevent collapse/explosion

            results.append({
                "candidate": cand,
                "score": float(normalized_score),
                "reasoning": f"Swarm consensus via free-energy minimization. Precision-weighted error: {np.mean(np.abs(errors)):.4f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the swarm's precision-weighted agreement.
        """
        p_vec = self._hash_to_vector(prompt)
        a_vec = self._hash_to_vector(answer)
        
        # Re-calculate swarm state for this specific pair
        predictions = np.dot(self.agents, a_vec)
        target_signal = np.dot(p_vec, a_vec) / (np.linalg.norm(p_vec) * np.linalg.norm(a_vec) + 1e-9)
        target_signal = (target_signal + 1.0) / 2.0
        
        errors = target_signal - (predictions + 1.0) / 2.0
        
        # Confidence is the weighted average of certainty
        # High precision + low error = high confidence
        weighted_certainty = np.sum(self.precisions * np.exp(-errors**2))
        total_precision = np.sum(self.precisions)
        
        if total_precision == 0:
            return 0.5
            
        # Normalize to 0-1
        conf = weighted_certainty / total_precision
        return float(np.clip(conf, 0.0, 1.0))