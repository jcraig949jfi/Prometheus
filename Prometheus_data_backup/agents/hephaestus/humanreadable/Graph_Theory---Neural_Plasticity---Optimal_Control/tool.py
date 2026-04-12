import math
import hashlib

class ReasoningTool:
    """
    Plasticity-Guided Optimal Graph Neural Network (PO-GNN) Approximation.
    
    Mechanism:
    1. Graph Construction: Nodes are hypothesis states derived from text hashes.
       Edges represent inferential relationships based on semantic overlap (Jaccard-like).
    2. Neural Plasticity: Edge weights evolve via a Hebbian rule: delta_w = eta * pre * post - lambda * w.
       Here, 'pre' and 'post' are activation levels derived from candidate relevance to the prompt.
    3. Optimal Control: 
       - Cost J includes prediction error (relevance), sparsity (L0 approx via thresholding), 
         and smoothness (penalizing large weight swings).
       - We approximate Pontryagin's Minimum Principle by dynamically adjusting learning rate (eta)
         and decay (lambda) to minimize a discrete cost function at each step.
       - High error increases eta (exploration); high complexity increases lambda (pruning).
    4. Metacognition: The system monitors the variance in candidate scores to adjust confidence.
    """

    def __init__(self):
        # State: Graph nodes (hypotheses) and edges (weights)
        self.nodes = {}  # id -> activation
        self.edges = {}  # (id1, id2) -> weight
        self.time = 0
        
        # Control parameters (initially fixed, then modulated)
        self.eta_base = 0.1   # Base learning rate
        self.lambda_base = 0.05 # Base decay
        self.alpha = 0.1      # Sparsity penalty
        self.beta = 0.05      # Smoothness penalty

    def _hash_node(self, text):
        """Deterministic ID generation for text."""
        return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)

    def _activate(self, prompt, candidate):
        """Compute initial activation based on simple token overlap (semantic proxy)."""
        p_tokens = set(prompt.lower().split())
        c_tokens = set(candidate.lower().split())
        if not p_tokens or not c_tokens:
            return 0.0
        overlap = len(p_tokens & c_tokens)
        union = len(p_tokens | c_tokens)
        return overlap / union if union > 0 else 0.0

    def _update_plasticity(self, prompt, candidates):
        """
        Apply Hebbian plasticity and Optimal Control constraints.
        Updates edge weights based on current activations and cost minimization.
        """
        # 1. Compute Activations (Pre/Post synapses)
        c_ids = []
        activations = {}
        for cand in candidates:
            nid = self._hash_node(cand)
            act = self._activate(prompt, cand)
            # Add prompt influence as a global bias node
            activations[nid] = act
            c_ids.append(nid)
        
        prompt_id = self._hash_node(prompt)
        activations[prompt_id] = 1.0 # Prompt is always fully active
        c_ids.append(prompt_id)

        # Initialize nodes if new
        for nid in c_ids:
            if nid not in self.nodes:
                self.nodes[nid] = 0.0
            self.nodes[nid] = activations.get(nid, 0.0)

        # 2. Optimal Control: Adjust hyperparameters based on system state
        # If total activity is low, increase eta (exploration). If high, increase lambda (pruning).
        total_act = sum(activations.values())
        dynamic_eta = self.eta_base * (1.0 / (total_act + 0.1))
        dynamic_lambda = self.lambda_base * (total_act * 2.0)

        # 3. Update Edges (Hebbian + Control)
        # Create fully connected graph among candidates for this step (simplified inference graph)
        current_edges = set()
        for i, n1 in enumerate(c_ids):
            for n2 in c_ids[i+1:]:
                if n1 == n2: continue
                
                edge = (min(n1, n2), max(n1, n2)) # Canonical order
                current_edges.add(edge)
                
                w = self.edges.get(edge, 0.0)
                pre = self.nodes.get(n1, 0.0)
                post = self.nodes.get(n2, 0.0)
                
                # Hebbian term: delta = eta * pre * post
                hebbian = dynamic_eta * pre * post
                
                # Decay term: lambda * w
                decay = dynamic_lambda * w
                
                # Smoothness constraint (approximated): Penalize large jumps from previous weight
                # In continuous time: beta * w_dot^2. Discrete approx: dampen change.
                smoothness_factor = 1.0 - (self.beta * dynamic_eta)
                smoothness_factor = max(0.0, min(1.0, smoothness_factor))
                
                new_w = (w + hebbian - decay) * smoothness_factor
                
                # Sparsity (L0 approx): Prune if below threshold
                if new_w < 0.01: 
                    new_w = 0.0
                
                if new_w > 0:
                    self.edges[edge] = new_w
                elif edge in self.edges:
                    del self.edges[edge]

        # Return scores based on graph connectivity to prompt
        scores = {}
        for cid in c_ids[:-1]: # Exclude prompt node
            score = self.nodes.get(cid, 0.0)
            # Augment score with edge weight to prompt
            edge = (min(cid, prompt_id), max(cid, prompt_id))
            score += self.edges.get(edge, 0.0) * 0.5
            scores[cid] = score
            
        return scores

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # Run plasticity update to refine graph weights
        scores = self._update_plasticity(prompt, candidates)
        
        results = []
        max_score = max(scores.values()) if scores else 1.0
        min_score = min(scores.values()) if scores else 0.0
        span = max_score - min_score if max_score != min_score else 1.0
        
        for cand in candidates:
            nid = self._hash_node(cand)
            raw = scores.get(nid, 0.0)
            # Normalize score 0-1 for ranking
            norm_score = (raw - min_score) / span if span > 0 else 0.5
            
            # Generate reasoning string
            reasoning = f"Graph connectivity: {raw:.4f}. "
            if raw > 0.5:
                reasoning += "Strong Hebbian association with prompt context."
            elif raw > 0.2:
                reasoning += "Moderate inferential path found; weights stabilizing."
            else:
                reasoning += "Weak connection; subject to synaptic pruning."
                
            results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimates confidence by simulating the graph state if this answer were added.
        Returns 0-1 based on consistency with current graph structure.
        """
        # Temporarily evaluate to get internal score
        # We treat the single answer as a candidate list of one
        temp_results = self.evaluate(prompt, [answer])
        if not temp_results:
            return 0.0
            
        base_score = temp_results[0]["score"]
        
        # Metacognitive check: 
        # If the graph has many strong edges, we trust the score more.
        # If the graph is sparse (few edges), uncertainty is higher.
        edge_density = len(self.edges) / (max(1, len(self.nodes)**2))
        
        # Confidence is a function of base score and structural certainty
        conf = base_score * (0.5 + 0.5 * math.tanh(edge_density * 10))
        return float(min(1.0, max(0.0, conf)))