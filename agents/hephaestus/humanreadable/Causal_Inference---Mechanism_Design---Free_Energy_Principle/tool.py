import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Causal-Mechanism Free Energy Reasoner.
    
    Mechanism:
    1. Parsing: Extracts propositions (subject, relation, object) and modalities 
       (causal, conditional, negation, comparative, numeric, utility) using regex.
       Builds a DAG where nodes are grounded propositions.
    2. Intervention: Treats candidate answers as hard interventions (do-calculus), 
       setting node states to 0 or 1.
    3. Propagation: Computes predicted states via topological sort and weighted sums.
    4. Utility & Free Energy: Calculates expected utility from extracted preferences 
       and computes variational free energy (F) based on prediction error and precision.
       Score = -F. Higher score indicates better alignment with causal structure and incentives.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'causal': re.compile(r'(\w+)\s+(causes|leads to|results in|reduces|increases)\s+(\w+)', re.I),
        'conditional': re.compile(r'if\s+(\w+)\s+(?:then)?\s+(\w+)', re.I),
        'negation': re.compile(r'(?:does not|no|not|never)\s+(\w+)', re.I),
        'comparative': re.compile(r'(\w+)\s+(is greater than|is less than|exceeds|less than)\s+(\w+)', re.I),
        'numeric': re.compile(r'(\w+)\s+(?:is|=)\s*([\d\.]+)'),
        'utility': re.compile(r'(\w+)\s+(prefers|rewards|values|wants)\s+(\w+)', re.I),
        'agent_action': re.compile(r'(\w+)\s+(should|will|must)\s+(\w+)', re.I)
    }

    def __init__(self):
        self.epsilon = 1e-6

    def _parse_text(self, text: str) -> Tuple[List[Dict], Dict[str, Any]]:
        """Extract propositions and build graph components."""
        nodes = {}
        edges = []
        utilities = {}
        text_lower = text.lower()
        
        # Helper to normalize node names
        def get_node(name):
            name = name.lower().strip()
            if name not in nodes:
                nodes[name] = {'state': 0.5, 'precision': 0.5, 'utility': 0.0}
            return name

        # Extract Causal/Conditional
        for m in self.PATTERNS['causal'].finditer(text):
            subj, rel, obj = m.group(1), m.group(2), m.group(3)
            u, v = get_node(subj), get_node(obj)
            weight = 0.8 if 'reduces' in rel else 0.9
            if 'reduces' in rel: weight = -0.8
            edges.append((u, v, weight, 'causal'))

        for m in self.PATTERNS['conditional'].finditer(text):
            cond, res = m.group(1), m.group(2)
            u, v = get_node(cond), get_node(res)
            edges.append((u, v, 0.7, 'conditional'))

        # Extract Comparatives (Ordering constraints)
        for m in self.PATTERNS['comparative'].finditer(text):
            subj, rel, obj = m.group(1), m.group(2), m.group(3)
            u, v = get_node(subj), get_node(obj)
            # Encode as causal link with specific weight for ordering
            w = 1.0 if 'greater' in rel or 'exceeds' in rel else -1.0
            edges.append((u, v, w, 'comparative'))

        # Extract Utilities
        for m in self.PATTERNS['utility'].finditer(text):
            agent, _, outcome = m.group(1), m.group(2), m.group(3)
            node = get_node(outcome)
            utilities[node] = 1.0 # Positive utility for preferred outcomes
            
        for m in self.PATTERNS['agent_action'].finditer(text):
            agent, mod, action = m.group(1), m.group(2), m.group(3)
            node = get_node(action)
            utilities[node] = 1.0

        # Extract Negations (Store as metadata for state flipping later)
        negations = set()
        for m in self.PATTERNS['negation'].finditer(text):
            negations.add(m.group(1).lower())
            
        # Extract Numerics (Priors)
        numerics = {}
        for m in self.PATTERNS['numeric'].finditer(text):
            var, val = m.group(1), float(m.group(2))
            node = get_node(var)
            numerics[node] = val

        return nodes, edges, utilities, negations, numerics

    def _build_and_simulate(self, prompt: str, candidate: str) -> float:
        """Build graph from prompt, intervene with candidate, compute Free Energy."""
        full_text = f"{prompt} {candidate}"
        nodes, edges, utils, negations, numerics = self._parse_text(full_text)
        
        if not nodes:
            # Fallback if no structure found
            return 0.0

        node_list = list(nodes.keys())
        n = len(node_list)
        idx_map = {name: i for i, name in enumerate(node_list)}
        
        # Initialize State Vectors
        # State: 1.0 (True), 0.0 (False), 0.5 (Unknown)
        state = np.full(n, 0.5, dtype=np.float64)
        precision = np.full(n, 0.5, dtype=np.float64)
        utility_vec = np.zeros(n, dtype=np.float64)
        
        # Apply parsed priors
        for name, val in numerics.items():
            if name in idx_map:
                state[idx_map[name]] = min(1.0, val / 10.0) # Normalize roughly
                precision[idx_map[name]] = 0.8

        # Apply Utilities
        for name, val in utils.items():
            if name in idx_map:
                utility_vec[idx_map[name]] = val

        # INTERVENTION: Parse candidate for hard constraints
        cand_lower = candidate.lower()
        intervened = False
        
        # Simple keyword intervention based on parsed nodes
        for name in node_list:
            if name in cand_lower:
                # Check for negation in candidate
                if re.search(rf'(no|not|never)\s+{name}', cand_lower) or f"not {name}" in cand_lower:
                    state[idx_map[name]] = 0.0
                    precision[idx_map[name]] = 1.0 # High confidence intervention
                    intervened = True
                else:
                    state[idx_map[name]] = 1.0
                    precision[idx_map[name]] = 1.0
                    intervened = True
        
        # If no direct node match, try to infer from simple "Yes/No" if prompt implies binary
        if not intervened and n > 0:
            # Heuristic: If candidate is "Yes", assume first node is true? 
            # Too risky. Better to rely on structural overlap.
            pass

        # Build Adjacency Matrix (Weighted)
        W = np.zeros((n, n), dtype=np.float64)
        for u, v, w, _ in edges:
            if u in idx_map and v in idx_map:
                W[idx_map[v], idx_map[u]] = w # Column u -> Row v

        # Propagation (Topological-like relaxation)
        # Since we might have cycles in loose parsing, we do fixed-point iteration
        y_pred = state.copy()
        for _ in range(5): # 5 steps of propagation
            y_new = W @ state
            # Mask where we have no inputs
            mask = (W.sum(axis=1) > 0)
            y_pred[mask] = y_new[mask]
            
        # Normalize predictions to [0,1] range roughly for error calc
        # Using sigmoid-like clamp for stability
        y_pred = 1.0 / (1.0 + np.exp(-5 * (y_pred - 0.5)))

        # Compute Errors
        error = state - y_pred
        
        # Free Energy Calculation
        # F = 0.5 * sum(precision * error^2) - 0.5 * sum(log(precision)) - EU
        # Note: We add small epsilon to log to avoid div by zero
        log_prec = np.log(precision + self.epsilon)
        
        # Expected Utility
        EU = np.dot(utility_vec, state)
        
        # Free Energy terms
        term1 = 0.5 * np.sum(precision * (error ** 2))
        term2 = 0.5 * np.sum(log_prec)
        
        F = term1 - term2 - EU
        
        return -F # Score = -F (Higher is better)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        scores = []
        
        # Calculate scores
        for cand in candidates:
            score = self._build_and_simulate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": ""})
            scores.append(score)
            
        # Normalize scores to 0-1 range for readability if needed, but raw score is fine for ranking
        # Add reasoning string based on score magnitude relative to others
        if scores:
            min_s, max_s = min(scores), max(scores)
            range_s = max_s - min_s + self.epsilon
            
            for res in results:
                s = res['score']
                norm = (s - min_s) / range_s
                if norm > 0.6:
                    res['reasoning'] = "High alignment with causal structure and utility maximization."
                elif norm > 0.3:
                    res['reasoning'] = "Moderate alignment; some prediction errors or utility conflicts."
                else:
                    res['reasoning'] = "Low alignment; high prediction error or negative utility outcome."

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the free energy score normalized."""
        # We simulate the single answer against the prompt
        score = self._build_and_simulate(prompt, answer)
        
        # We need a baseline to compare against to get 0-1. 
        # Heuristic: Compare against a null hypothesis (empty string) or just map score.
        # Since F can be negative or positive, let's map via sigmoid of the score.
        # A very negative F (good) becomes large positive score.
        # Let's assume a typical range of scores is [-5, 5].
        # Sigmoid(x) = 1 / (1 + exp(-x))
        conf = 1.0 / (1.0 + np.exp(-score))
        return float(np.clip(conf, 0.0, 1.0))