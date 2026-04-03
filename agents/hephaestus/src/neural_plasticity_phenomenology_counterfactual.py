"""Neural Plasticity x Phenomenology x Counterfactual Reasoning Tool.

Combines:
- Neural Plasticity: Hebbian weight updates on logical graph
- Phenomenology: Bracketing to extract essential predicate-argument structure
- Counterfactual Reasoning: do-calculus intervention to test alternative worlds
"""

import re
import zlib
import numpy as np
from forge_primitives import (
    modus_ponens, check_transitivity, counterfactual_intervention,
    confidence_from_agreement, information_sufficiency, negate
)


class ReasoningTool:
    def __init__(self):
        self.eta = 0.01  # Hebbian learning rate
        self.tau = 0.1   # Pruning threshold
        
    def _parse_predicates(self, text: str) -> list[dict]:
        """Extract predicate-argument structure (phenomenological bracketing)."""
        text = text.lower()
        nodes = []
        # Negations
        for m in re.finditer(r'\b(not|no|never|n\'t)\s+(\w+)', text):
            nodes.append({'text': m.group(2), 'polarity': -1, 'type': 'predicate'})
        # Conditionals
        for m in re.finditer(r'\bif\s+([^,]+?)\s+then\s+([^.,]+)', text):
            ante, cons = m.group(1).strip(), m.group(2).strip()
            nodes.append({'text': ante, 'polarity': 1, 'type': 'antecedent'})
            nodes.append({'text': cons, 'polarity': 1, 'type': 'consequent', 'implies_from': ante})
        # Causals
        for m in re.finditer(r'(\w+(?:\s+\w+){0,3})\s+(because|leads to|results in|causes)\s+(\w+(?:\s+\w+){0,3})', text):
            nodes.append({'text': m.group(3).strip(), 'polarity': 1, 'type': 'cause'})
            nodes.append({'text': m.group(1).strip(), 'polarity': 1, 'type': 'effect', 'caused_by': m.group(3).strip()})
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(>|<|>=|<=|=|more than|less than|equals?)\s+(\w+)', text):
            nodes.append({'text': f"{m.group(1)} {m.group(2)} {m.group(3)}", 'polarity': 1, 'type': 'comparison'})
        # Basic predicates
        for m in re.finditer(r'\b(\w+)\s+(is|are|was|were|has|have)\s+(\w+)', text):
            nodes.append({'text': f"{m.group(1)}_{m.group(3)}", 'polarity': 1, 'type': 'predicate'})
        return nodes if nodes else [{'text': text[:50], 'polarity': 1, 'type': 'raw'}]
    
    def _build_graph(self, nodes: list[dict]) -> tuple[np.ndarray, list[tuple[str, str]]]:
        """Build adjacency matrix and edge list from parsed nodes."""
        n, A, edges = len(nodes), np.zeros((len(nodes), len(nodes))), []
        for i, ni in enumerate(nodes):
            for j, nj in enumerate(nodes):
                if i != j and (('implies_from' in nj and nj['implies_from'] == ni['text']) or
                              ('caused_by' in nj and nj['caused_by'] == ni['text'])):
                    A[i, j] = 1
                    edges.append((ni['text'], nj['text']))
        return A, edges
    
    def _hebbian_update(self, W: np.ndarray, A: np.ndarray, activation: np.ndarray) -> np.ndarray:
        """Apply Hebbian learning: neurons that fire together wire together."""
        delta = self.eta * (np.outer(activation, activation) * A)
        W_new = W + delta
        # Prune weak connections
        W_new[W_new < self.tau] = 0
        return W_new

    def _counterfactual_score(self, nodes: list[dict], edges: list[tuple[str, str]],
                              candidate: str) -> float:
        """Apply counterfactual intervention to test alternative scenarios."""
        if not edges:
            return 0.0

        # Build values dict from nodes
        values = {n['text']: 1.0 if n['polarity'] > 0 else 0.0 for n in nodes}
        candidate_nodes = self._parse_predicates(candidate)

        # Intervene on each candidate node and measure propagation
        scores = []
        for c_node in candidate_nodes:
            if c_node['text'] in values:
                # Counterfactual intervention
                cf_values = counterfactual_intervention(
                    edges, values, c_node['text'],
                    1.0 if c_node['polarity'] > 0 else 0.0
                )
                # Score = alignment of propagated values
                score = sum(cf_values.values()) / max(len(cf_values), 1)
                scores.append(score)

        return np.mean(scores) if scores else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/presupposition (Tier B epistemic honesty)."""
        p_lower = prompt.lower()

        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)', p_lower):
            return 0.2

        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', p_lower):
            return 0.25

        # Pronoun ambiguity with "who" question
        if 'who' in p_lower and re.search(r'\b(he|she|they|it)\b', p_lower):
            return 0.25

        # False dichotomy: "either A or B"
        if re.search(r'\beither\s+\w+\s+or\s+\w+', p_lower):
            return 0.3

        # Subjectivity markers
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p_lower):
            return 0.3

        # Unanswerability: "what is the answer" without context
        if len(prompt.split()) < 5:
            return 0.4

        return 1.0  # No ambiguity detected

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Evaluate candidates using neural plasticity + phenomenology + counterfactuals."""
        # Parse prompt into phenomenological structure
        prompt_nodes = self._parse_predicates(prompt)
        A, edges = self._build_graph(prompt_nodes)
        n = len(prompt_nodes)

        # Initialize Hebbian weight matrix
        W = np.ones_like(A, dtype=float)

        results = []
        for candidate in candidates:
            # Parse candidate
            cand_nodes = self._parse_predicates(candidate)

            # Activation vector: 1 if node appears in candidate (respecting polarity)
            activation = np.zeros(n)
            for i, p_node in enumerate(prompt_nodes):
                for c_node in cand_nodes:
                    if p_node['text'] in c_node['text'] or c_node['text'] in p_node['text']:
                        if p_node['polarity'] == c_node['polarity']:
                            activation[i] = 1.0
                        else:
                            activation[i] = -0.5  # Polarity conflict

            # Update weights with Hebbian rule
            W = self._hebbian_update(W, A, np.abs(activation))

            # Score = match - conflict
            match = np.sum(W * np.outer(activation, activation) * np.eye(n))
            polarity_vec = np.array([p['polarity'] for p in prompt_nodes])
            conflict_activation = np.abs(polarity_vec - np.abs(activation))
            conflict = np.sum(W * np.outer(conflict_activation, conflict_activation) * np.eye(n))

            structural_score = match - 0.5 * conflict

            # Counterfactual reasoning score
            cf_score = self._counterfactual_score(prompt_nodes, edges, candidate)

            # NCD tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, candidate)

            # Combine: 60% structural, 30% counterfactual, 10% NCD
            final_score = 0.6 * structural_score + 0.3 * cf_score + 0.1 * ncd_score

            results.append({
                'candidate': candidate,
                'score': final_score,
                'reasoning': f"Structural={structural_score:.2f}, CF={cf_score:.2f}, NCD={ncd_score:.2f}"
            })

        # Normalize scores to [0, 1]
        if results:
            scores = [r['score'] for r in results]
            min_s, max_s = min(scores), max(scores)
            if max_s > min_s:
                for r in results:
                    r['score'] = (r['score'] - min_s) / (max_s - min_s)

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and structural match."""
        # Check for ambiguity first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf

        # Evaluate just this answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3

        # Cap confidence - never exceed 0.9 unless we computed something definitive
        base_conf = max(0.0, min(1.0, results[0]['score']))

        # Check if we have numeric computation
        if re.search(r'\d+\.?\d*\s*[<>=]+\s*\d+\.?\d*', prompt):
            # Numeric comparison detected - slightly higher confidence if parsed
            return min(0.85, base_conf * meta_conf)

        # Default: moderate confidence capped by meta
        return max(0.1, min(0.75, base_conf * meta_conf))
