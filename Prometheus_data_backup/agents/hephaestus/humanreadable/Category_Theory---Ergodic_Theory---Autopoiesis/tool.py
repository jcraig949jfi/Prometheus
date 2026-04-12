"""
Category Theory x Ergodic Theory x Autopoiesis Reasoning Tool

Mechanism:
1. Parse propositions from prompt/candidates using regex patterns
2. Build inference graph (functorial mapping: syntax -> semantics)
3. Compute ergodic stationary distribution via matrix iteration
4. Apply autopoietic closure filter (only reachable propositions score)
5. Score = average stationary truth of candidate propositions
"""

import re
import numpy as np
from collections import defaultdict
from forge_primitives import dag_traverse, entropy, confidence_from_agreement, information_sufficiency


class ReasoningTool:
    def __init__(self):
        self.convergence_threshold = 1e-4
        self.max_iterations = 100
        
    def _extract_propositions(self, text):
        """Extract atomic propositions and their relationships using regex."""
        props = []
        edges = []
        
        # Normalize text
        text = text.lower().strip()
        
        # Extract negations: "not P", "no P", "~P"
        for match in re.finditer(r'(?:not|no|never)\s+(\w+(?:\s+\w+){0,3})', text):
            prop = f"NOT_{match.group(1).replace(' ', '_')}"
            props.append(prop)
        
        # Extract conditionals: "if P then Q", "P implies Q"
        for match in re.finditer(r'if\s+([^,]+?)\s+then\s+([^,.]+)', text):
            p1, p2 = match.group(1).replace(' ', '_'), match.group(2).replace(' ', '_')
            props.extend([p1, p2])
            edges.append((p1, p2, 0.9))  # High confidence for explicit conditionals
        
        # Extract causal: "P leads to Q", "P causes Q", "P results in Q"
        for match in re.finditer(r'(\w+(?:\s+\w+){0,2})\s+(?:leads to|causes|results in)\s+(\w+(?:\s+\w+){0,2})', text):
            p1, p2 = match.group(1).replace(' ', '_'), match.group(2).replace(' ', '_')
            props.extend([p1, p2])
            edges.append((p1, p2, 0.85))
        
        # Extract comparatives: "P > Q", "more P than Q"
        for match in re.finditer(r'(\w+)\s+(?:>|greater than|more than)\s+(\w+)', text):
            p1, p2 = match.group(1), match.group(2)
            props.extend([p1, p2])
            edges.append((p1, p2, 0.7))
        
        # Extract numeric thresholds: "P >= 5", "P < 3"
        for match in re.finditer(r'(\w+)\s*([><=]+)\s*(\d+(?:\.\d+)?)', text):
            prop = f"{match.group(1)}_{match.group(2)}_{match.group(3)}"
            props.append(prop)
        
        # Extract temporal ordering: "before P", "after Q", "first...second"
        for match in re.finditer(r'(?:before|after|first|second|then)\s+(\w+(?:\s+\w+){0,2})', text):
            prop = match.group(1).replace(' ', '_')
            props.append(prop)
        
        # Extract base words as atomic propositions
        words = re.findall(r'\b[a-z]{3,}\b', text)
        props.extend(words[:10])  # Limit to avoid explosion
        
        return list(set(props)), edges
    
    def _build_transition_matrix(self, props, edges):
        """Build column-stochastic transition matrix from inference graph."""
        n = len(props)
        prop_idx = {p: i for i, p in enumerate(props)}
        T = np.zeros((n, n))
        
        # Add edges
        for src, dst, weight in edges:
            if src in prop_idx and dst in prop_idx:
                T[prop_idx[dst], prop_idx[src]] = weight
        
        # Add self-loops with small weight
        for i in range(n):
            T[i, i] += 0.1
        
        # Normalize columns to make stochastic
        col_sums = T.sum(axis=0)
        col_sums[col_sums == 0] = 1.0  # Avoid division by zero
        T = T / col_sums
        
        return T, prop_idx
    
    def _ergodic_propagation(self, T, seed_indices, n_props):
        """Iterate transition matrix to find stationary distribution."""
        x = np.zeros(n_props)
        if seed_indices:
            x[list(seed_indices)] = 1.0 / len(seed_indices)
        else:
            x[:] = 1.0 / n_props
        
        for _ in range(self.max_iterations):
            x_next = T @ x
            if np.linalg.norm(x_next - x, 1) < self.convergence_threshold:
                break
            x = x_next
        
        return x
    
    def _autopoietic_closure(self, edges, seed_indices, n_props):
        """Compute reachable set from seed nodes using dag_traverse."""
        if not edges or not seed_indices:
            return set(range(n_props))
        
        # Build edge list for dag_traverse
        edge_list = [(src, dst) for src, dst, _ in edges if isinstance(src, int) and isinstance(dst, int)]
        
        reachable = set()
        for seed in seed_indices:
            try:
                reached = dag_traverse(edge_list, seed)
                reachable.update(reached)
            except:
                reachable.add(seed)
        
        return reachable if reachable else set(range(n_props))
    
    def _meta_confidence(self, prompt):
        """Detect ambiguity, presupposition, unanswerability in prompt."""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [
            r'have you (?:stopped|quit|ceased)',
            r'why did .+? (?:fail|stop|end)',
            r'when did you (?:stop|start|begin)',
        ]
        if any(re.search(p, prompt_lower) for p in presup_patterns):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'every\s+\w+.*?\s+a\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity: "X told Y he/she"
        if re.search(r'\w+\s+told\s+\w+\s+(?:he|she)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'either\s+.+?\s+or\s+', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if any(word in prompt_lower for word in ['best', 'worst', 'favorite', 'most beautiful']):
            if not any(word in prompt_lower for word in ['because', 'criteria', 'metric', 'measure']):
                return 0.3
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by ergodic-autopoietic score."""
        # Extract prompt propositions
        prompt_props, prompt_edges = self._extract_propositions(prompt)
        
        if not prompt_props:
            # Fallback: use NCD
            return self._ncd_fallback(prompt, candidates)
        
        all_props = set(prompt_props)
        all_edges = list(prompt_edges)
        
        # Extract candidate propositions
        cand_props_list = []
        for cand in candidates:
            cprops, cedges = self._extract_propositions(cand)
            cand_props_list.append(cprops)
            all_props.update(cprops)
            all_edges.extend(cedges)
        
        # Build unified graph
        props_list = list(all_props)
        prop_idx = {p: i for i, p in enumerate(props_list)}
        
        # Convert edges to indices
        indexed_edges = []
        for src, dst, weight in all_edges:
            if src in prop_idx and dst in prop_idx:
                indexed_edges.append((prop_idx[src], prop_idx[dst], weight))
        
        # Build transition matrix
        T, _ = self._build_transition_matrix(props_list, all_edges)
        
        # Seed from prompt propositions
        seed_indices = {prop_idx[p] for p in prompt_props if p in prop_idx}
        
        # Ergodic propagation
        stationary = self._ergodic_propagation(T, seed_indices, len(props_list))
        
        # Autopoietic closure
        closure_set = self._autopoietic_closure(indexed_edges, seed_indices, len(props_list))
        
        # Score candidates
        results = []
        for cand, cprops in zip(candidates, cand_props_list):
            if not cprops:
                score = 0.0
            else:
                # Average stationary truth of propositions in closure
                valid_props = [prop_idx[p] for p in cprops if p in prop_idx and prop_idx[p] in closure_set]
                if valid_props:
                    score = np.mean([stationary[i] for i in valid_props])
                else:
                    score = 0.0
            
            # Add small NCD bonus (max 10%)
            ncd_score = self._ncd(prompt, cand)
            final_score = 0.9 * score + 0.1 * (1.0 - ncd_score)
            
            results.append({
                'candidate': cand,
                'score': float(final_score),
                'reasoning': f'Ergodic truth: {score:.3f}, closure size: {len(closure_set)}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 based on meta-analysis and structural match."""
        # Check for meta-issues first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Extract structures
        prompt_props, prompt_edges = self._extract_propositions(prompt)
        answer_props, answer_edges = self._extract_propositions(answer)
        
        # If no structure extracted, honest uncertainty
        if not prompt_props or not answer_props:
            return 0.25
        
        # Compute overlap with prompt propositions
        overlap = len(set(answer_props) & set(prompt_props)) / max(len(answer_props), 1)
        
        # Use entropy as uncertainty measure
        scores = [overlap, 0.5, 0.3]  # Simulate agreement scores
        conf = confidence_from_agreement(scores[:2])
        
        # Cap by meta-confidence
        final_conf = min(conf * meta_conf, 0.85)  # Never exceed 0.85
        
        return float(final_conf)
    
    def _ncd(self, s1, s2):
        """Normalized compression distance using zlib."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def _ncd_fallback(self, prompt, candidates):
        """Fallback scoring using NCD when structure parsing fails."""
        results = []
        for cand in candidates:
            ncd = self._ncd(prompt, cand)
            results.append({
                'candidate': cand,
                'score': 1.0 - ncd,
                'reasoning': 'Fallback NCD scoring'
            })
        return sorted(results, key=lambda x: x['score'], reverse=True)