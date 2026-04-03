"""
Category Theory x Error Correcting Codes x Property-Based Testing

Parses text into labeled graphs (category morphisms), encodes structural features
via Hamming codes, and uses property-based testing to find logical violations.
Score = structural_similarity * (1 - logical_failure_rate)
"""

import re
import numpy as np
from itertools import product
from forge_primitives import (
    check_transitivity, modus_ponens, negate,
    confidence_from_agreement, information_sufficiency,
    solve_constraints, topological_sort
)
import networkx as nx


class ReasoningTool:
    def __init__(self):
        # Hamming(7,4) generator matrix for encoding structural features
        self.hamming_G = np.array([
            [1, 0, 0, 0, 0, 1, 1],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 1, 1, 1, 1]
        ], dtype=np.uint8)
        
        # Structural feature types
        self.features = ['negation', 'comparative', 'conditional', 'causal', 
                        'ordering', 'numeric', 'quantifier']
        
    def _parse_propositions(self, text):
        """Extract atomic propositions and their structural features."""
        sentences = re.split(r'[.;]', text.lower())
        props = []
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3:
                continue
                
            features = {
                'text': sent,
                'negation': bool(re.search(r'\b(not|no|never|none)\b', sent)),
                'comparative': bool(re.search(r'(>|<|more|less|greater|fewer|than)', sent)),
                'conditional': bool(re.search(r'\b(if|then|when|unless)\b', sent)),
                'causal': bool(re.search(r'\b(because|cause|leads? to|result|due to)\b', sent)),
                'ordering': bool(re.search(r'\b(before|after|first|last|next|previous)\b', sent)),
                'numeric': bool(re.search(r'\d+\.?\d*', sent)),
                'quantifier': bool(re.search(r'\b(all|some|every|any|each|most|few)\b', sent))
            }
            props.append(features)
        
        return props
    
    def _build_graph(self, props):
        """Build directed labeled graph from propositions."""
        G = nx.DiGraph()
        
        for i, p in enumerate(props):
            G.add_node(i, **p)
        
        # Add edges based on structural patterns
        for i in range(len(props)):
            for j in range(len(props)):
                if i == j:
                    continue
                    
                pi, pj = props[i], props[j]
                
                # Negation edge
                if pi['negation'] and not pj['negation']:
                    G.add_edge(i, j, label='neg')
                
                # Ordering edge
                if pi['ordering'] and pj['ordering']:
                    if 'before' in pi['text'] or 'first' in pi['text']:
                        G.add_edge(i, j, label='precedes')
                
                # Conditional edge
                if pi['conditional']:
                    if 'if' in pi['text'] and 'then' in pj['text']:
                        G.add_edge(i, j, label='implies')
                
                # Causal edge
                if pi['causal']:
                    G.add_edge(i, j, label='cause')
        
        return G
    
    def _encode_features(self, props):
        """Encode structural features using Hamming code."""
        if not props:
            return np.zeros(7, dtype=np.uint8)
        
        # Create feature vector (4 bits, use first 4 features)
        feature_vec = np.zeros(4, dtype=np.uint8)
        for p in props:
            for idx, feat in enumerate(self.features[:4]):
                if p[feat]:
                    feature_vec[idx] = 1
        
        # Encode using Hamming(7,4)
        codeword = (self.hamming_G.T @ feature_vec) % 2
        return codeword
    
    def _hamming_similarity(self, code1, code2):
        """Compute similarity from Hamming distance."""
        distance = np.sum(code1 != code2)
        return 1.0 - (distance / len(code1))
    
    def _property_test(self, G):
        """Property-based testing: randomly assign truth values, check constraints."""
        if G.number_of_nodes() == 0:
            return 0.0
        
        n_tests = min(50, 2 ** G.number_of_nodes())
        failures = 0
        
        for _ in range(n_tests):
            # Random truth assignment
            truth = {node: np.random.choice([True, False]) 
                    for node in G.nodes()}
            
            # Check categorical constraints
            for u, v, data in G.edges(data=True):
                label = data.get('label', '')
                
                # Negation constraint
                if label == 'neg' and truth[u] == truth[v]:
                    failures += 1
                    break
                
                # Implication constraint (modus ponens)
                if label == 'implies' and truth[u] and not truth[v]:
                    failures += 1
                    break
                
                # Transitivity check for ordering
                if label == 'precedes':
                    # Find transitive closure violations
                    for w in G.nodes():
                        if G.has_edge(v, w) and G[v][w].get('label') == 'precedes':
                            if not G.has_edge(u, w):
                                failures += 1
                                break
        
        return failures / n_tests
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/presupposition markers."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* fail)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\bbecause\b', p):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using Category Theory + ECC + Property-Based Testing."""
        results = []
        
        # Parse prompt for reference structure
        prompt_props = self._parse_propositions(prompt)
        prompt_code = self._encode_features(prompt_props)
        
        for cand in candidates:
            # Parse candidate
            cand_props = self._parse_propositions(cand)
            
            # Structural similarity via Hamming code
            cand_code = self._encode_features(cand_props)
            structural_sim = self._hamming_similarity(prompt_code, cand_code)
            
            # Build category graph
            G = self._build_graph(cand_props)
            
            # Property-based testing for logical consistency
            failure_rate = self._property_test(G)
            
            # Combined score
            score = structural_sim * (1.0 - failure_rate)
            
            # Add small NCD tiebreaker (max 10%)
            import zlib
            ncd = (len(zlib.compress((prompt + cand).encode())) - 
                   min(len(zlib.compress(prompt.encode())), len(zlib.compress(cand.encode())))) / \
                  max(len(zlib.compress(prompt.encode())), len(zlib.compress(cand.encode())))
            score = 0.9 * score + 0.1 * (1 - ncd)
            
            reasoning = f"Structural={structural_sim:.2f}, FailureRate={failure_rate:.2f}, Nodes={G.number_of_nodes()}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on prompt properties and answer consistency."""
        # Check prompt for meta-issues
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Parse and test answer
        props = self._parse_propositions(answer)
        if len(props) == 0:
            return 0.2
        
        G = self._build_graph(props)
        failure_rate = self._property_test(G)
        
        # Confidence inversely related to failures
        conf = (1.0 - failure_rate) * meta_conf
        
        # Cap at 0.85 unless very strong signal
        if conf > 0.85 and G.number_of_nodes() < 3:
            conf = 0.85
        
        return float(np.clip(conf, 0.0, 1.0))