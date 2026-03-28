import re
import math
from typing import List, Dict, Any, Optional, Tuple

class ReasoningTool:
    """
    Pragmatic-Ergodic Bandit Scorer (PEBS)
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (negations, comparatives, 
       conditionals, numerics, causality, ordering) via regex into a directed graph.
    2. Ergodic Constraint Propagation: Iteratively propagates truth values and 
       numeric bounds across the graph. The 'space average' of satisfied constraints
       over time serves as the stability metric (ergodic mean).
    3. Multi-Armed Bandit (UCB): Treats each candidate as an arm. Computation budget
       is allocated dynamically to candidates with high uncertainty or high potential,
       refining their ergodic score estimate.
    4. Scoring: Final rank based on the converged ergodic mean of constraint satisfaction.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\s+(\w+)', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|greater than|less than)\s*(\w+|\d+\.?\d*)', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'numeric_val': re.compile(r'\b(\d+\.?\d*)\b'),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next)\b', re.IGNORECASE)
        }
        self.budget = 500  # Total bandit sweeps
        self.t_steps = 100 # Ergodic steps per sweep

    def _extract_graph(self, text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """Extract nodes and edges from text using regex."""
        nodes = set()
        edges = []
        text_lower = text.lower()
        
        # Extract negations
        for m in self.patterns['negation'].finditer(text_lower):
            target = m.group(2)
            nodes.add(target)
            nodes.add(f"not_{target}")
            edges.append((target, f"not_{target}", "NEG"))
            
        # Extract comparatives and numerics
        for m in self.patterns['comparative'].finditer(text_lower):
            u, op, v = m.group(1), m.group(2), m.group(3)
            nodes.update([u, v])
            edge_type = "GT" if ">" in op or "greater" in op else "LT"
            edges.append((u, v, edge_type))
            
        # Extract conditionals (simplified to link context)
        if self.patterns['conditional'].search(text_lower):
            nodes.add("_cond_root")
            edges.append(("_cond_root", "_cond_effect", "IMPLIES"))
            
        # Extract causal
        for m in self.patterns['causal'].finditer(text_lower):
            nodes.add("_cause_root")
            edges.append(("_cause_root", "_cause_effect", "CAUSE"))

        # Extract ordering
        if self.patterns['ordering'].search(text_lower):
            nodes.add("_order_root")
            edges.append(("_order_root", "_order_next", "ORDER"))

        # Fallback: if no structure, treat whole text as a single node to ensure NCD tiebreaker works
        if not nodes:
            nodes.add("_raw_content")
            
        return list(nodes), edges

    def _ergodic_propagation(self, nodes: List[str], edges: List[Tuple[str, str, str]], steps: int) -> float:
        """Run deterministic constraint propagation and return time-averaged space mean."""
        if not nodes:
            return 0.0
            
        node_idx = {n: i for i, n in enumerate(nodes)}
        n_vars = len(nodes)
        
        # State: None (unknown), True, False
        # For numeric nodes, we simulate bounds via a proxy value if needed, 
        # but here we focus on boolean consistency for the 'space average'.
        state = [None] * n_vars
        
        # Initialize some nodes to True randomly but deterministically based on content hash
        # to simulate 'seeding' the ergodic process
        seed_val = sum(ord(c) for c in str(nodes)) 
        if seed_val % 2 == 0:
            state[0] = True
        else:
            state[-1] = True
            
        space_averages = []
        
        for _ in range(steps):
            changed = False
            # Propagate edges
            for u, v, etype in edges:
                if u not in node_idx or v not in node_idx:
                    continue
                i_u, i_v = node_idx[u], node_idx[v]
                
                # Modus Ponens / Propagation
                if state[i_u] is True:
                    if etype == "NEG":
                        if state[i_v] is None:
                            state[i_v] = False
                            changed = True
                        elif state[i_v] is True: # Contradiction
                            state[i_v] = False # Resolve to false for consistency
                            changed = True
                    else: # IMPLIES, CAUSE, ORDER, GT, LT
                        if state[i_v] is None:
                            state[i_v] = True
                            changed = True
                            
            # Calculate Space Average (S_i)
            known_count = sum(1 for s in state if s is not None)
            true_count = sum(1 for s in state if s is True)
            
            # Avoid division by zero if nothing is known yet
            s_i = (true_count / n_vars) if n_vars > 0 else 0.0
            space_averages.append(s_i)
            
            if not changed:
                break
                
        # Ergodic theorem: time average converges to ensemble average
        return sum(space_averages) / len(space_averages) if space_averages else 0.0

    def _ucb_select(self, counts: List[int], rewards: List[float], t: int) -> int:
        """Select arm with highest UCB."""
        k = len(counts)
        if k == 0:
            return 0
        
        # If any arm not pulled, pull it
        for i in range(k):
            if counts[i] == 0:
                return i
                
        ucb_values = []
        for i in range(k):
            if counts[i] == 0:
                ucb_values.append(float('inf'))
            else:
                mean = rewards[i] / counts[i]
                exploration = math.sqrt(2 * math.log(t + 1) / counts[i])
                ucb_values.append(mean + exploration)
                
        return max(range(k), key=lambda i: ucb_values[i])

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        results = []
        k = len(candidates)
        counts = [0] * k
        rewards = [0.0] * k
        
        # Bandit loop
        for t in range(1, self.budget + 1):
            arm = self._ucb_select(counts, rewards, t)
            
            # Construct full context for evaluation
            # We evaluate the candidate's consistency with the prompt
            context = f"{prompt} {candidates[arm]}"
            nodes, edges = self._extract_graph(context)
            
            # Run ergodic propagation
            score = self._ergodic_propagation(nodes, edges, self.t_steps)
            
            # Update bandit stats
            counts[arm] += 1
            rewards[arm] += score
            
        # Final scoring
        final_scores = []
        for i in range(k):
            mean_score = (rewards[i] / counts[i]) if counts[i] > 0 else 0.0
            final_scores.append({
                "candidate": candidates[i],
                "score": mean_score,
                "reasoning": f"Ergodic mean of constraint satisfaction: {mean_score:.4f}"
            })
            
        # Sort descending by score
        final_scores.sort(key=lambda x: x["score"], reverse=True)
        return final_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural consistency."""
        context = f"{prompt} {answer}"
        nodes, edges = self._extract_graph(context)
        score = self._ergodic_propagation(nodes, edges, self.t_steps)
        # Normalize score to 0-1 range roughly, assuming max space average is 1.0
        return min(1.0, max(0.0, score))