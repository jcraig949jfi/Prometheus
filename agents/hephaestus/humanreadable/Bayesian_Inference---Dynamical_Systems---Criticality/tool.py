from typing import Dict, Tuple

"""
Bayesian Factor Graph Reasoning with Critical Temperature Selection

Combines:
1. Bayesian priors over candidate correctness
2. Loopy belief propagation (dynamical message passing)
3. Criticality tuning (find beta where variance peaks)

Extracts structural constraints, builds factor graph, runs BP until convergence,
selects critical beta, returns posteriors as scores.
"""
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple
from forge_primitives import (
    bayesian_update, solve_constraints, entropy,
    confidence_from_agreement, information_sufficiency
)


class ReasoningTool:
    def __init__(self):
        self.max_iterations = 30
        self.convergence_threshold = 1e-4
        self.beta_grid = np.logspace(-3, 2, 20)
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates via critical Bayesian factor graph."""
        n = len(candidates)
        if n == 0:
            return []
        
        # Extract constraints from prompt and candidates
        constraints = self._extract_constraints(prompt, candidates)
        
        # Uniform priors
        priors = np.ones(n) * 0.5
        
        # Find critical beta
        beta_critical = self._find_critical_beta(priors, constraints, n)
        
        # Run BP at critical beta
        posteriors = self._belief_propagation(priors, constraints, n, beta_critical)
        
        # Add NCD tiebreaker (max 10%)
        ncd_scores = self._ncd_scores(prompt, candidates)
        final_scores = 0.9 * posteriors + 0.1 * ncd_scores
        
        # Build results
        results = []
        for i, cand in enumerate(candidates):
            reasoning = self._explain_score(prompt, cand, constraints, posteriors[i])
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, with meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate against self
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.2
        
        base_score = results[0]["score"]
        
        # Never exceed 0.9 unless we computed a definitive answer
        constraints = self._extract_constraints(prompt, [answer])
        has_numeric = any(c[0] == 'numeric' for c in constraints)
        
        if has_numeric and base_score > 0.8:
            return min(0.85, base_score)
        
        return min(meta_conf, base_score * 0.85)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B reasoning traps."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) ', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|is|were|are)', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and not re.search(r'\b(because|since|criteria|metric)\b', p_lower):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(not enough information|cannot determine|ambiguous)\b', p_lower):
            return 0.25
        
        return 1.0
    
    def _extract_constraints(self, prompt: str, candidates: List[str]) -> List[Tuple]:
        """Extract logical/numeric constraints as (type, data) tuples."""
        constraints = []
        
        # Numeric comparisons
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', prompt):
            val1, op, val2 = float(match.group(1)), match.group(2), float(match.group(3))
            constraints.append(('numeric', {'val1': val1, 'op': op, 'val2': val2}))
        
        # Negations
        for i, cand in enumerate(candidates):
            if re.search(r'\b(not|no|never|false)\b', cand.lower()):
                constraints.append(('negation', {'candidate_idx': i}))
        
        # Conditionals (if-then)
        for match in re.finditer(r'if (.+?) then (.+?)[\.\,]', prompt.lower()):
            antecedent, consequent = match.group(1), match.group(2)
            constraints.append(('conditional', {'antecedent': antecedent, 'consequent': consequent}))
        
        # Temporal ordering
        for match in re.finditer(r'(.+?) (before|after|precedes) (.+?)[\.\,]', prompt.lower()):
            constraints.append(('temporal', {'event1': match.group(1), 'relation': match.group(2), 'event2': match.group(3)}))
        
        # Quantifiers
        for i, cand in enumerate(candidates):
            if re.search(r'\b(all|every|none|some)\b', cand.lower()):
                constraints.append(('quantifier', {'candidate_idx': i, 'text': cand}))
        
        return constraints
    
    def _belief_propagation(self, priors: np.ndarray, constraints: List[Tuple], n: int, beta: float) -> np.ndarray:
        """Run loopy BP with given beta."""
        if len(constraints) == 0:
            return priors
        
        # Initialize messages: msg[i][k] = message from candidate i to constraint k
        k = len(constraints)
        msg_to_constraint = np.ones((n, k))
        msg_to_candidate = np.ones((k, n))
        
        for iteration in range(self.max_iterations):
            old_msg_c = msg_to_constraint.copy()
            
            # Update messages to constraints
            for i in range(n):
                for k_idx in range(k):
                    # Collect messages from other constraints
                    incoming = np.prod([msg_to_candidate[other_k, i] for other_k in range(k) if other_k != k_idx])
                    msg_to_constraint[i, k_idx] = priors[i] * incoming
            
            # Update messages to candidates (from constraints)
            for k_idx in range(k):
                constraint = constraints[k_idx]
                for i in range(n):
                    # Compute factor potential
                    violation = self._compute_violation(constraint, i, n)
                    factor_potential = np.exp(-beta * violation)
                    
                    # Message is weighted by factor
                    msg_to_candidate[k_idx, i] = factor_potential * np.prod([msg_to_constraint[j, k_idx] for j in range(n) if j != i])
            
            # Check convergence
            if np.max(np.abs(msg_to_constraint - old_msg_c)) < self.convergence_threshold:
                break
        
        # Compute marginals
        posteriors = priors.copy()
        for i in range(n):
            posteriors[i] *= np.prod(msg_to_candidate[:, i])
        
        # Normalize
        posteriors = posteriors / (np.sum(posteriors) + 1e-10)
        return posteriors
    
    def _compute_violation(self, constraint: Tuple, candidate_idx: int, n: int) -> float:
        """Compute violation score for a constraint."""
        c_type, data = constraint
        
        if c_type == 'numeric':
            val1, op, val2 = data['val1'], data['op'], data['val2']
            if op in ['>', 'greater']:
                return 0.0 if val1 > val2 else 1.0
            elif op in ['<', 'less']:
                return 0.0 if val1 < val2 else 1.0
            elif op in ['=', 'equals', 'equal']:
                return (val1 - val2) ** 2
        
        elif c_type == 'negation':
            target_idx = data['candidate_idx']
            return 0.0 if candidate_idx != target_idx else 0.5
        
        return 0.0
    
    def _find_critical_beta(self, priors: np.ndarray, constraints: List[Tuple], n: int) -> float:
        """Find beta that maximizes susceptibility (variance)."""
        if len(constraints) == 0:
            return 1.0
        
        variances = []
        for beta in self.beta_grid:
            posteriors = self._belief_propagation(priors, constraints, n, beta)
            variance = np.var(posteriors)
            variances.append(variance)
        
        # Return beta at peak variance
        critical_idx = np.argmax(variances)
        return self.beta_grid[critical_idx]
    
    def _ncd_scores(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Normalized Compression Distance as tiebreaker."""
        def ncd(s1: str, s2: str) -> float:
            c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
        
        scores = np.array([1.0 - ncd(prompt, cand) for cand in candidates])
        return scores / (np.max(scores) + 1e-10)
    
    def _explain_score(self, prompt: str, candidate: str, constraints: List[Tuple], posterior: float) -> str:
        """Generate brief reasoning explanation."""
        n_constraints = len(constraints)
        if n_constraints == 0:
            return f"No structural constraints; prior-based score {posterior:.2f}"
        
        c_types = [c[0] for c in constraints]
        return f"BP posterior {posterior:.2f} from {n_constraints} constraints: {', '.join(set(c_types))}"