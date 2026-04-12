"""
Bandit-Guided Invariant Verifier (BGIV)

Combines Multi-Armed Bandits, Free Energy Principle, and Hoare Logic:
- Extract logical constraints from prompt (Hoare-style pre/postconditions)
- Treat each candidate as an arm inducing a state over constraints
- Score via free-energy error (distance from satisfying all constraints)
- Use UCB bandit to balance exploration/exploitation
- Primitives: modus_ponens, solve_constraints, entropy, confidence_from_agreement
"""

import re
import numpy as np
import zlib
from collections import defaultdict
from forge_primitives import (
    modus_ponens, solve_constraints, entropy, 
    confidence_from_agreement, information_sufficiency
)


class ReasoningTool:
    def __init__(self):
        self.budget = 20
        
    def _extract_constraints(self, prompt):
        """Parse prompt into Horn clauses (antecedent, consequent) and facts."""
        constraints = []
        facts = set()
        
        # Comparatives: X > Y, X < Y, X = Y
        for match in re.finditer(r'(\w+)\s*(>|<|=|>=|<=)\s*(\w+)', prompt):
            subj, op, obj = match.groups()
            constraints.append(('compare', op, subj, obj))
        
        # Conditionals: if A then B
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', prompt, re.I):
            ant, cons = match.groups()
            constraints.append(('implies', ant.strip(), cons.strip()))
        
        # Causal: A because B, A leads to B
        for match in re.finditer(r'(\w+)\s+because\s+(\w+)', prompt, re.I):
            cons, ant = match.groups()
            constraints.append(('implies', ant, cons))
        for match in re.finditer(r'(\w+)\s+leads to\s+(\w+)', prompt, re.I):
            ant, cons = match.groups()
            constraints.append(('implies', ant, cons))
        
        # Negations: not X, X is false
        for match in re.finditer(r'not\s+(\w+)|(\w+)\s+is\s+false', prompt, re.I):
            term = match.group(1) or match.group(2)
            constraints.append(('not', term))
        
        # Temporal: X before Y, X after Y
        for match in re.finditer(r'(\w+)\s+before\s+(\w+)', prompt, re.I):
            first, second = match.groups()
            constraints.append(('before', first, second))
        
        # Numeric literals
        for match in re.finditer(r'\b(\d+\.?\d*)\b', prompt):
            facts.add(('num', float(match.group(1))))
        
        return constraints, facts
    
    def _evaluate_constraints(self, constraints, facts, candidate):
        """Forward-chaining: compute which constraints are satisfied."""
        # Merge candidate into facts
        working_facts = facts.copy()
        
        # Extract entities from candidate
        for match in re.finditer(r'\b(\d+\.?\d*)\b', candidate):
            working_facts.add(('num', float(match.group(1))))
        
        # Extract propositions from candidate
        candidate_props = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        satisfied = np.zeros(len(constraints), dtype=bool)
        
        for i, cons in enumerate(constraints):
            if cons[0] == 'compare' and len(cons) == 4:
                op, subj, obj = cons[1], cons[2], cons[3]
                # Try to extract numbers for comparison
                subj_val = self._extract_number(subj, candidate)
                obj_val = self._extract_number(obj, candidate)
                if subj_val is not None and obj_val is not None:
                    if op == '>' and subj_val > obj_val:
                        satisfied[i] = True
                    elif op == '<' and subj_val < obj_val:
                        satisfied[i] = True
                    elif op in ('=', '==') and abs(subj_val - obj_val) < 1e-9:
                        satisfied[i] = True
                        
            elif cons[0] == 'implies' and len(cons) == 3:
                ant, conseq = cons[1].lower(), cons[2].lower()
                # Simple presence check (could use modus_ponens primitive)
                if ant in candidate.lower() or any(w in candidate_props for w in ant.split()):
                    if conseq in candidate.lower():
                        satisfied[i] = True
                        
            elif cons[0] == 'not' and len(cons) == 2:
                term = cons[1].lower()
                if term not in candidate.lower():
                    satisfied[i] = True
                    
            elif cons[0] == 'before' and len(cons) == 3:
                first, second = cons[1].lower(), cons[2].lower()
                first_pos = candidate.lower().find(first)
                second_pos = candidate.lower().find(second)
                if first_pos != -1 and second_pos != -1 and first_pos < second_pos:
                    satisfied[i] = True
        
        return satisfied
    
    def _extract_number(self, text, context):
        """Extract numeric value from text or context."""
        match = re.search(r'\d+\.?\d*', text)
        if match:
            return float(match.group())
        match = re.search(r'\b' + re.escape(text) + r'\s*[=:]\s*(\d+\.?\d*)', context, re.I)
        if match:
            return float(match.group(1))
        return None
    
    def _free_energy_error(self, state, goal):
        """Compute prediction error: ||state - goal||^2."""
        return np.sum((state.astype(float) - goal) ** 2)
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity, presupposition, and unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did \w+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*?\ba\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity + "who" question
        if re.search(r'\bhe\b|\bshe\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', prompt_lower):
            return 0.3
        
        # Insufficient info
        if re.search(r'\b(not enough|cannot determine|insufficient)', prompt_lower):
            return 0.25
        
        return 1.0  # No red flags
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        constraints, facts = self._extract_constraints(prompt)
        
        if len(constraints) == 0:
            # Fallback to NCD
            results = []
            for cand in candidates:
                score = 1.0 - self._ncd(prompt, cand)
                results.append({'candidate': cand, 'score': score, 'reasoning': 'NCD-fallback'})
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        goal = np.ones(len(constraints))
        n_arms = len(candidates)
        pulls = np.zeros(n_arms)
        rewards = np.zeros(n_arms)
        
        # UCB exploration
        for t in range(1, self.budget + 1):
            ucb_scores = np.zeros(n_arms)
            for i in range(n_arms):
                if pulls[i] == 0:
                    ucb_scores[i] = float('inf')
                else:
                    mu = rewards[i] / pulls[i]
                    ucb_scores[i] = mu + np.sqrt(2 * np.log(t) / pulls[i])
            
            arm = np.argmax(ucb_scores)
            state = self._evaluate_constraints(constraints, facts, candidates[arm])
            error = self._free_energy_error(state, goal)
            reward = -error  # Lower error = higher reward
            
            pulls[arm] += 1
            rewards[arm] += reward
        
        # Compute final scores
        results = []
        for i, cand in enumerate(candidates):
            if pulls[i] > 0:
                mu = rewards[i] / pulls[i]
            else:
                mu = -len(constraints)
            
            # Normalize and add small NCD component
            ncd_score = 1.0 - self._ncd(prompt, cand)
            final_score = 0.85 * (mu + len(constraints)) / (2 * len(constraints)) + 0.15 * ncd_score
            
            results.append({
                'candidate': cand,
                'score': max(0.0, min(1.0, final_score)),
                'reasoning': f'UCB-FE pulls={int(pulls[i])}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        constraints, facts = self._extract_constraints(prompt)
        
        if len(constraints) == 0:
            return 0.4 * meta_conf  # Honest uncertainty
        
        goal = np.ones(len(constraints))
        state = self._evaluate_constraints(constraints, facts, answer)
        satisfaction_rate = np.mean(state)
        
        # Never exceed 0.9 unless perfect satisfaction
        if satisfaction_rate >= 0.99:
            conf = 0.9
        elif satisfaction_rate >= 0.8:
            conf = 0.7
        elif satisfaction_rate >= 0.5:
            conf = 0.5
        else:
            conf = 0.3
        
        return min(conf, meta_conf)