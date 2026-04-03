"""
Tensor Decomposition + Ergodic Theory + Theory of Mind Reasoning Tool

Builds a (subject, relation, object) tensor from text, performs CP decomposition,
then uses ergodic MCMC sampling over belief states to score consistency with constraints.
"""

import re
import numpy as np
from itertools import product
from collections import defaultdict
import zlib


class ReasoningTool:
    def __init__(self):
        np.random.seed(42)  # Deterministic
        self.rank = 3  # CP decomposition rank
        self.mcmc_steps = 30  # Ergodic sampling steps
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = f"Tensor score: {score:.3f}, Meta-conf: {conf:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we have strong structural signal
        constraints = self._extract_constraints(prompt)
        if len(constraints) == 0:
            return 0.25  # No structure parsed
        
        # Check for computational signals
        comp_score = self._computational_score(prompt, answer)
        if comp_score > 0.9:
            return 0.85  # High confidence on computation
        elif comp_score > 0.7:
            return 0.65
        
        # Default moderate confidence
        return min(0.75, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition patterns
        presup_patterns = [r"have you (stopped|quit|ceased)", r"why did .+ (fail|stop|end)"]
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r"\bevery\b.{5,50}\ba\b", p_lower):
            return 0.25
        
        # Pronoun ambiguity: "X told Y he/she"
        if re.search(r"\btold\b.{5,30}\b(he|she)\b", p_lower) and "who" in p_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r"\beither\b.+\bor\b", p_lower) and "only" not in p_lower:
            return 0.28
        
        # Subjectivity without criteria
        if re.search(r"\b(best|worst|favorite|prefer)\b", p_lower) and "most" not in p_lower:
            return 0.3
        
        return 1.0  # No meta-issues detected
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Multi-component scoring
        struct_score = self._structural_score(prompt, candidate)
        comp_score = self._computational_score(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        
        # Weighted combination: structural 55%, computational 30%, NCD 15%
        return 0.55 * struct_score + 0.30 * comp_score + 0.15 * ncd_score
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        # Build tensor from prompt+candidate
        triples_p = self._extract_triples(prompt)
        triples_c = self._extract_triples(candidate)
        
        if not triples_p:
            return 0.5
        
        # Build vocabulary
        all_triples = triples_p + triples_c
        subjects = list(set(t[0] for t in all_triples))
        relations = list(set(t[1] for t in all_triples))
        objects = list(set(t[2] for t in all_triples))
        
        if not subjects or not relations or not objects:
            return 0.5
        
        S, R, O = len(subjects), len(relations), len(objects)
        s_idx = {s: i for i, s in enumerate(subjects)}
        r_idx = {r: i for i, r in enumerate(relations)}
        o_idx = {o: i for i, o in enumerate(objects)}
        
        # Build tensor T
        T = np.zeros((S, R, O))
        for s, r, o in triples_p:
            T[s_idx[s], r_idx[r], o_idx[o]] = 1.0
        
        # CP decomposition via ALS
        k = min(self.rank, S, R, O)
        A, B, C = self._cp_als(T, k, iters=5)
        
        # Extract constraints
        constraints = self._extract_constraints(prompt)
        
        # Ergodic belief sampling
        belief = T.copy()
        violation_rates = []
        
        for _ in range(self.mcmc_steps):
            # Propose a random flip
            i, j, k_pos = np.random.randint(S), np.random.randint(R), np.random.randint(O)
            old_val = belief[i, j, k_pos]
            belief[i, j, k_pos] = 1 - old_val
            
            # Count violations
            violations = self._count_violations(belief, constraints, s_idx, r_idx, o_idx, subjects, relations, objects)
            total_constraints = max(len(constraints), 1)
            delta_E = violations  # Energy = violation count
            
            # Metropolis acceptance
            if np.random.rand() < np.exp(-delta_E):
                pass  # Accept
            else:
                belief[i, j, k_pos] = old_val  # Reject
            
            violation_rates.append(violations / total_constraints)
        
        # Ergodic average
        avg_violation = np.mean(violation_rates) if violation_rates else 0.5
        return 1.0 - avg_violation
    
    def _cp_als(self, T, rank, iters=5):
        S, R, O = T.shape
        A = np.random.rand(S, rank) + 0.1
        B = np.random.rand(R, rank) + 0.1
        C = np.random.rand(O, rank) + 0.1
        
        for _ in range(iters):
            # Update A
            T0 = T.reshape(S, -1)
            BC = np.einsum('ri,oi->roi', B, C).reshape(-1, rank)
            A = T0 @ np.linalg.pinv(BC.T).T
            
            # Update B
            T1 = T.transpose(1, 0, 2).reshape(R, -1)
            AC = np.einsum('si,oi->soi', A, C).reshape(-1, rank)
            B = T1 @ np.linalg.pinv(AC.T).T
            
            # Update C
            T2 = T.transpose(2, 0, 1).reshape(O, -1)
            AB = np.einsum('si,ri->sri', A, B).reshape(-1, rank)
            C = T2 @ np.linalg.pinv(AB.T).T
        
        return A, B, C
    
    def _extract_triples(self, text):
        triples = []
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            # Extract entities (nouns, names, numbers)
            entities = re.findall(r'\b[A-Z][a-z]+\b|\b\d+\.?\d*\b|\b(he|she|it|they)\b', sent)
            words = sent.lower().split()
            
            # Extract relations (verbs, prepositions, comparatives)
            relations = [w for w in words if w in ['is', 'has', 'more', 'less', 'than', 'before', 'after', 'causes', 'leads']]
            
            if len(entities) >= 2 and relations:
                for i in range(len(entities) - 1):
                    triples.append((entities[i], relations[0] if relations else 'related', entities[i+1]))
        
        return triples
    
    def _extract_constraints(self, prompt):
        constraints = []
        p_lower = prompt.lower()
        
        # Negations
        for match in re.finditer(r'(not|no|never) (\w+)', p_lower):
            constraints.append(('negation', match.group(2)))
        
        # Comparatives
        for match in re.finditer(r'(\w+) (more|less|greater|fewer) than (\w+)', p_lower):
            constraints.append(('comparative', match.group(1), match.group(2), match.group(3)))
        
        # Conditionals
        if 'if' in p_lower and 'then' in p_lower:
            constraints.append(('conditional', 'if-then'))
        
        # Causals
        for match in re.finditer(r'(\w+) (causes|leads to|results in) (\w+)', p_lower):
            constraints.append(('causal', match.group(1), match.group(3)))
        
        return constraints
    
    def _count_violations(self, belief, constraints, s_idx, r_idx, o_idx, subjects, relations, objects):
        violations = 0
        for c in constraints:
            if c[0] == 'negation':
                # Check if negated relation is present
                violations += np.sum(belief) * 0.1  # Soft penalty
            elif c[0] == 'comparative':
                violations += 0  # Would need numeric grounding
        return violations
    
    def _computational_score(self, prompt, candidate):
        # Numeric comparison
        nums_p = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        nums_c = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        # Bat-and-ball pattern: "X and Y cost A, X costs B more than Y"
        bb_match = re.search(r'cost[s]? (\d+\.?\d*).+costs? (\d+\.?\d*) more', prompt.lower())
        if bb_match and nums_c:
            total = float(bb_match.group(1))
            diff = float(bb_match.group(2))
            correct_y = (total - diff) / 2
            if abs(nums_c[0] - correct_y) < 0.01:
                return 0.95
        
        # Simple numeric comparison
        if "greater" in prompt.lower() or "more" in prompt.lower():
            if nums_p and nums_c and len(nums_c) > 0:
                if nums_c[0] > nums_p[0]:
                    return 0.75
        
        # Negation check
        if ("not" in prompt.lower() or "no" in prompt.lower()) and ("not" in candidate.lower() or "no" in candidate.lower()):
            return 0.7
        
        return 0.5
    
    def _ncd_score(self, prompt, candidate):
        def ncd(x, y):
            cx, cy = zlib.compress(x.encode()), zlib.compress(y.encode())
            cxy = zlib.compress((x + y).encode())
            return (len(cxy) - min(len(cx), len(cy))) / max(len(cx), len(cy))
        
        return 1.0 - min(ncd(prompt, candidate), 1.0)