from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Reasoning evaluator combining Cognitive Load Theory, Hoare Logic, and Sensitivity Analysis
    with dynamical state evolution tracking.
    
    Mechanism:
    1. Parse propositions (literals, comparatives, conditionals, causal)
    2. Build Hoare triples (P, C, Q) and propagate constraints
    3. Estimate cognitive load (intrinsic, extraneous, germane)
    4. Sensitivity analysis via perturbation
    5. Track state evolution dynamics for trajectory stability
    6. Meta-confidence for ambiguity detection
    """
    
    def __init__(self):
        self.weights = {'germane': 0.4, 'extraneous': 0.2, 'intrinsic': 0.2, 'sensitivity': 0.2}
    
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with unique IDs"""
        props = []
        pid = 0
        
        # Comparatives: A > B, A <= B, etc.
        for m in re.finditer(r'(\w+(?:\.\d+)?)\s*(>=|<=|>|<|=)\s*(\w+(?:\.\d+)?)', text):
            props.append({'id': pid, 'type': 'comparative', 'lhs': m.group(1), 
                         'op': m.group(2), 'rhs': m.group(3), 'polarity': 1})
            pid += 1
        
        # Conditionals: if X then Y
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|;|$)', text, re.I):
            props.append({'id': pid, 'type': 'conditional', 'lhs': m.group(1).strip(), 
                         'op': '=>', 'rhs': m.group(2).strip(), 'polarity': 1})
            pid += 1
        
        # Causal: X because Y, X leads to Y
        for m in re.finditer(r'(.+?)\s+(because|leads to|causes)\s+(.+?)(?:\.|,|;|$)', text, re.I):
            props.append({'id': pid, 'type': 'causal', 'lhs': m.group(1).strip(), 
                         'op': '=>', 'rhs': m.group(3).strip(), 'polarity': 1})
            pid += 1
        
        # Literals with negation
        for m in re.finditer(r'\b(not|no|never)\s+(\w+)', text, re.I):
            props.append({'id': pid, 'type': 'literal', 'lhs': m.group(2), 
                         'op': 'not', 'rhs': None, 'polarity': -1})
            pid += 1
        
        # Simple literals
        for m in re.finditer(r'\b([A-Z]\w*)\b', text):
            if not any(p['lhs'] == m.group(1) for p in props):
                props.append({'id': pid, 'type': 'literal', 'lhs': m.group(1), 
                             'op': 'is', 'rhs': None, 'polarity': 1})
                pid += 1
        
        return props[:50]  # Limit for performance
    
    def _constraint_propagation(self, props: List[Dict]) -> np.ndarray:
        """Hoare-style constraint propagation to derive closure"""
        n = len(props)
        if n == 0:
            return np.array([])
        
        T = np.zeros(n, dtype=bool)
        # Initialize with literals
        for i, p in enumerate(props):
            if p['type'] == 'literal' and p['polarity'] == 1:
                T[i] = True
        
        # Fixed-point iteration on implications
        changed = True
        iterations = 0
        while changed and iterations < 20:
            changed = False
            for i, p in enumerate(props):
                if p['op'] == '=>':
                    # Find antecedent
                    for j, q in enumerate(props):
                        if q['lhs'] == p['lhs'] and T[j]:
                            if not T[i]:
                                T[i] = True
                                changed = True
            iterations += 1
        
        return T
    
    def _cognitive_load(self, props: List[Dict], T: np.ndarray, goals: List[Dict]) -> Tuple[int, int, int]:
        """Estimate intrinsic, extraneous, germane load"""
        n = len(props)
        if n == 0:
            return 0, 0, 0
        
        # Intrinsic: distinct premises
        intrinsic = sum(1 for p in props if p['type'] in ['literal', 'comparative'])
        
        # Germane: derived propositions matching goals
        goal_strs = {g['lhs'] for g in goals}
        germane = sum(1 for i, p in enumerate(props) if T[i] and p['lhs'] in goal_strs)
        
        # Extraneous: propositions not contributing to derivation
        extraneous = 0
        for i in range(n):
            T_minus = T.copy()
            T_minus[i] = False
            if np.array_equal(T, T_minus):
                extraneous += 1
        
        return intrinsic, extraneous, germane
    
    def _sensitivity_analysis(self, props: List[Dict]) -> float:
        """Perturb numeric values and measure variance"""
        variances = []
        
        for p in props:
            if p['type'] == 'comparative':
                try:
                    val = float(p['rhs'])
                    epsilon = 1e-3 * abs(val) if val != 0 else 1e-3
                    perturbed = [val + epsilon, val - epsilon]
                    variances.append(np.var(perturbed))
                except:
                    pass
        
        return np.mean(variances) if variances else 0.0
    
    def _state_evolution(self, props: List[Dict], answer: str) -> float:
        """Track dynamical state evolution and measure trajectory stability"""
        n = len(props)
        if n == 0:
            return 0.5
        
        # State vector: truth values evolving over premise processing
        states = []
        state = np.zeros(n)
        
        # Process premises sequentially
        for i, p in enumerate(props):
            if p['type'] == 'literal' and p['polarity'] == 1:
                state[i] = 1.0
            elif p['type'] == 'comparative':
                state[i] = self._eval_comparative(p)
            states.append(state.copy())
        
        if len(states) < 2:
            return 0.5
        
        # Lyapunov stability: measure convergence
        deltas = [np.linalg.norm(states[i+1] - states[i]) for i in range(len(states)-1)]
        convergence_rate = np.mean(deltas) if deltas else 1.0
        
        # Perturbation robustness: shuffle premises and recompute
        stability_scores = []
        for _ in range(3):
            indices = np.random.permutation(n)
            perturbed_state = np.zeros(n)
            for idx in indices:
                if props[idx]['type'] == 'literal' and props[idx]['polarity'] == 1:
                    perturbed_state[idx] = 1.0
            stability_scores.append(np.dot(state, perturbed_state) / (np.linalg.norm(state) * np.linalg.norm(perturbed_state) + 1e-9))
        
        stability = np.mean(stability_scores)
        
        # Combine: low convergence rate + high stability = good
        return stability * (1.0 - min(convergence_rate, 1.0))
    
    def _eval_comparative(self, p: Dict) -> float:
        """Evaluate comparative propositions numerically"""
        try:
            lhs = float(p['lhs'])
            rhs = float(p['rhs'])
            op = p['op']
            if op == '>': return 1.0 if lhs > rhs else 0.0
            if op == '<': return 1.0 if lhs < rhs else 0.0
            if op == '>=': return 1.0 if lhs >= rhs else 0.0
            if op == '<=': return 1.0 if lhs <= rhs else 0.0
            if op == '=': return 1.0 if abs(lhs - rhs) < 1e-6 else 0.0
        except:
            pass
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability"""
        prompt_lower = prompt.lower()
        
        # Presupposition: "Have you stopped/quit X?"
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity: "X told Y he/she" + "who?"
        if re.search(r'\b(he|she)\b.*\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy: "Either A or B"
        if re.search(r'\beither\s+.+\bor\b.+', prompt_lower):
            return 0.3
        
        # Subjectivity: "best/worst/favorite"
        if re.search(r'\b(best|worst|favorite|better|worse)\b', prompt_lower):
            return 0.4
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined score"""
        prompt_props = self._parse_propositions(prompt)
        results = []
        
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            T = self._constraint_propagation(cand_props)
            
            intrinsic, extraneous, germane = self._cognitive_load(cand_props, T, prompt_props)
            sensitivity = self._sensitivity_analysis(cand_props)
            dynamics = self._state_evolution(cand_props, cand)
            ncd = 1.0 - self._ncd(prompt, cand)
            
            # Score composition: dynamics 40%, germane 30%, structural 20%, NCD 10%
            score = (0.4 * dynamics + 
                    0.3 * germane / max(len(prompt_props), 1) -
                    0.1 * extraneous -
                    0.1 * intrinsic / 10.0 -
                    0.05 * sensitivity +
                    0.1 * ncd)
            
            results.append({
                'candidate': cand,
                'score': max(0.0, min(1.0, score)),
                'reasoning': f"dynamics={dynamics:.2f} germane={germane} extran={extraneous} ncd={ncd:.2f}"
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and structural match"""
        meta_conf = self._meta_confidence(prompt)
        
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        
        if not answer_props:
            return min(0.3, meta_conf)
        
        T = self._constraint_propagation(answer_props)
        dynamics = self._state_evolution(answer_props, answer)
        
        # Structural confidence: how well answer matches prompt structure
        structural = len(answer_props) / max(len(prompt_props), 1)
        structural = min(structural, 1.0)
        
        # Combined confidence capped by meta-confidence
        base_conf = 0.5 * dynamics + 0.3 * structural + 0.2 * (np.sum(T) / max(len(T), 1))
        
        return min(base_conf, meta_conf, 0.85)