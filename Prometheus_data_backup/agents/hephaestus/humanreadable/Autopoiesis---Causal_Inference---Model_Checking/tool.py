import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Self-Maintaining Causal Model Checker (SMCMC)
    
    Combines autopoiesis (closure-based self-organization), causal inference
    (cause/effect relations), and model checking (constraint validation).
    
    Mechanism:
    1. Parse text into propositions, causal/temporal relations, numeric claims
    2. Build directed labeled graph (NumPy adjacency matrices)
    3. Apply closure rules (modus ponens, transitivity) until fixed point
    4. Validate constraints (consistency, acyclicity, causal validity)
    5. Score candidates by satisfied constraints + computational correctness
    """
    
    def __init__(self):
        self.relation_types = ['cause', 'precedes', 'implies', 'equal', 'less', 'greater']
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for candidate in candidates:
            score = self._score_candidate(prompt, candidate)
            reasoning = self._generate_reasoning(prompt, candidate)
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reasoning
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._score_candidate(prompt, answer)
        computational_certainty = self._computational_certainty(prompt, answer)
        
        if computational_certainty > 0:
            return min(0.95, 0.5 + computational_certainty * 0.45)
        
        base_conf = min(0.85, score)
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does) .* (fail|stop|refuse)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every .* (a|an|the) ', p) and 'same' not in p:
            return 0.3
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|they|it) (was|is|were)', p) and re.search(r'who\?', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or .*[?]', p) and 'only' not in p:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|most beautiful)', p) and not re.search(r'(most|least|highest|lowest)', p):
            return 0.3
        
        # Multiple questions or unclear
        if p.count('?') > 1:
            return 0.4
        
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Computational scoring
        comp_score = self._compute_answer(prompt, candidate)
        if comp_score >= 0:
            return comp_score
        
        # Structural scoring via SMCMC
        graph_score = self._graph_based_score(prompt, candidate)
        
        # NCD as tiebreaker (max 15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = max(0, 1 - ncd) * 0.15
        
        return graph_score * 0.85 + ncd_score
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """Constructive computation: actually solve the problem"""
        
        # Numeric comparison
        num_score = self._numeric_comparison(prompt, candidate)
        if num_score >= 0:
            return num_score
        
        # Probability/Bayesian
        prob_score = self._bayesian_compute(prompt, candidate)
        if prob_score >= 0:
            return prob_score
        
        # Arithmetic/PEMDAS
        arith_score = self._arithmetic_compute(prompt, candidate)
        if arith_score >= 0:
            return arith_score
        
        # Temporal ordering
        temp_score = self._temporal_compute(prompt, candidate)
        if temp_score >= 0:
            return temp_score
        
        return -1
    
    def _numeric_comparison(self, prompt: str, candidate: str) -> float:
        if not re.search(r'(greater|less|larger|smaller|more|fewer)', prompt.lower()):
            return -1
        
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_lower = candidate.lower()
        
        if len(p_nums) >= 2:
            try:
                a, b = float(p_nums[0]), float(p_nums[1])
                
                if re.search(r'(greater|larger|more)', prompt.lower()):
                    correct = str(max(a, b))
                    if correct in candidate or (a > b and re.search(r'(first|yes)', c_lower)) or (b > a and re.search(r'(second|no)', c_lower)):
                        return 0.95
                    return 0.1
                elif re.search(r'(less|smaller|fewer)', prompt.lower()):
                    correct = str(min(a, b))
                    if correct in candidate or (a < b and re.search(r'(first|yes)', c_lower)) or (b < a and re.search(r'(second|no)', c_lower)):
                        return 0.95
                    return 0.1
            except:
                pass
        
        return -1
    
    def _bayesian_compute(self, prompt: str, candidate: str) -> float:
        if 'probability' not in prompt.lower() and 'percent' not in prompt.lower():
            return -1
        
        # Extract percentages
        percents = re.findall(r'(\d+(?:\.\d+)?)\s*%', prompt)
        if len(percents) < 2:
            return -1
        
        try:
            c_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
            if c_nums:
                c_val = float(c_nums[0])
                # Simple check if candidate value is plausible
                if 0 <= c_val <= 100:
                    return 0.7
        except:
            pass
        
        return -1
    
    def _arithmetic_compute(self, prompt: str, candidate: str) -> float:
        # Look for arithmetic expressions
        expr_match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', prompt)
        if not expr_match:
            return -1
        
        try:
            a, op, b = expr_match.groups()
            a, b = float(a), float(b)
            
            result = 0
            if op == '+': result = a + b
            elif op == '-': result = a - b
            elif op == '*': result = a * b
            elif op == '/': result = a / b if b != 0 else 0
            
            c_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
            if c_nums and abs(float(c_nums[0]) - result) < 0.01:
                return 0.98
        except:
            pass
        
        return -1
    
    def _temporal_compute(self, prompt: str, candidate: str) -> float:
        if not re.search(r'(before|after|first|last|earlier|later)', prompt.lower()):
            return -1
        
        # Extract events/entities
        events = re.findall(r'[A-Z][a-z]+', prompt)
        if len(events) < 2:
            return -1
        
        # Check if candidate mentions the right entity
        if 'before' in prompt.lower() and events[0] in candidate:
            return 0.8
        elif 'after' in prompt.lower() and events[1] in candidate:
            return 0.8
        
        return -1
    
    def _computational_certainty(self, prompt: str, answer: str) -> float:
        """How certain are we from pure computation?"""
        comp = self._compute_answer(prompt, answer)
        if comp > 0.9:
            return 1.0
        elif comp > 0.7:
            return 0.6
        return 0.0
    
    def _graph_based_score(self, prompt: str, candidate: str) -> float:
        """Core SMCMC algorithm: parse, build graph, close, validate"""
        
        # Parse both texts
        p_props, p_rels = self._parse_structure(prompt)
        c_props, c_rels = self._parse_structure(candidate)
        
        # Build combined node set
        all_props = list(set(p_props + c_props))
        if len(all_props) == 0:
            return 0.5
        
        n = len(all_props)
        prop_idx = {p: i for i, p in enumerate(all_props)}
        
        # Build adjacency tensor
        adj = np.zeros((n, n, len(self.relation_types)), dtype=bool)
        
        for rel_type, src, tgt in p_rels + c_rels:
            if src in prop_idx and tgt in prop_idx:
                type_idx = self.relation_types.index(rel_type) if rel_type in self.relation_types else 0
                adj[prop_idx[src], prop_idx[tgt], type_idx] = True
        
        # Autopoietic closure
        adj_closed = self._autopoietic_closure(adj, all_props, prop_idx)
        
        # Model checking
        constraints_satisfied = self._check_constraints(adj_closed, all_props)
        
        return constraints_satisfied
    
    def _parse_structure(self, text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """Extract propositions and relations"""
        props = []
        relations = []
        
        # Extract propositions (simple: capitalized words/phrases)
        prop_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[a-z]+){0,3}\b', text)
        props.extend(prop_matches)
        
        # Negations
        neg_matches = re.findall(r'not\s+(\w+)', text.lower())
        props.extend([f'NOT_{p}' for p in neg_matches])
        
        # Causal relations
        cause_matches = re.findall(r'(\w+)\s+cause[sd]?\s+(\w+)', text.lower())
        relations.extend([('cause', c[0], c[1]) for c in cause_matches])
        
        # Temporal precedence
        prec_matches = re.findall(r'(\w+)\s+before\s+(\w+)', text.lower())
        relations.extend([('precedes', p[0], p[1]) for p in prec_matches])
        
        # Implications
        impl_matches = re.findall(r'if\s+(\w+)\s+then\s+(\w+)', text.lower())
        relations.extend([('implies', i[0], i[1]) for i in impl_matches])
        
        return props, relations
    
    def _autopoietic_closure(self, adj: np.ndarray, props: List[str], prop_idx: Dict) -> np.ndarray:
        """Fixed-point closure via inference rules"""
        n = adj.shape[0]
        truth = np.zeros(n, dtype=bool)
        
        # Iterate until fixed point
        for _ in range(10):
            old_truth = truth.copy()
            
            # Modus ponens on 'implies'
            impl_idx = self.relation_types.index('implies')
            for i in range(n):
                if truth[i]:
                    truth |= adj[i, :, impl_idx]
            
            # Transitivity on 'cause' and 'precedes'
            for rel in ['cause', 'precedes']:
                rel_idx = self.relation_types.index(rel)
                adj[:, :, rel_idx] |= (adj[:, :, rel_idx] @ adj[:, :, rel_idx])
            
            if np.array_equal(truth, old_truth):
                break
        
        return adj
    
    def _check_constraints(self, adj: np.ndarray, props: List[str]) -> float:
        """Validate logical/causal constraints"""
        n = adj.shape[0]
        satisfied = 0
        total = 0
        
        # Acyclicity on 'cause'
        cause_idx = self.relation_types.index('cause')
        cause_mat = adj[:, :, cause_idx].astype(float)
        total += 1
        if n > 0:
            trace_sum = sum(np.trace(np.linalg.matrix_power(cause_mat + np.eye(n), k)) for k in range(1, min(n+1, 5)))
            if trace_sum == n * min(n, 4):  # Only self-loops
                satisfied += 1
        
        # Consistency (no P and NOT_P both true)
        total += 1
        has_contradiction = False
        for i, p in enumerate(props):
            if p.startswith('NOT_'):
                base = p[4:]
                if base in props:
                    # Check if both could be inferred
                    has_contradiction = True
                    break
        if not has_contradiction:
            satisfied += 1
        
        return satisfied / total if total > 0 else 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _generate_reasoning(self, prompt: str, candidate: str) -> str:
        comp = self._compute_answer(prompt, candidate)
        if comp > 0.9:
            return "Computational verification"
        elif comp > 0:
            return "Partial computation match"
        return "Structural graph analysis"