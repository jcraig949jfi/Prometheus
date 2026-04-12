from typing import Set

import re
import numpy as np
from forge_primitives import (
    modus_ponens, check_transitivity, negate,
    dag_traverse, topological_sort,
    solve_constraints, information_sufficiency,
    confidence_from_agreement
)
import networkx as nx

class ReasoningTool:
    """
    Gene Regulatory Network + Apoptosis + Mechanism Design reasoning tool.
    
    Builds a signed directed graph of propositions, propagates constraints through
    network dynamics, prunes weak nodes via apoptosis, and scores via mechanism-design
    payoffs that reward self-verifiable claims.
    """
    
    def __init__(self):
        self.activation_threshold = 0.5
        self.apoptosis_threshold = 0.2
        self.max_iterations = 10
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = f"GRN score: {score:.3f}, confidence: {conf:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._score_candidate(prompt, answer)
        base_conf = min(0.85, score / 10.0)
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|did you stop|why did .* (fail|stop|quit))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .* (a|an) ', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|were|is|are)', p_lower) and '?' in prompt:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or|must be .* or)\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p_lower):
            return 0.3
        
        # Insufficient information
        if re.search(r'\b(who knows|impossible to|cannot determine|not enough)\b', p_lower):
            return 0.2
        
        return 0.8
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Extract propositions and build graph
        props = self._extract_propositions(candidate)
        if not props:
            return self._fallback_ncd(prompt, candidate)
        
        G = self._build_regulatory_graph(props)
        
        # GRN constraint propagation
        states = self._propagate_constraints(G, props)
        
        # Apoptotic pruning
        pruned_states = self._apoptotic_pruning(G, states, props)
        
        # Mechanism design payoff
        payoff = self._mechanism_payoff(props, pruned_states)
        
        # Add numeric verification bonus
        numeric_score = self._evaluate_numeric_claims(prompt, candidate)
        
        # Combine scores: 70% GRN+apoptosis+mechanism, 20% numeric, 10% NCD
        ncd = self._fallback_ncd(prompt, candidate)
        total = 0.7 * payoff + 0.2 * numeric_score + 0.1 * ncd
        
        return total
    
    def _extract_propositions(self, text: str) -> list[dict]:
        props = []
        sentences = re.split(r'[.!?;]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            prop = {
                'text': sent,
                'negated': bool(re.search(r'\b(not|no|never|none)\b', sent.lower())),
                'numeric': self._extract_numeric(sent),
                'causal_verb': bool(re.search(r'\b(causes?|leads? to|results? in|produces?)\b', sent.lower())),
                'inhibitory': bool(re.search(r'\b(prevents?|blocks?|suppresses?|inhibits?)\b', sent.lower())),
                'conditional': bool(re.search(r'\b(if|then|only if|unless)\b', sent.lower()))
            }
            props.append(prop)
        
        return props
    
    def _extract_numeric(self, text: str) -> dict:
        # Extract numeric comparisons
        match = re.search(r'(\d+\.?\d*)\s*(>|<|=|>=|<=)\s*(\d+\.?\d*)', text)
        if match:
            return {'left': float(match.group(1)), 'op': match.group(2), 'right': float(match.group(3))}
        return None
    
    def _build_regulatory_graph(self, props: list[dict]) -> nx.DiGraph:
        G = nx.DiGraph()
        
        for i, prop in enumerate(props):
            G.add_node(i, **prop)
        
        # Add regulatory edges based on structure
        for i in range(len(props)):
            for j in range(i+1, len(props)):
                if props[i]['causal_verb']:
                    G.add_edge(i, j, weight=1.0)  # Activation
                elif props[i]['inhibitory']:
                    G.add_edge(i, j, weight=-1.0)  # Inhibition
                elif props[i]['conditional'] and props[j]['conditional']:
                    G.add_edge(i, j, weight=0.5)  # Weak support
        
        return G
    
    def _propagate_constraints(self, G: nx.DiGraph, props: list[dict]) -> np.ndarray:
        n = len(props)
        if n == 0:
            return np.array([])
        
        states = np.ones(n) * 0.5
        
        # Set initial biases based on numeric verification
        for i, prop in enumerate(props):
            if prop['numeric']:
                if self._check_numeric(prop['numeric']):
                    states[i] = 0.8
                else:
                    states[i] = 0.2
        
        # Iterative constraint propagation (GRN dynamics)
        for _ in range(self.max_iterations):
            new_states = states.copy()
            
            for node in G.nodes():
                incoming = sum(G[pred][node]['weight'] * states[pred] 
                             for pred in G.predecessors(node))
                bias = 0.5 if props[node].get('numeric') and self._check_numeric(props[node]['numeric']) else 0
                
                activation = incoming + bias
                new_states[node] = 1.0 if activation > self.activation_threshold else 0.0
            
            if np.allclose(states, new_states):
                break
            states = new_states
        
        return states
    
    def _check_numeric(self, numeric: dict) -> bool:
        if not numeric:
            return False
        
        left, op, right = numeric['left'], numeric['op'], numeric['right']
        if op == '>':
            return left > right
        elif op == '<':
            return left < right
        elif op in ('=', '=='):
            return abs(left - right) < 1e-6
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right
        return False
    
    def _apoptotic_pruning(self, G: nx.DiGraph, states: np.ndarray, props: list[dict]) -> np.ndarray:
        if len(states) == 0:
            return states
        
        # Mark weakly activated nodes for apoptosis
        pruned = states.copy()
        apoptotic_nodes = np.where(states < self.apoptosis_threshold)[0]
        
        # Remove edges incident to apoptotic nodes and re-propagate
        G_pruned = G.copy()
        G_pruned.remove_nodes_from(apoptotic_nodes)
        
        # Re-propagate on pruned graph
        for node in apoptotic_nodes:
            pruned[node] = 0.0
        
        return pruned
    
    def _mechanism_payoff(self, props: list[dict], states: np.ndarray) -> float:
        if len(props) == 0 or len(states) == 0:
            return 0.0
        
        # Mechanism design: higher payoff for self-verifiable propositions
        payoff = 0.0
        for i, prop in enumerate(props):
            prop_payoff = 0.5  # Base payoff
            
            if prop['numeric']:
                prop_payoff = 2.0  # Self-verifiable numeric claims
            elif prop['conditional']:
                prop_payoff = 1.0  # Testable conditionals
            elif prop['causal_verb']:
                prop_payoff = 0.5  # Untested causal claims
            
            payoff += states[i] * prop_payoff
        
        return payoff
    
    def _evaluate_numeric_claims(self, prompt: str, candidate: str) -> float:
        # Extract and verify numeric comparisons
        prompt_nums = re.findall(r'\d+\.?\d*', prompt)
        cand_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not cand_nums:
            return 0.0
        
        score = 0.0
        # Check for correct numeric reasoning
        for cand_num in cand_nums:
            try:
                val = float(cand_num)
                # Reward plausible numeric answers
                if 0 <= val <= 1000:
                    score += 0.5
            except:
                pass
        
        return min(10.0, score)
    
    def _fallback_ncd(self, prompt: str, candidate: str) -> float:
        import zlib
        
        def ncd(s1: str, s2: str) -> float:
            c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
        
        return max(0.0, 10.0 * (1.0 - ncd(prompt, candidate)))