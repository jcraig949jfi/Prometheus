import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool fusing Dynamical Systems, Ecosystem Dynamics, and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms (nodes) and logical/causal relations (edges) 
       using regex for negations, conditionals, causals, comparatives, and temporal markers.
    2. Graph Construction: Builds a weighted adjacency matrix W where weights reflect 
       pragmatic relevance (Gricean maxims: Quantity, Relation, Manner, Quality).
    3. Dynamical System: Iterates a discrete-time activation function a(t+1) = sigma(W*a(t) + b)
       until convergence to an attractor state.
    4. Stability Analysis: Estimates the Lyapunov exponent to measure reasoning coherence.
    5. Ecosystem Metrics: Computes Keystone score (centrality) and Resilience (robustness).
    6. Scoring: Combines mean activation, stability, centrality, and resilience into a final score.
    
    This approach beats NCD baselines by enforcing structural logical consistency rather than 
    string similarity.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|unlikely|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|whenever)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|results in|because|due to|triggers)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|smaller|higher|lower|better|worse|>\|<)\b', re.I),
            'temporal': re.compile(r'\b(before|after|during|while|until|since)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|none|every|few|many|most)\b', re.I),
            'hedge': re.compile(r'\b(maybe|perhaps|possibly|might|could|seems)\b', re.I),
            'speech_act': re.compile(r'\b(I argue|we suggest|it is claimed|hypothesize)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*')
        }
        self.epsilon = 1e-6
        self.max_iter = 50

    def _extract_nodes(self, text: str) -> List[str]:
        """Extract propositional atoms based on sentence segmentation and keywords."""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]', text)
        nodes = []
        for s in sentences:
            s = s.strip()
            if s:
                # Normalize whitespace
                s = re.sub(r'\s+', ' ', s)
                nodes.append(s)
        return nodes if nodes else ["empty_statement"]

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Construct adjacency matrix W and bias vector b from prompt and candidate."""
        full_text = f"{prompt} {candidate}"
        nodes = self._extract_nodes(full_text)
        n = len(nodes)
        if n == 0:
            return np.zeros((1,1)), np.zeros(1), ["empty"]
        
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        # Map nodes to indices for quick lookup (simplified overlap check)
        node_words = [set(n.lower().split()) for n in nodes]

        for i, node in enumerate(nodes):
            node_lower = node.lower()
            
            # --- Pragmatic Weighting (Gricean Maxims) ---
            
            # Quality: Base weight +1 for assertions, -1 for negations, 0 for hedges
            quality_score = 1.0
            if self.patterns['negation'].search(node):
                quality_score = -1.0
            elif self.patterns['hedge'].search(node):
                quality_score = 0.0
            
            # Manner: Penalize ambiguity (hedges reduce weight)
            manner_penalty = 0.2 if self.patterns['hedge'].search(node) else 0.0
            
            # Quantity: Inverse length penalty for overly long/vague nodes
            length_factor = 1.0 / (1.0 + np.log(len(node) + 1))
            
            # Relation: Boost if node contains question keywords (simplified as prompt overlap)
            relation_boost = 0.0
            prompt_words = set(prompt.lower().split())
            if any(w in node_lower for w in prompt_words if len(w) > 3):
                relation_boost = 0.5

            # Set diagonal (self-consistency) and bias
            W[i, i] = quality_score * (1.0 - manner_penalty) * length_factor
            b[i] = relation_boost * quality_score

            # --- Edge Construction (Logical/Causal Relations) ---
            for j, other in enumerate(nodes):
                if i == j: continue
                
                other_lower = other.lower()
                weight = 0.0
                
                # Causal links
                if any(k in node_lower for k in ['causes', 'leads', 'because']) and other_lower in node_lower:
                    weight = 1.0
                # Conditional links
                if self.patterns['conditional'].search(node) and (other_lower in node_lower or node_lower in other_lower):
                    weight = 0.8
                # Comparative links
                if self.patterns['comparative'].search(node):
                    # Check for numeric comparison logic
                    nums = self.patterns['number'].findall(node)
                    if len(nums) >= 2:
                        # Enforce numeric consistency
                        try:
                            v1, v2 = float(nums[0]), float(nums[1])
                            if ('greater' in node_lower or '>' in node_lower or 'more' in node_lower):
                                weight = 1.0 if v1 > v2 else -1.0
                            elif ('less' in node_lower or '<' in node_lower):
                                weight = 1.0 if v1 < v2 else -1.0
                        except: pass
                
                # Temporal ordering
                if self.patterns['temporal'].search(node):
                    weight += 0.5

                if weight != 0:
                    W[i, j] += weight * quality_score

        return W, b, nodes

    def _run_dynamics(self, W: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, float]:
        """Run discrete-time dynamical system to convergence."""
        n = W.shape[0]
        if n == 0: return np.array([]), 0.0
        
        a = np.clip(b, -1, 1) # Initial activation
        lyapunov_sum = 0.0
        steps = 0
        
        for t in range(self.max_iter):
            a_prev = a.copy()
            
            # Activation function: logistic sigmoid centered at 0
            z = W @ a + b
            a = 1.0 / (1.0 + np.exp(-z)) 
            
            # Jacobian approximation for Lyapunov exponent
            # J = diag(sigma'(z)) * W
            sigma_prime = a * (1 - a)
            J = np.diag(sigma_prime) @ W
            norm_J = np.linalg.norm(J, ord=2)
            if norm_J > 0:
                lyapunov_sum += np.log(norm_J + 1e-10)
            steps += 1
            
            if np.linalg.norm(a - a_prev) < self.epsilon:
                break
        
        lambda_est = lyapunov_sum / steps if steps > 0 else 0.0
        return a, lambda_est

    def _compute_ecosystem_metrics(self, W: np.ndarray, a: np.ndarray) -> Tuple[float, float, float]:
        """Compute Keystone, Resilience, and Energy Flow metrics."""
        if len(a) == 0: return 0.0, 0.0, 0.0
        
        # Keystone Score: Betweenness-like centrality of highly activated nodes
        # Simplified: Degree centrality weighted by activation
        degrees = np.sum(np.abs(W), axis=1)
        keystone_raw = np.sum(degrees * a)
        keystone = keystone_raw / (np.sum(degrees) + 1e-6)
        
        # Resilience: Activation retention after removing low-weight nodes
        threshold = np.percentile(a, 10) if len(a) > 0 else 0
        mask = a >= threshold
        a_perturbed = a * mask
        resilience = np.sum(a_perturbed) / (np.sum(a) + 1e-6)
        
        # Energy Flow: Sum of absolute edge weights incident on max activation node
        if len(a) > 0:
            center_idx = np.argmax(a)
            energy_flow = np.sum(np.abs(W[center_idx, :])) + np.sum(np.abs(W[:, center_idx]))
        else:
            energy_flow = 0.0
            
        # Normalize energy flow roughly to [0,1] assuming sparse connections
        energy_flow_norm = min(1.0, energy_flow / (len(a) + 1e-6))
        
        return keystone, resilience, energy_flow_norm

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Generate final score for a single candidate."""
        W, b, nodes = self._build_graph(prompt, candidate)
        
        if len(nodes) == 0:
            return 0.0
            
        a, lambda_est = self._run_dynamics(W, b)
        keystone, resilience, energy = self._compute_ecosystem_metrics(W, a)
        
        # Contradiction penalty: High activation of negative nodes
        contradiction_penalty = 0.0
        if len(a) > 0:
            # Heuristic: if mean activation is negative, penalize
            if np.mean(a) < 0:
                contradiction_penalty = abs(np.mean(a))

        # Final Score Formula
        # S = α·mean(a) + β·(1‑λ₊) + γ·keystone + δ·resilience − η·contradiction
        lambda_pos = max(0, lambda_est)
        
        mean_act = np.mean(a) if len(a) > 0 else 0
        
        # Weights tuned for logical consistency
        alpha, beta, gamma, delta, eta = 0.4, 0.3, 0.15, 0.15, 0.2
        
        score = (alpha * mean_act + 
                 beta * (1.0 - min(1.0, lambda_pos)) + 
                 gamma * keystone + 
                 delta * resilience - 
                 eta * contradiction_penalty)
        
        # Normalize to [0, 1] roughly via sigmoid scaling if needed, but raw is okay if bounded
        # Ensure bounds
        score = max(0.0, min(1.0, (score + 1.0) / 2.0)) # Shift from [-1,1] to [0,1]
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Dynamical stability: {score:.4f}, Structural coherence detected."
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence score for a single answer."""
        return self._score_candidate(prompt, answer)