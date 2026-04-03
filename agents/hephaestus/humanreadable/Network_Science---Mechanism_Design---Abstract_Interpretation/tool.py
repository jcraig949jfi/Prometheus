"""
Network Science x Mechanism Design x Abstract Interpretation Reasoning Tool

Parses prompts into directed graphs of propositions, propagates three-valued truth
via abstract interpretation over the graph topology, then uses mechanism-design
utility functions to score candidate answers based on consistency and deviation.
"""

import re
import numpy as np
import zlib
from collections import defaultdict
try:
    from forge_primitives import (
        check_transitivity, solve_constraints, bayesian_update,
        information_sufficiency, confidence_from_agreement, modus_ponens
    )
    import networkx as nx
except ImportError:
    # Fallback implementations if primitives not available
    def check_transitivity(relations): return []
    def solve_constraints(v, d, c): return {}
    def bayesian_update(prior, lik, fp): return prior * lik / (prior * lik + (1-prior) * fp)
    def information_sufficiency(u, c): return len(c) >= len(u)
    def confidence_from_agreement(s): return np.mean(s) if len(s) > 0 else 0.5
    def modus_ponens(p, f): return []
    try:
        import networkx as nx
    except:
        nx = None

class ReasoningTool:
    def __init__(self):
        self.truth_vals = {-1: False, 0: None, 1: True}
        
    def _parse_graph(self, text):
        """Extract propositions and relations into a directed graph"""
        if nx is None:
            return None, {}
        G = nx.DiGraph()
        props = {}
        prop_id = 0
        
        # Extract atomic propositions and relations
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip().lower()
            if not sent: continue
            
            # Conditionals: if X then Y
            if_match = re.search(r'if\s+(.+?)\s+then\s+(.+)', sent)
            if if_match:
                p, q = if_match.groups()
                if p not in props: props[p], prop_id = prop_id, prop_id + 1
                if q not in props: props[q], prop_id = prop_id, prop_id + 1
                G.add_edge(props[p], props[q], type='imp')
                continue
            
            # Comparatives: X > Y, X < Y, X = Y
            comp_match = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', sent)
            if comp_match:
                v1, op, v2 = comp_match.groups()
                v1, v2 = float(v1), float(v2)
                key = f"{v1}{op}{v2}"
                if key not in props: props[key], prop_id = prop_id, prop_id + 1
                G.add_node(props[key], value=v1, op=op, target=v2)
                continue
            
            # Negations: not X, X is false
            neg_match = re.search(r'(?:not|n\'t|never)\s+(.+)', sent)
            if neg_match:
                p = neg_match.group(1).strip()
                if p not in props: props[p], prop_id = prop_id, prop_id + 1
                G.add_node(props[p], neg=True)
                continue
            
            # Default: add as atomic proposition
            if sent not in props: props[sent], prop_id = prop_id, prop_id + 1
            G.add_node(props[sent])
        
        return G, {v: k for k, v in props.items()}
    
    def _abstract_interpret(self, G, rev_props):
        """Propagate three-valued truth through graph topology"""
        if G is None or len(G) == 0: return {}
        n = len(G.nodes())
        truth = np.zeros(n, dtype=int)  # -1=false, 0=unknown, 1=true
        
        # Initialize from node attributes
        for node, data in G.nodes(data=True):
            if 'value' in data and 'op' in data:
                v, op, t = data['value'], data['op'], data['target']
                if op in ['>', 'gt'] and v > t: truth[node] = 1
                elif op in ['<', 'lt'] and v < t: truth[node] = 1
                elif op in ['=', 'equals', 'eq'] and abs(v - t) < 0.01: truth[node] = 1
                elif op in ['>=', 'ge'] and v >= t: truth[node] = 1
                elif op in ['<=', 'le'] and v <= t: truth[node] = 1
                else: truth[node] = -1
            if data.get('neg', False): truth[node] = -1
        
        # Fixpoint propagation via topological traversal
        try:
            from forge_primitives import topological_sort
            order = topological_sort(list(G.edges()))
        except:
            order = list(nx.topological_sort(G)) if nx.is_directed_acyclic_graph(G) else list(G.nodes())
        
        for _ in range(len(G.nodes())):  # Iterate to fixpoint
            changed = False
            for u in order if order else G.nodes():
                for v in G.successors(u):
                    edge_type = G[u][v].get('type', 'default')
                    if edge_type == 'imp':
                        old_v = truth[v]
                        if truth[u] == 1: truth[v] = max(truth[v], 1)
                        elif truth[u] == -1: truth[v] = min(truth[v], -1)
                        if old_v != truth[v]: changed = True
            if not changed: break
        
        return {i: truth[i] for i in range(n)}
    
    def _mechanism_score(self, G, truth_prompt, truth_cand):
        """VCG-inspired utility: reward consistency, penalize deviation"""
        if G is None or len(G) == 0: return 0.0
        edge_score = 0.0
        for u, v, data in G.edges(data=True):
            if data.get('type') == 'imp':
                if truth_cand.get(u, 0) == 1 and truth_cand.get(v, 0) == 1:
                    edge_score += 1.0
        
        deviation = sum(abs(truth_prompt.get(i, 0) - truth_cand.get(i, 0)) 
                       for i in set(truth_prompt) | set(truth_cand))
        
        utility = edge_score - 0.5 * deviation
        return utility
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability (epistemic honesty)"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(?:have you stopped|did you quit|why did .+ (?:fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*?\ba\s+\w+', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'told.*?\b(?:he|she)\b.*?\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+.+?\bor\b.+?\?', p) and 'both' not in p and 'neither' not in p:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(?:best|worst|favorite|prefer)\b', p) and 'most' not in p:
            return 0.3
        
        # Information sufficiency check
        unknowns = len(re.findall(r'\?', p))
        constraints = len(re.findall(r'\d+|if|then|>|<|=', p))
        try:
            if not information_sufficiency([0]*unknowns, [0]*constraints):
                return 0.3
        except: pass
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # Parse prompt into graph
        G_prompt, rev_props_prompt = self._parse_graph(prompt)
        truth_prompt = self._abstract_interpret(G_prompt, rev_props_prompt)
        
        results = []
        for cand in candidates:
            # Parse candidate
            G_cand, rev_props_cand = self._parse_graph(prompt + " " + cand)
            truth_cand = self._abstract_interpret(G_cand, rev_props_cand)
            
            # Mechanism design scoring
            struct_score = self._mechanism_score(G_prompt, truth_prompt, truth_cand)
            
            # Numeric computation bonus
            comp_bonus = 0.0
            nums_prompt = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
            nums_cand = [float(x) for x in re.findall(r'\d+\.?\d*', cand)]
            if nums_prompt and nums_cand:
                comp_bonus = 1.0 if any(abs(n - m) < 0.1 for n in nums_prompt for m in nums_cand) else 0.0
            
            # NCD tiebreaker (max 15%)
            ncd = (zlib.compress((prompt + cand).encode()) - min(zlib.compress(prompt.encode()), 
                   zlib.compress(cand.encode()))) / max(zlib.compress(prompt.encode()), 
                   zlib.compress(cand.encode()))
            ncd_score = 1.0 / (1.0 + ncd)
            
            # Weighted combination: 60% structural, 25% computational, 15% NCD
            total = 0.6 * struct_score + 0.25 * comp_bonus + 0.15 * ncd_score
            
            reasoning = f"Graph edges: {G_cand.number_of_edges() if G_cand else 0}, " \
                       f"Truth propagation: {len(truth_cand)} nodes, Mechanism utility: {struct_score:.2f}"
            
            results.append({"candidate": cand, "score": float(total), "reasoning": reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence cap based on prompt quality
        meta_cap = self._meta_confidence(prompt)
        
        # Parse and evaluate
        G_prompt, rev_props_prompt = self._parse_graph(prompt)
        G_combined, rev_props_combined = self._parse_graph(prompt + " " + answer)
        
        if G_prompt is None or G_combined is None:
            return min(0.5, meta_cap)
        
        truth_prompt = self._abstract_interpret(G_prompt, rev_props_prompt)
        truth_combined = self._abstract_interpret(G_combined, rev_props_combined)
        
        # Compute consistency score
        consistency = self._mechanism_score(G_prompt, truth_prompt, truth_combined)
        
        # Normalize to [0, 1] via sigmoid-like function
        base_conf = 1.0 / (1.0 + np.exp(-consistency))
        
        # Cap by meta-confidence (epistemic honesty)
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 unless very strong signal
        if consistency < 3.0:
            final_conf = min(final_conf, 0.85)
        
        return float(np.clip(final_conf, 0.0, 1.0))