"""
Quantum-Analogical Reasoning Tool with Cognitive Load Weighting

Treats prompt and candidates as relational graphs, computes quantum-like
superposition overlap, and weights by cognitive load theory principles.
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import (
    check_transitivity, solve_constraints, confidence_from_agreement,
    information_sufficiency, bayesian_update, entropy
)
import networkx as nx


class ReasoningTool:
    def __init__(self):
        self.relation_types = ['neg', 'comp', 'cond', 'causal', 'order', 'num']
        self.alpha = 1.5  # Extraneous load penalty
        self.beta = 2.0   # Germane load bonus
        
    def _parse_to_graph(self, text):
        """Parse text into directed graph with typed edges (relations)."""
        G = nx.DiGraph()
        text_lower = text.lower()
        
        # Extract noun phrases (simplified: words between relation markers)
        chunks = re.split(r'[.?!,;]', text)
        nodes = []
        edges = []
        
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
                
            # Negation relations
            if re.search(r'\bnot\b|\bno\b|\bnever\b|\bfalse\b', chunk):
                parts = re.split(r'\bnot\b|\bno\b|\bnever\b', chunk)
                if len(parts) >= 2:
                    edges.append((parts[0].strip(), parts[1].strip(), 'neg'))
            
            # Comparative relations
            if re.search(r'\bgreater|more|less|fewer|higher|lower|bigger|smaller\b', chunk):
                parts = re.split(r'\bthan\b', chunk)
                if len(parts) >= 2:
                    edges.append((parts[0].strip(), parts[1].strip(), 'comp'))
            
            # Conditional relations
            if re.search(r'\bif\b.*\bthen\b', chunk):
                match = re.search(r'if\s+(.+?)\s+then\s+(.+)', chunk)
                if match:
                    edges.append((match.group(1).strip(), match.group(2).strip(), 'cond'))
            
            # Causal relations
            if re.search(r'\bbecause\b|\bcauses?\b|\bleads? to\b|\bresults? in\b', chunk):
                parts = re.split(r'\bbecause\b|\bcauses?\b|\bleads? to\b|\bresults? in\b', chunk)
                if len(parts) >= 2:
                    edges.append((parts[0].strip(), parts[1].strip(), 'causal'))
            
            # Temporal order
            if re.search(r'\bbefore\b|\bafter\b|\bfirst\b|\bsecond\b|\bthen\b', chunk):
                parts = re.split(r'\bbefore\b|\bafter\b', chunk)
                if len(parts) >= 2:
                    edges.append((parts[0].strip(), parts[1].strip(), 'order'))
            
            # Numeric comparisons
            nums = re.findall(r'\d+\.?\d*', chunk)
            if len(nums) >= 2:
                edges.append((nums[0], nums[1], 'num'))
        
        # Build graph
        for src, tgt, rel_type in edges:
            if src and tgt:
                G.add_edge(src, tgt, relation=rel_type)
                
        return G
    
    def _graph_to_state_vector(self, G):
        """Convert graph to quantum-like state vector encoding relation types."""
        if len(G.nodes()) == 0:
            return np.zeros(len(self.relation_types))
        
        # Count relation types
        relation_counts = defaultdict(int)
        for _, _, data in G.edges(data=True):
            rel = data.get('relation', 'unknown')
            if rel in self.relation_types:
                relation_counts[rel] += 1
        
        # Build vector
        vec = np.array([relation_counts[r] for r in self.relation_types], dtype=float)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec
    
    def _compute_cognitive_load(self, prompt_graph, answer_graph):
        """Compute cognitive load factors from graph structure."""
        prompt_rels = set()
        for _, _, data in prompt_graph.edges(data=True):
            prompt_rels.add(data.get('relation', 'unknown'))
        
        answer_rels = set()
        for _, _, data in answer_graph.edges(data=True):
            answer_rels.add(data.get('relation', 'unknown'))
        
        if len(answer_rels) == 0:
            return 0.5
        
        # Extraneous: answer relations not in prompt
        extraneous = len(answer_rels - prompt_rels) / max(len(answer_rels), 1)
        
        # Intrinsic: prompt relations missing from answer
        intrinsic = len(prompt_rels - answer_rels) / max(len(prompt_rels), 1) if len(prompt_rels) > 0 else 0
        
        # Germane: productive overlap
        germane = 1.0 - extraneous - intrinsic
        germane = max(0, germane)
        
        load_factor = np.exp(-self.alpha * extraneous + self.beta * germane)
        return load_factor
    
    def _structural_similarity(self, G1, G2):
        """Compute structural similarity via quantum-like state overlap."""
        v1 = self._graph_to_state_vector(G1)
        v2 = self._graph_to_state_vector(G2)
        
        # Inner product (amplitude)
        overlap = np.dot(v1, v2)
        
        # Measurement probability (Born rule)
        prob = overlap ** 2
        
        return prob
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability markers."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why did .+ (fail|stop|end)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every .+ a ', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|it|they) (was|were|is|are)', prompt_lower) and 'who' in prompt_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', prompt_lower):
            if not re.search(r'(most|least|highest|lowest) \w+ (score|rating|measure)', prompt_lower):
                return 0.25
        
        # Unanswerable markers
        if re.search(r'(cannot be determined|not enough information|insufficient)', prompt_lower):
            return 0.15
        
        return 1.0  # No ambiguity detected
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using quantum-analogical-cognitive pipeline."""
        prompt_graph = self._parse_to_graph(prompt)
        results = []
        
        for candidate in candidates:
            answer_graph = self._parse_to_graph(candidate)
            
            # Quantum-like structural overlap
            similarity = self._structural_similarity(prompt_graph, answer_graph)
            
            # Cognitive load weighting
            load_factor = self._compute_cognitive_load(prompt_graph, answer_graph)
            
            # Combined score
            base_score = similarity * load_factor
            
            # Bayesian refinement: update prior based on structural evidence
            prior = 0.5
            # Likelihood: how well structure matches
            likelihood = similarity
            false_pos = 0.1
            posterior = bayesian_update(prior, likelihood, false_pos)
            
            # Final score combines measurement probability and Bayesian posterior
            score = 0.7 * base_score + 0.3 * posterior
            
            # NCD tiebreaker (max 10% influence)
            import zlib
            prompt_comp = len(zlib.compress(prompt.encode()))
            cand_comp = len(zlib.compress(candidate.encode()))
            combined_comp = len(zlib.compress((prompt + candidate).encode()))
            ncd = (combined_comp - min(prompt_comp, cand_comp)) / max(prompt_comp, cand_comp, 1)
            ncd_bonus = (1 - ncd) * 0.1
            
            score = 0.9 * score + ncd_bonus
            
            reasoning = f"Struct_sim={similarity:.3f}, Load={load_factor:.3f}, Bayes={posterior:.3f}"
            results.append({"candidate": candidate, "score": float(score), "reasoning": reasoning})
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and structural match."""
        # First check for prompt ambiguity
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate structural match
        prompt_graph = self._parse_to_graph(prompt)
        answer_graph = self._parse_to_graph(answer)
        
        # No structure detected -> uncertain
        if len(prompt_graph.edges()) == 0 and len(answer_graph.edges()) == 0:
            return 0.4
        
        similarity = self._structural_similarity(prompt_graph, answer_graph)
        load_factor = self._compute_cognitive_load(prompt_graph, answer_graph)
        
        # Base confidence on structural alignment
        struct_conf = similarity * load_factor
        
        # Cap confidence - never exceed 0.9 without definitive computation
        final_conf = min(0.85, struct_conf * meta_conf)
        
        # Boost if strong structural match
        if similarity > 0.8 and load_factor > 0.7:
            final_conf = min(0.9, final_conf * 1.1)
        
        return float(np.clip(final_conf, 0.0, 1.0))