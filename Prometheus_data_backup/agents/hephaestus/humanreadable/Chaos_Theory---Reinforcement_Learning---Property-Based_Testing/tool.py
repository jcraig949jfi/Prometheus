from typing import Dict, Tuple

"""
Lyapunov-Guided Policy-Graph Scorer (LPGS)

Combines Chaos Theory, Reinforcement Learning, and Property-Based Testing:
1. Extracts logical propositions into a constraint graph
2. Generates perturbations (PBT) and measures sensitivity (Lyapunov exponent)
3. Uses stability as RL reward to score candidates
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib
from forge_primitives import (
    solve_constraints, check_transitivity, bayesian_update,
    confidence_from_agreement, information_sufficiency, topological_sort
)
import networkx as nx


class ReasoningTool:
    def __init__(self):
        self.baseline_reward = 0.0
        self.learning_rate = 0.1
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by graph stability + constraint satisfaction."""
        # Parse prompt into constraint graph
        prompt_graph, prompt_props = self._parse_to_graph(prompt)
        
        results = []
        for cand in candidates:
            cand_graph, cand_props = self._parse_to_graph(cand)
            
            # 1. Constraint satisfaction score
            constraint_score = self._compute_constraint_match(
                prompt_props, cand_props, prompt_graph, cand_graph
            )
            
            # 2. Lyapunov stability (chaos sensitivity)
            stability = self._lyapunov_stability(prompt, cand)
            
            # 3. Graph coherence via transitivity
            coherence = self._graph_coherence(cand_graph)
            
            # 4. NCD tiebreaker
            ncd = self._ncd(prompt, cand)
            
            # Weighted combination
            score = (0.50 * constraint_score + 
                    0.25 * stability + 
                    0.15 * coherence + 
                    0.10 * (1 - ncd))
            
            reasoning = f"constraint={constraint_score:.2f} stability={stability:.2f} coherence={coherence:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        # RL-style baseline update
        scores = [r["score"] for r in results]
        self.baseline_reward = 0.9 * self.baseline_reward + 0.1 * np.mean(scores)
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Epistemic honest confidence with meta-reasoning checks."""
        # Check prompt for ambiguity/unanswerability
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Structural parsing confidence
        _, prompt_props = self._parse_to_graph(prompt)
        _, ans_props = self._parse_to_graph(answer)
        
        if not prompt_props and not ans_props:
            return 0.2  # No structure detected
        
        # Multi-metric agreement
        stability = self._lyapunov_stability(prompt, answer)
        _, coherence_graph = self._parse_to_graph(answer)
        coherence = self._graph_coherence(coherence_graph)
        
        scores = [stability, coherence, meta_conf]
        conf = confidence_from_agreement(scores)
        
        # Cap at 0.85 unless perfect computational match
        return min(conf, 0.85) if conf < 0.95 else conf
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.15
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery \w+ .+ a \w+', p) and 'same' not in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and 'who' in p:
            return 0.20
        
        # False dichotomy
        if re.search(r'\b(either .+ or|must be (true|false))\b', p):
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            if not re.search(r'\b(because|since|criteria|measure)\b', p):
                return 0.20
        
        # Insufficient information
        unknowns = len(re.findall(r'\?|\bunknown\b|\bnot (given|stated)\b', p))
        if unknowns > 1:
            return 0.25
        
        return 0.8  # Default: assumable answerable
    
    def _parse_to_graph(self, text: str) -> Tuple[nx.DiGraph, List[Dict]]:
        """Extract propositions and build dependency graph."""
        props = []
        G = nx.DiGraph()
        
        # Extract structured patterns
        # Negations
        for m in re.finditer(r'\b(not|no|never)\s+(\w+)', text.lower()):
            props.append({"type": "neg", "target": m.group(2), "text": m.group(0)})
        
        # Comparatives with numbers
        for m in re.finditer(r'([\d.]+)\s*(>|<|>=|<=|more than|less than)\s*([\d.]+)', text):
            val1, op, val2 = float(m.group(1)), m.group(2), float(m.group(3))
            result = self._eval_comparison(val1, op, val2)
            props.append({"type": "comp", "val": result, "text": m.group(0)})
        
        # Conditionals
        for m in re.finditer(r'\bif (.+?) then (.+?)(?:\.|$)', text.lower()):
            ante, cons = m.group(1).strip(), m.group(2).strip()
            props.append({"type": "cond", "ante": ante, "cons": cons})
            G.add_edge(ante, cons, weight=1.0)
        
        # Causal
        for m in re.finditer(r'(.+?)\s+(because|leads to|results in|causes)\s+(.+?)(?:\.|$)', text.lower()):
            cause, effect = m.group(1).strip(), m.group(3).strip()
            props.append({"type": "causal", "cause": cause, "effect": effect})
            G.add_edge(cause, effect, weight=1.0)
        
        # Ordering
        for m in re.finditer(r'(.+?)\s+(before|after)\s+(.+?)(?:\.|$)', text.lower()):
            first, rel, second = m.group(1).strip(), m.group(2), m.group(3).strip()
            if rel == "before":
                G.add_edge(first, second, weight=1.0)
            else:
                G.add_edge(second, first, weight=1.0)
            props.append({"type": "order", "rel": rel})
        
        return G, props
    
    def _eval_comparison(self, v1: float, op: str, v2: float) -> bool:
        """Evaluate numeric comparison."""
        if '>' in op:
            return v1 >= v2 if '=' in op else v1 > v2
        elif '<' in op:
            return v1 <= v2 if '=' in op else v1 < v2
        elif 'more' in op:
            return v1 > v2
        elif 'less' in op:
            return v1 < v2
        return False
    
    def _compute_constraint_match(self, p_props, c_props, p_graph, c_graph) -> float:
        """Match constraints between prompt and candidate using primitives."""
        if not p_props and not c_props:
            return 0.5
        
        # Type overlap
        p_types = set(p.get("type") for p in p_props)
        c_types = set(p.get("type") for p in c_props)
        type_overlap = len(p_types & c_types) / max(len(p_types | c_types), 1)
        
        # Graph edge overlap (using networkx topological similarity)
        p_edges = set(p_graph.edges())
        c_edges = set(c_graph.edges())
        edge_overlap = len(p_edges & c_edges) / max(len(p_edges | c_edges), 1) if p_edges or c_edges else 0.5
        
        # Numeric constraint matching
        p_comps = [p for p in p_props if p.get("type") == "comp"]
        c_comps = [p for p in c_props if p.get("type") == "comp"]
        comp_match = sum(1 for pc in p_comps for cc in c_comps if pc.get("val") == cc.get("val"))
        comp_score = comp_match / max(len(p_comps), 1) if p_comps else 0.5
        
        return 0.4 * type_overlap + 0.3 * edge_overlap + 0.3 * comp_score
    
    def _lyapunov_stability(self, prompt: str, candidate: str, n_pert: int = 5) -> float:
        """Estimate stability via perturbation sensitivity (chaos theory)."""
        base_graph, _ = self._parse_to_graph(candidate)
        base_size = len(base_graph.edges())
        
        if base_size == 0:
            return 0.5
        
        deviations = []
        for _ in range(n_pert):
            perturbed = self._perturb_text(candidate)
            pert_graph, _ = self._parse_to_graph(perturbed)
            
            # Measure graph divergence
            deviation = abs(len(pert_graph.edges()) - base_size) / max(base_size, 1)
            deviations.append(deviation)
        
        # Stability = inverse of average deviation
        avg_dev = np.mean(deviations) if deviations else 1.0
        lyap_approx = avg_dev
        
        # Lower Lyapunov = more stable = higher score
        return max(0, 1.0 - lyap_approx)
    
    def _perturb_text(self, text: str) -> str:
        """Property-based perturbation: swap words, tweak numbers."""
        tokens = text.split()
        if len(tokens) < 2:
            return text
        
        choice = np.random.randint(0, 3)
        
        if choice == 0:  # Swap two tokens
            i, j = np.random.choice(len(tokens), 2, replace=False)
            tokens[i], tokens[j] = tokens[j], tokens[i]
        elif choice == 1:  # Perturb number
            for i, tok in enumerate(tokens):
                if re.match(r'^\d+(\.\d+)?$', tok):
                    val = float(tok)
                    tokens[i] = str(val + np.random.uniform(-0.1, 0.1))
                    break
        # choice == 2: no-op perturbation
        
        return ' '.join(tokens)
    
    def _graph_coherence(self, G: nx.DiGraph) -> float:
        """Check transitivity and DAG structure via primitives."""
        if len(G.edges()) == 0:
            return 0.5
        
        # Check if graph is a DAG
        try:
            topological_sort(list(G.edges()))
            dag_score = 1.0
        except:
            dag_score = 0.3
        
        # Check transitivity
        edges = list(G.edges())
        trans_violations = 0
        for u, v in edges:
            for v2, w in edges:
                if v == v2 and (u, w) not in edges and u != w:
                    trans_violations += 1
        
        trans_score = max(0, 1.0 - trans_violations / max(len(edges), 1))
        
        return 0.6 * dag_score + 0.4 * trans_score
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0