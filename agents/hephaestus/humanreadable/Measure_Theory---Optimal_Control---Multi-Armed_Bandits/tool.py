from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines measure theory, optimal control, and multi-armed bandits for logical reasoning.
    
    Extracts propositions from candidates, assigns belief masses, detects logical conflicts,
    and uses dynamic programming to minimize inconsistency cost J(x). UCB-based bandit
    selection focuses computation on uncertain propositions.
    """
    
    def __init__(self):
        self.lambda_penalty = 0.5
        self.beta_ucb = 1.0
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            props = self._extract_propositions(cand)
            if not props:
                score = self._ncd_score(prompt, cand)
            else:
                J_star = self._optimal_control_dp(props, prompt)
                score = np.exp(-J_star)
            
            reasoning = self._explain_score(prompt, cand, props)
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        props = self._extract_propositions(answer)
        if not props:
            return 0.3
        
        J_star = self._optimal_control_dp(props, prompt)
        base_conf = np.exp(-J_star)
        
        return min(meta_conf, base_conf * 0.85)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'\bhave you (stopped|quit|ceased)', r'\bwhy did .+ (fail|stop)',
                          r'\bwhen did you (stop|quit)', r'\bstill .+ing']
        if any(re.search(pat, p_lower) for pat in presup_patterns):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|criteria|measure)\b', p_lower):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'\b(impossible|cannot determine|insufficient|ambiguous)\b', p_lower):
            return 0.2
        
        return 0.7
    
    def _extract_propositions(self, text: str) -> List[Dict]:
        props = []
        
        # Numeric comparisons
        num_pattern = r'([\d.]+)\s*(>|<|>=|<=|=|equals?)\s*([\d.]+)'
        for m in re.finditer(num_pattern, text):
            props.append({
                'type': 'numeric',
                'left': float(m.group(1)),
                'op': m.group(2),
                'right': float(m.group(3)),
                'text': m.group(0)
            })
        
        # Negations
        neg_pattern = r'\b(not|no|never|n\'t)\s+(\w+(?:\s+\w+){0,3})'
        for m in re.finditer(neg_pattern, text.lower()):
            props.append({'type': 'negation', 'target': m.group(2), 'text': m.group(0)})
        
        # Conditionals
        cond_pattern = r'\bif\s+(.+?)\s+then\s+(.+?)(?:\.|$)'
        for m in re.finditer(cond_pattern, text.lower()):
            props.append({'type': 'conditional', 'antecedent': m.group(1), 'consequent': m.group(2), 'text': m.group(0)})
        
        # Causals
        causal_pattern = r'(\w+(?:\s+\w+){0,3})\s+(causes?|leads? to|results? in|produces?)\s+(\w+(?:\s+\w+){0,3})'
        for m in re.finditer(causal_pattern, text.lower()):
            props.append({'type': 'causal', 'cause': m.group(1), 'effect': m.group(3), 'text': m.group(0)})
        
        # Comparatives
        comp_pattern = r'(\w+)\s+(?:is\s+)?(more|less|greater|smaller|taller|shorter)\s+(?:than\s+)?(\w+)'
        for m in re.finditer(comp_pattern, text.lower()):
            props.append({'type': 'comparative', 'subject': m.group(1), 'relation': m.group(2), 'object': m.group(3), 'text': m.group(0)})
        
        # Temporal ordering
        temp_pattern = r'(\w+)\s+(before|after|precedes?|follows?)\s+(\w+)'
        for m in re.finditer(temp_pattern, text.lower()):
            props.append({'type': 'temporal', 'first': m.group(1), 'relation': m.group(2), 'second': m.group(3), 'text': m.group(0)})
        
        return props
    
    def _compute_conflicts(self, props: List[Dict], prompt: str) -> np.ndarray:
        n = len(props)
        C = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                if self._conflicts(props[i], props[j]):
                    C[i, j] = 1
                    C[j, i] = 1
        
        return C
    
    def _conflicts(self, p1: Dict, p2: Dict) -> bool:
        # Numeric conflicts
        if p1['type'] == 'numeric' and p2['type'] == 'numeric':
            if p1['left'] == p2['left'] and p1['right'] == p2['right']:
                if (p1['op'] in ['>', '>='] and p2['op'] in ['<', '<=']) or \
                   (p1['op'] in ['<', '<='] and p2['op'] in ['>', '>=']):
                    return True
        
        # Negation conflicts
        if p1['type'] == 'negation' and p2['type'] != 'negation':
            if p1['target'] in p2.get('text', ''):
                return True
        
        # Comparative transitivity
        if p1['type'] == 'comparative' and p2['type'] == 'comparative':
            if p1['object'] == p2['subject'] and p1['subject'] == p2['object']:
                if p1['relation'] in ['more', 'greater', 'taller'] and p2['relation'] in ['more', 'greater', 'taller']:
                    return True
        
        return False
    
    def _optimal_control_dp(self, props: List[Dict], prompt: str) -> float:
        n = len(props)
        if n == 0:
            return 1.0
        
        # Initialize belief masses
        m = np.ones(n) * 0.5
        
        # Compute conflict matrix
        C = self._compute_conflicts(props, prompt)
        
        # UCB-based bandit selection
        for _ in range(min(10, n)):
            sigma = np.sqrt(m * (1 - m))
            c_i = C.sum(axis=1) / (n + 1)
            ucb = -c_i + self.beta_ucb * sigma
            arm = np.argmax(ucb)
            
            # Update belief (simple Bayesian)
            conflict_count = C[arm].sum()
            m[arm] = max(0.1, m[arm] - 0.1 * conflict_count / n)
        
        # Dynamic programming to minimize J(x)
        # Simplified: greedy assignment
        x = np.zeros(n)
        for i in np.argsort(-m):
            cost_accept = (C[i] * x).sum() + self.lambda_penalty * (1 - m[i])
            cost_reject = 0
            if cost_accept < cost_reject + 0.5:
                x[i] = 1
        
        # Compute final cost
        J = 0
        for i in range(n):
            for j in range(i+1, n):
                J += C[i, j] * abs(x[i] - x[j])
            J += self.lambda_penalty * (1 - m[i]) * x[i]
        
        return J
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        cx = len(zlib.compress(candidate.encode()))
        cy = len(zlib.compress(prompt.encode()))
        cxy = len(zlib.compress((prompt + candidate).encode()))
        ncd = (cxy - min(cx, cy)) / max(cx, cy)
        return max(0.1, 1 - ncd)
    
    def _explain_score(self, prompt: str, cand: str, props: List[Dict]) -> str:
        if not props:
            return "No logical propositions extracted; using baseline scoring"
        return f"Extracted {len(props)} propositions; minimized inconsistency cost"