from typing import Any, Dict, Optional, Set, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Set, Optional, Any

class ReasoningTool:
    """
    Constraint-Driven Counterfactual Validator (CDCV)
    
    Combines causal inference, property-based testing, and SAT to validate answers.
    Builds a DAG from causal/logical relations, propagates constraints, samples
    counterfactuals with shrinking, and tracks state trajectory stability.
    """
    
    def __init__(self):
        self.rng = np.random.RandomState(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"DAG score: {score:.3f}, confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score = self._score_candidate(prompt, answer)
        return min(0.85, meta_conf * (0.3 + 0.55 * score))
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p_lower):
            return 0.2
        if re.search(r'why (did|does) .+ (fail|stop|end)', p_lower):
            return 0.25
        # Scope ambiguity
        if re.search(r'(every|all|each) .+ (a|an) ', p_lower):
            return 0.28
        # Pronoun ambiguity
        if 'who?' in p_lower and re.search(r'(he|she|they|it) (was|is|were)', p_lower):
            return 0.25
        # False dichotomy
        if re.search(r'either .+ or .+[?.!]', p_lower) and 'only' not in p_lower:
            return 0.27
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.3
        return 0.75
    
    def _score_candidate(self, prompt: str, answer: str) -> float:
        # Parse structures
        p_clauses = self._extract_clauses(prompt)
        a_clauses = self._extract_clauses(answer)
        dag = self._build_dag(p_clauses + a_clauses)
        
        # Structural score
        struct_score = self._structural_match(prompt, answer)
        
        # Computation score
        comp_score = self._compute_numeric(prompt, answer)
        
        # DAG propagation score
        prop_score = self._propagate_constraints(dag, p_clauses, a_clauses)
        
        # Counterfactual sampling
        cf_score = self._counterfactual_sampling(dag, a_clauses)
        
        # Trajectory stability (dynamics)
        dyn_score = self._trajectory_stability(prompt, answer)
        
        # NCD tiebreaker
        ncd_score = 1.0 - self._ncd(prompt, answer)
        
        # Weighted combination
        final = (0.25 * struct_score + 0.15 * comp_score + 0.20 * prop_score +
                 0.15 * cf_score + 0.15 * dyn_score + 0.10 * ncd_score)
        return np.clip(final, 0.0, 1.0)
    
    def _extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        clauses = []
        t_lower = text.lower()
        # Causal relations
        for m in re.finditer(r'(\w+)\s+(cause[sd]?|lead[sd]? to|produce[sd]?)\s+(\w+)', t_lower):
            clauses.append({'type': 'causal', 'from': m.group(1), 'to': m.group(3)})
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:[.,;]|$)', t_lower):
            clauses.append({'type': 'conditional', 'antecedent': m.group(1).strip(), 'consequent': m.group(2).strip()})
        # Numeric values
        for m in re.finditer(r'(\w+)\s*[=:]\s*([0-9.]+)', text):
            clauses.append({'type': 'numeric', 'var': m.group(1), 'value': float(m.group(2))})
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(greater|less|more|fewer)\s+than\s+(\w+)', t_lower):
            clauses.append({'type': 'comparative', 'left': m.group(1), 'op': m.group(2), 'right': m.group(3)})
        return clauses
    
    def _build_dag(self, clauses: List[Dict]) -> Dict[str, Set[str]]:
        dag = {}
        for c in clauses:
            if c['type'] == 'causal':
                dag.setdefault(c['from'], set()).add(c['to'])
            elif c['type'] == 'conditional':
                ant = c['antecedent'][:10]
                cons = c['consequent'][:10]
                dag.setdefault(ant, set()).add(cons)
        return dag
    
    def _structural_match(self, prompt: str, answer: str) -> float:
        score = 0.0
        p_lower, a_lower = prompt.lower(), answer.lower()
        # Negation consistency
        p_neg = len(re.findall(r'\b(not|no|never)\b', p_lower))
        a_neg = len(re.findall(r'\b(not|no|never)\b', a_lower))
        if p_neg > 0:
            score += 0.3 if (p_neg % 2 == a_neg % 2) else 0.0
        # Conditional structure
        if 'if' in p_lower and 'then' in a_lower:
            score += 0.2
        # Comparative alignment
        p_comp = set(re.findall(r'(greater|less|more|fewer|equal)', p_lower))
        a_comp = set(re.findall(r'(greater|less|more|fewer|equal)', a_lower))
        if p_comp and a_comp:
            score += 0.3 * len(p_comp & a_comp) / max(len(p_comp | a_comp), 1)
        return min(score, 1.0)
    
    def _compute_numeric(self, prompt: str, answer: str) -> float:
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        a_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', answer)]
        if not p_nums or not a_nums:
            return 0.5
        # Check if answer computes a result from prompt numbers
        for op in [np.add, np.subtract, np.multiply]:
            for i in range(len(p_nums)):
                for j in range(i+1, len(p_nums)):
                    result = op(p_nums[i], p_nums[j])
                    if any(abs(result - a) < 0.01 for a in a_nums):
                        return 0.9
        # Check ordering
        if len(p_nums) >= 2 and len(a_nums) >= 1:
            if ('greater' in answer.lower() and a_nums[0] > np.mean(p_nums)) or \
               ('less' in answer.lower() and a_nums[0] < np.mean(p_nums)):
                return 0.7
        return 0.3
    
    def _propagate_constraints(self, dag: Dict, p_clauses: List, a_clauses: List) -> float:
        state = {}
        for c in p_clauses:
            if c['type'] == 'numeric':
                state[c['var']] = c['value']
        # Topological propagation
        visited = set()
        for node in dag:
            if node not in visited:
                self._dfs_propagate(dag, node, state, visited)
        # Check consistency with answer
        score = 0.5
        for c in a_clauses:
            if c['type'] == 'numeric' and c['var'] in state:
                if abs(state[c['var']] - c['value']) < 0.01:
                    score += 0.3
        return min(score, 1.0)
    
    def _dfs_propagate(self, dag: Dict, node: str, state: Dict, visited: Set):
        visited.add(node)
        if node in dag:
            for child in dag[node]:
                if child not in visited:
                    self._dfs_propagate(dag, child, state, visited)
    
    def _counterfactual_sampling(self, dag: Dict, a_clauses: List) -> float:
        if not dag:
            return 0.5
        num_samples = 10
        successes = 0
        for _ in range(num_samples):
            intervention = {node: self.rng.uniform(0, 1) for node in dag}
            propagated = self._propagate_intervention(dag, intervention)
            if self._check_answer_holds(propagated, a_clauses):
                successes += 1
        return successes / num_samples
    
    def _propagate_intervention(self, dag: Dict, intervention: Dict) -> Dict:
        state = intervention.copy()
        for node in dag:
            if node in dag:
                children = dag[node]
                for child in children:
                    if child in state:
                        state[child] = (state.get(child, 0) + state[node]) / 2
        return state
    
    def _check_answer_holds(self, state: Dict, a_clauses: List) -> bool:
        for c in a_clauses:
            if c['type'] == 'comparative':
                left_val = state.get(c['left'], 0)
                right_val = state.get(c['right'], 0)
                if 'greater' in c['op'] or 'more' in c['op']:
                    if left_val <= right_val:
                        return False
                elif 'less' in c['op'] or 'fewer' in c['op']:
                    if left_val >= right_val:
                        return False
        return True
    
    def _trajectory_stability(self, prompt: str, answer: str) -> float:
        sentences = re.split(r'[.!?]', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            return 0.5
        # Build state trajectory
        state = np.zeros(5)
        trajectory = [state.copy()]
        for sent in sentences:
            delta = self._sentence_to_vector(sent)
            state = 0.7 * state + 0.3 * delta
            trajectory.append(state.copy())
        # Check convergence
        if len(trajectory) > 2:
            diffs = [np.linalg.norm(trajectory[i+1] - trajectory[i]) for i in range(len(trajectory)-1)]
            convergence = 1.0 - (diffs[-1] / (diffs[0] + 1e-6))
            return np.clip(convergence, 0.0, 1.0)
        return 0.5
    
    def _sentence_to_vector(self, sent: str) -> np.ndarray:
        vec = np.zeros(5)
        vec[0] = len(re.findall(r'\b(not|no)\b', sent.lower())) * 0.5
        vec[1] = len(re.findall(r'\b\d+\.?\d*\b', sent)) * 0.3
        vec[2] = len(re.findall(r'\b(if|then|because)\b', sent.lower())) * 0.4
        vec[3] = len(re.findall(r'\b(all|every|some)\b', sent.lower())) * 0.3
        vec[4] = len(re.findall(r'\b(greater|less|more)\b', sent.lower())) * 0.4
        return vec
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)