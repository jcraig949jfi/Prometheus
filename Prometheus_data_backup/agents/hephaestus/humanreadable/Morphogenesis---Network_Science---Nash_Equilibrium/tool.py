from typing import Dict, Set, Tuple

"""
Reaction-Diffusion Best-Response Scorer (RD-BRS)

Combines morphogenesis (reaction-diffusion), network science (graph propagation),
and game theory (Nash equilibrium) to score logical consistency.

Core mechanism:
1. Parse prompt into proposition graph with support/contradiction edges
2. Initialize activations with prompt bias
3. Iterate reaction-diffusion dynamics until Nash equilibrium
4. Score candidates by mean activation of their propositions
"""

import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

try:
    from forge_primitives import (
        check_transitivity, modus_ponens, negate,
        bayesian_update, entropy, solve_constraints,
        information_sufficiency, confidence_from_agreement
    )
    PRIMITIVES_AVAILABLE = True
except ImportError:
    PRIMITIVES_AVAILABLE = False


class ReasoningTool:
    def __init__(self):
        self.diffusion_rate = 0.3
        self.reaction_gain = 2.0
        self.sigmoid_steepness = 1.0
        self.max_iterations = 50
        self.epsilon = 1e-4
        
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-self.sigmoid_steepness * x))
    
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions from text."""
        text = text.lower()
        # Split on sentence boundaries and common separators
        props = re.split(r'[.!?;]|\s+and\s+|\s+or\s+|\s+but\s+', text)
        props = [p.strip() for p in props if len(p.strip()) > 5]
        return props
    
    def _parse_relations(self, text: str) -> List[Tuple[str, str, float]]:
        """Parse logical relations: (prop1, prop2, weight)."""
        text = text.lower()
        relations = []
        
        # Negation patterns (contradiction)
        negations = re.findall(r'(not\s+(\w+)|no\s+(\w+))', text)
        
        # Conditionals (support)
        conditionals = re.findall(r'if\s+([^,]+?)\s+then\s+([^,.]+)', text)
        for ant, cons in conditionals:
            relations.append((ant.strip(), cons.strip(), 0.8))
        
        # Causal (strong support)
        causals = re.findall(r'([^,]+?)\s+(?:because|leads to|results in|causes)\s+([^,.]+)', text)
        for cause, effect in causals:
            relations.append((cause.strip(), effect.strip(), 0.9))
        
        # Comparatives (can be contradiction or support)
        comparatives = re.findall(r'(\S+)\s+(?:greater than|less than|>|<)\s+(\S+)', text)
        
        return relations
    
    def _build_graph(self, prompt: str, candidates: List[str]) -> Tuple[Dict, np.ndarray, np.ndarray]:
        """Build adjacency matrix and bias vector."""
        all_text = prompt + " " + " ".join(candidates)
        props = self._extract_propositions(all_text)
        prompt_props = set(self._extract_propositions(prompt))
        
        if not props:
            props = [prompt] + candidates
            prompt_props = {prompt}
        
        prop2idx = {p: i for i, p in enumerate(props)}
        n = len(props)
        
        A = np.zeros((n, n))
        b = np.zeros(n)
        
        # Set bias for prompt propositions
        for p in prompt_props:
            if p in prop2idx:
                b[prop2idx[p]] = 1.0
        
        # Parse relations and build adjacency
        relations = self._parse_relations(prompt + " " + " ".join(candidates))
        for p1, p2, weight in relations:
            if p1 in prop2idx and p2 in prop2idx:
                i, j = prop2idx[p1], prop2idx[p2]
                A[j, i] = weight  # p1 influences p2
        
        # Self-loops for stability
        np.fill_diagonal(A, 0.5)
        
        return prop2idx, A, b
    
    def _reaction_diffusion(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Run reaction-diffusion dynamics to Nash equilibrium."""
        n = A.shape[0]
        x = b.copy()
        
        for _ in range(self.max_iterations):
            # Diffusion: spread activation across graph
            diffusion = A @ x
            x_temp = x + self.diffusion_rate * (diffusion - x)
            
            # Reaction: nonlinear best-response update
            x_new = self._sigmoid(self.reaction_gain * (x_temp + b))
            
            # Check convergence
            if np.sum(np.abs(x_new - x)) < self.epsilon:
                break
            
            x = x_new
        
        return x
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability patterns."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did \w+ (?:fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery \w+.*?\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|it)\b', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+\b', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower):
            return 0.35
        
        # Question marks without sufficient info
        if '?' in prompt and len(prompt.split()) < 8:
            return 0.4
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score candidates by equilibrium activation."""
        if not candidates:
            return []
        
        prop2idx, A, b = self._build_graph(prompt, candidates)
        x_eq = self._reaction_diffusion(A, b)
        
        results = []
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            if not cand_props:
                cand_props = [cand]
            
            # Structural score: mean activation
            cand_indices = [prop2idx[p] for p in cand_props if p in prop2idx]
            if cand_indices:
                struct_score = float(np.mean(x_eq[cand_indices]))
            else:
                struct_score = 0.5
            
            # NCD tiebreaker (max 10% weight)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combined score: 85% structural, 15% NCD
            final_score = 0.85 * struct_score + 0.15 * ncd_score
            
            reasoning = f"Equilibrium activation: {struct_score:.3f}, NCD: {ncd_score:.3f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.4:
            return meta_conf
        
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        base_conf = results[0]["score"]
        
        # Cap confidence unless definitive
        if base_conf > 0.9:
            base_conf = 0.85
        
        return min(base_conf * meta_conf, 0.95)