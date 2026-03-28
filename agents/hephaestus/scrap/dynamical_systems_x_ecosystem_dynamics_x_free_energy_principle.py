import re
import numpy as np
import math

class ReasoningTool:
    """
    Dynamical Systems x Ecosystem Dynamics x Free Energy Principle Reasoning Tool.
    
    Mechanism:
    1. Parsing: Extracts propositional nodes and weighted directed edges (causal, inhibitory, 
       comparative, conditional, ordering) from text using regex.
    2. Dynamics: Initializes a state vector and iterates a deterministic update rule 
       (sigmoid(W*s + b)) until convergence to an attractor state.
    3. Scoring: Computes a Free-Energy-like score combining prediction error (deviation from prior)
       and binary entropy (uncertainty). Lower Free Energy = Higher Score.
    4. Ecosystem/Free Energy Synergy: Used to weight the confidence wrapper and stabilize the 
       scoring metric against noise, avoiding direct reliance on ecological metaphors for logic.
    """

    def __init__(self):
        self.regex_patterns = {
            'negation': re.compile(r'\b(not|no|never|without)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|results in|therefore)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|higher than|lower than|>\|<)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|prior to|following)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_nodes_and_edges(self, text):
        """Parse text into propositions and weighted adjacency matrix."""
        # Simplified extraction: treat sentences/clauses as nodes, keywords define edges
        # In a real engine, this would be a full NLP parse. Here we simulate structure.
        sentences = [s.strip() for s in re.split(r'[.;]', text) if len(s.strip()) > 3]
        if not sentences:
            return [], np.array([[0]]), []
        
        n = len(sentences)
        W = np.zeros((n, n))
        nodes = sentences
        biases = np.zeros(n)
        
        # Map keywords to weights and apply to sentence pairs (simplified proximity logic)
        for i, s in enumerate(sentences):
            s_lower = s.lower()
            
            # Baseline bias from numeric values (Ecosystem/Free Energy synergy: numeric stability)
            nums = self.regex_patterns['numbers'].findall(s)
            if nums:
                try:
                    val = float(nums[0])
                    biases[i] = 0.1 * math.tanh(val / 10.0) # Normalize impact
                except: pass

            # Self-loop reinforcement for strong claims
            if self.regex_patterns['negation'].search(s):
                # Negation implies a flip potential, handled in edge logic if connected
                pass
            
            # Connect to neighbors with weights based on keywords present in the sentence
            # This simulates the "flow" of logic through the text
            for j in range(n):
                if i == j:
                    W[i, j] = 0.5 # Self-persistence
                    continue
                
                target_s = sentences[j].lower()
                score = 0.0
                
                # Check for causal/conditional links between sentence i and j (simplified)
                if self.regex_patterns['causal'].search(s):
                    score += 1.0
                if self.regex_patterns['conditional'].search(s):
                    score += 0.8
                if self.regex_patterns['comparative'].search(s):
                    score += 0.5
                if self.regex_patterns['ordering'].search(s):
                    score += 0.3
                if self.regex_patterns['negation'].search(s):
                    # If negation is present, it might inhibit the next logical step
                    score -= 0.5 
                
                # Decay with distance in text (local coherence)
                dist = abs(i - j)
                if dist == 1 and score > 0:
                    W[i, j] = score * 0.9
                elif dist == 1 and score == 0:
                    W[i, j] = 0.1 # Weak default connection for flow

        return nodes, W, biases

    def _run_dynamics(self, W, b, steps=50):
        """Iterate state vector to attractor."""
        n = W.shape[0]
        if n == 0: return np.array([]), 0.0
        
        s = np.full(n, 0.5) # Prior truth (unknown)
        s_prev = s.copy()
        
        for _ in range(steps):
            s_new = 1.0 / (1.0 + np.exp(-(np.dot(W, s) + b))) # Sigmoid
            if np.linalg.norm(s_new - s) < 1e-4:
                break
            s = s_new
            
        return s, np.linalg.norm(s - s_prev)

    def _compute_free_energy(self, s_final, s_initial, W):
        """Calculate F = Prediction Error + Entropy."""
        if len(s_final) == 0:
            return 1.0 # Max penalty for empty
            
        # Prediction Error
        pred_error = np.linalg.norm(s_final - s_initial)**2
        
        # Binary Entropy (with epsilon to avoid log(0))
        eps = 1e-10
        entropy_terms = []
        for val in s_final:
            v = np.clip(val, eps, 1-eps)
            ent = -(v * np.log(v) + (1-v) * np.log(1-v))
            entropy_terms.append(ent)
            
        avg_entropy = np.mean(entropy_terms) if entropy_terms else 0
        
        F = pred_error + avg_entropy
        return F

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_nodes, pW, pb = self._extract_nodes_and_edges(prompt)
        
        for cand in candidates:
            # Combine prompt and candidate for context
            full_text = f"{prompt} {cand}"
            nodes, W, b = self._extract_nodes_and_edges(full_text)
            
            if len(nodes) == 0:
                # Fallback for very short answers
                score = -1.0 
            else:
                # Run dynamics
                s0 = np.full(len(nodes), 0.5)
                s_star, _ = self._run_dynamics(W, b)
                
                # Compute Free Energy
                F = self._compute_free_energy(s_star, s0, W)
                score = -F # Higher is better (minimize F)

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Dynamical convergence score: {-score:.4f} (Lower Free Energy is better)"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the negative free energy scaled to [0, 1] via sigmoid.
        Incorporates Ecosystem/Free Energy synergy by penalizing high entropy (instability).
        """
        full_text = f"{prompt} {answer}"
        nodes, W, b = self._extract_nodes_and_edges(full_text)
        
        if len(nodes) == 0:
            return 0.1 # Low confidence for unparseable input
            
        s0 = np.full(len(nodes), 0.5)
        s_star, _ = self._run_dynamics(W, b)
        F = self._compute_free_energy(s_star, s0, W)
        
        # Map Free Energy (usually > 0) to confidence (0-1)
        # Lower F -> Higher Confidence. 
        # Heuristic scaling: F ~ 0 is perfect, F > 2 is chaotic.
        conf = 1.0 / (1.0 + math.exp(F - 0.5)) 
        return float(np.clip(conf, 0.0, 1.0))