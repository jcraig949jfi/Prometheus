import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Ergodic-Pragmatic Abstract Interpreter.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical relations (negation, conditional, ordering)
       using regex to build a constraint graph.
    2. Pragmatic Grounding: Initializes truth values based on verifiable numeric claims or 
       observable predicates (1.0/0.0), defaulting to 0.5 (unknown).
    3. Abstract Interpretation & Ergodic Convergence: Iteratively propagates truth values 
       through the graph using fuzzy logic rules (modulus ponens, transitivity). The system 
       runs until convergence (fixed point), approximating the ergodic time-average of the 
       belief state.
    4. Scoring: Candidates are scored by the average truth value of their constituent 
       propositions in the converged state.
    """
    
    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 100
        
        # Regex patterns for structural extraction
        self.patterns = {
            'numeric_claim': re.compile(r'(\d+(?:\.\d+)?)\s*(?:is|equals|=|>)\s*(\d+(?:\.\d+)?)'),
            'comparative': re.compile(r'(\w+)\s*(?:>|is greater than|>\=|>=)\s*(\w+)', re.IGNORECASE),
            'less_than': re.compile(r'(\w+)\s*(?:<|is less than|<=|=<)\s*(\w+)', re.IGNORECASE),
            'conditional': re.compile(r'(?:if|when)\s+([^,\.]+?)(?:,|\s+then|\s+it)\s+(.+?)(?:\.|$)', re.IGNORECASE),
            'negation': re.compile(r'(?:not|no|never|false)\s+(\w+)', re.IGNORECASE),
            'causal': re.compile(r'(\w+)\s+(?:causes|leads to|implies)\s+(\w+)', re.IGNORECASE)
        }

    def _extract_tokens(self, text: str) -> List[str]:
        """Simple tokenization for proposition mapping."""
        return list(set(re.findall(r'\w+', text.lower())))

    def _parse_graph(self, text: str) -> Tuple[List[str], Dict[str, List[Tuple[str, float]]], Dict[str, float]]:
        """
        Parses text into nodes, edges (adjacency list), and initial truth values.
        Returns: (nodes, edges, initial_truth)
        """
        nodes = []
        edges = {} # node -> [(target, weight, type)]
        initial_truth = {}
        
        # Helper to add node
        def add_node(name):
            name = name.strip().lower()
            if not name: return name
            if name not in nodes:
                nodes.append(name)
                initial_truth[name] = 0.5 # Default unknown
                edges[name] = []
            return name

        # 1. Extract Numeric Claims (Pragmatic Grounding)
        # Pattern: "X is 5" or "5 > 3" simplified logic
        nums = re.findall(r'\d+(?:\.\d+)?', text)
        for i, n in enumerate(nums):
            node_name = f"_num_{i}_{n}"
            add_node(node_name)
            initial_truth[node_name] = 1.0 # Numbers are grounded facts
            
        # 2. Extract Comparatives (A > B implies A is 'more' true if B is true? 
        # Or strictly: if A > B, and B is true, A is likely true. 
        # Simplified: Treat as constraint A >= B)
        for match in self.patterns['comparative'].finditer(text):
            a, b = add_node(match.group(1)), add_node(match.group(2))
            # A > B: If B is true, A must be true (monotonicity)
            edges[b].append((a, 0.9, 'implication')) 

        for match in self.patterns['less_than'].finditer(text):
            a, b = add_node(match.group(1)), add_node(match.group(2))
            # A < B: If A is true, B must be true
            edges[a].append((b, 0.9, 'implication'))

        # 3. Conditionals (If A then B)
        for match in self.patterns['conditional'].finditer(text):
            antecedent = add_node(match.group(1).strip())
            consequent = add_node(match.group(2).strip())
            edges[antecedent].append((consequent, 0.95, 'implication'))

        # 4. Causal
        for match in self.patterns['causal'].finditer(text):
            cause = add_node(match.group(1))
            effect = add_node(match.group(2))
            edges[cause].append((effect, 0.9, 'implication'))

        # 5. Negation (Special handling: not A)
        # We create a virtual node "_neg_A" linked to A
        for match in self.patterns['negation'].finditer(text):
            target = add_node(match.group(1))
            neg_node = add_node(f"_neg_{target}")
            # Link negation node to target with negative weight or special flag
            # For simplicity in this framework: store as special edge
            edges[neg_node].append((target, -1.0, 'negation')) 
            # If the text asserts "Not A", we ground "_neg_A" to 1.0
            if f"not {match.group(1)}" in text.lower() or f"no {match.group(1)}" in text.lower():
                 initial_truth[neg_node] = 1.0

        # Fill missing nodes with 0.5 if not grounded
        for n in nodes:
            if n not in initial_truth:
                initial_truth[n] = 0.5
                
        return nodes, edges, initial_truth

    def _propagate(self, nodes: List[str], edges: Dict, t0: Dict[str, float]) -> Dict[str, float]:
        """Iterative propagation to fixed point (Ergodic approximation)."""
        t = t0.copy()
        node_list = list(t.keys())
        
        for _ in range(self.max_iter):
            t_new = t.copy()
            changed = False
            
            for node in node_list:
                current_val = t[node]
                
                # Process outgoing edges
                if node in edges:
                    for target, weight, etype in edges[node]:
                        if target not in t: continue
                        
                        val = current_val
                        if etype == 'negation':
                            # Negation propagation: t(not A) = 1 - t(A)
                            # If node is "_neg_X", its value affects X? 
                            # Actually, logic is usually: if we know "Not A" is true, A is false.
                            # Here we treat the edge weight -1.0 as a flip.
                            propagated = 1.0 - val 
                        else:
                            # Implication: t(B) >= t(A) * w
                            propagated = val * weight
                            
                        if etype == 'negation':
                            # Special update for negation targets
                            if propagated > t_new.get(target, 0): 
                                # This logic is simplified for the demo
                                pass 
                            # Direct assignment for negation constraints
                            t_new[target] = max(t_new.get(target, 0), 1.0 - val)
                        else:
                            t_new[target] = max(t_new.get(target, 0), propagated)
                            
                # Clip to [0, 1]
                t_new[node] = max(0.0, min(1.0, t_new[node]))

            # Check convergence
            diff = sum(abs(t_new.get(k, 0) - t.get(k, 0)) for k in t)
            t = t_new
            if diff < self.epsilon:
                break
                
        return t

    def _score_candidate(self, candidate: str, final_truth: Dict[str, float], nodes: List[str]) -> float:
        """Scores a candidate based on the truth of its tokens in the final state."""
        cand_tokens = set(re.findall(r'\w+', candidate.lower()))
        if not cand_tokens:
            return 0.0
            
        scores = []
        for token in cand_tokens:
            # Check direct match
            if token in final_truth:
                scores.append(final_truth[token])
            # Check substring match for flexibility
            else:
                matched = False
                for node in nodes:
                    if token in node or node in token:
                        scores.append(final_truth.get(node, 0.5))
                        matched = True
                        break
                if not matched:
                    # Unknown tokens default to 0.5 (neutral)
                    scores.append(0.5)
                    
        return float(np.mean(scores)) if scores else 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # 1. Parse Prompt into Graph
        nodes, edges, initial_truth = self._parse_graph(prompt)
        
        # 2. Propagate to Fixed Point
        final_truth = self._propagate(nodes, edges, initial_truth)
        
        # 3. Score Candidates
        results = []
        for cand in candidates:
            score = self._score_candidate(cand, final_truth, nodes)
            
            # Tie-breaking with NCD (Normalized Compression Distance) if scores are close
            # But primary signal is structural. 
            # We add a tiny NCD bonus for brevity/relevance if structural score is ambiguous
            import zlib
            s1 = prompt.encode()
            s2 = cand.encode()
            try:
                l1, l2, l12 = len(s1), len(s2), len(zlib.compress(s1 + s2))
                ncd = (l12 - min(l1, l2)) / max(l1, l2) if max(l1, l2) > 0 else 1.0
                # Invert NCD: lower distance = higher score contribution
                ncd_score = (1.0 - ncd) * 0.01 # Small weight
            except:
                ncd_score = 0.0
                
            final_score = score + ncd_score
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural truth: {score:.4f}, NCD bonus: {ncd_score:.4f}"
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural consistency."""
        nodes, edges, initial_truth = self._parse_graph(prompt)
        final_truth = self._propagate(nodes, edges, initial_truth)
        score = self._score_candidate(answer, final_truth, nodes)
        return min(1.0, max(0.0, score))