import numpy as np
from typing import Dict, List

class ReasoningTool:
    """
    Reasoning tool combining measure theory, cognitive load, and sensitivity analysis.
    
    Algorithm:
    1. Parse atomic propositions (negations, comparatives, conditionals, numerics, causals, orderings)
    2. Construct cognitive-load weighted measure (intrinsic, extraneous, germane)
    3. Perform sensitivity analysis via truth-value perturbation
    4. Apply epistemic honesty via meta-confidence on prompt ambiguity
    """
    
    def __init__(self):
        self.alpha, self.beta, self.gamma = 0.4, 0.3, 0.3
        self.eps = 1e-9
        
    def _extract_propositions(self, text: str, reference_text: str = "") -> List[Dict]:
        """Extract typed propositions with truth values."""
        props = []
        text_lower = text.lower()
        ref_lower = reference_text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none|nobody|nothing)\s+(\w+)', text_lower):
            props.append({'type': 'negation', 'span': m.span(), 'text': m.group(), 
                         'truth': m.group() in ref_lower if ref_lower else True})
        
        # Comparatives with numbers
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\d+\.?\d*)', text_lower):
            try:
                n1, op, n2 = float(m.group(1)), m.group(2), float(m.group(3))
                truth = (n1 > n2 if 'greater' in op or '>' in op else n1 < n2)
                props.append({'type': 'comparative', 'span': m.span(), 'text': m.group(), 'truth': truth})
            except: pass
        
        # Conditionals
        for m in re.finditer(r'\b(if|when)\s+(.+?)\s+(then|,)\s+(.+?)[\.\?!]', text_lower):
            props.append({'type': 'conditional', 'span': m.span(), 'text': m.group(), 
                         'truth': m.group() in ref_lower if ref_lower else True})
        
        # Numeric values
        for m in re.finditer(r'\b(\d+\.?\d*)\s*([a-z]+)?\b', text_lower):
            props.append({'type': 'numeric', 'span': m.span(), 'text': m.group(), 
                         'truth': m.group() in ref_lower if ref_lower else True})
        
        # Causal claims
        for m in re.finditer(r'\b(because|since|therefore|thus|leads to|causes)\s+(.+?)[\.\?!]', text_lower):
            props.append({'type': 'causal', 'span': m.span(), 'text': m.group(), 
                         'truth': m.group(2) in ref_lower if ref_lower else True})
        
        # Ordering
        for m in re.finditer(r'\b(before|after|first|last|earlier|later)\s+(\w+)', text_lower):
            props.append({'type': 'ordering', 'span': m.span(), 'text': m.group(), 
                         'truth': m.group() in ref_lower if ref_lower else True})
        
        return props if props else [{'type': 'default', 'span': (0, len(text)), 'text': text, 'truth': True}]
    
    def _compute_weights(self, props: List[Dict], text: str, ref_props: List[Dict]) -> np.ndarray:
        """Compute cognitive load weights."""
        P = len(props)
        S_total = len(text)
        S_covered = len(set(i for p in props for i in range(p['span'][0], p['span'][1])))
        correct = sum(1 for p in props if p['truth'])
        
        intrinsic = self.alpha / P
        extraneous = self.beta * (S_total - S_covered) / (S_total + self.eps)
        germane = self.gamma * correct / P
        
        return np.full(P, intrinsic + extraneous + germane)
    
    def _sensitivity_analysis(self, props: List[Dict], weights: np.ndarray) -> np.ndarray:
        """Compute sensitivity of each proposition via perturbation."""
        truths = np.array([p['truth'] for p in props], dtype=float)
        S0 = np.sum(weights * truths)
        deltas = np.zeros(len(props))
        
        for i in range(len(props)):
            perturbed = truths.copy()
            perturbed[i] = 1 - perturbed[i]
            Si = np.sum(weights * perturbed)
            deltas[i] = abs(Si - S0)
        
        max_delta = deltas.max()
        return deltas / (max_delta + self.eps) if max_delta > 0 else deltas
    
    def _meta_confidence(self, prompt: str) -> float:
        """Evaluate prompt ambiguity and answerability."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an)\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which)\?', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower) and 'both' not in p_lower:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and 'by what' not in p_lower:
            return 0.3
        
        return 1.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / (max(c1, c2) + self.eps)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined score."""
        ref_props = self._extract_propositions(prompt)
        scores = []
        
        for cand in candidates:
            props = self._extract_propositions(cand, prompt)
            weights = self._compute_weights(props, cand, ref_props)
            sensitivities = self._sensitivity_analysis(props, weights)
            
            truths = np.array([p['truth'] for p in props], dtype=float)
            measure_score = np.sum(weights * truths * (1 - sensitivities)) / (np.sum(weights) + self.eps)
            
            ncd_score = 1 - self._ncd(prompt, cand)
            structural_score = sum(1 for p in props if p['truth']) / len(props)
            
            final_score = 0.4 * structural_score + 0.3 * measure_score + 0.15 * ncd_score + 0.15 * (1 - sensitivities.mean())
            scores.append((cand, final_score, f"Structural:{structural_score:.2f} Measure:{measure_score:.2f} NCD:{ncd_score:.2f}"))
        
        ranked = sorted(scores, key=lambda x: x[1], reverse=True)
        return [{"candidate": c, "score": s, "reasoning": r} for c, s, r in ranked]
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.3:
            return meta_conf
        
        props = self._extract_propositions(answer, prompt)
        if not props or all(p['type'] == 'default' for p in props):
            return 0.25
        
        weights = self._compute_weights(props, answer, self._extract_propositions(prompt))
        truths = np.array([p['truth'] for p in props], dtype=float)
        
        raw_conf = np.sum(weights * truths) / (np.sum(weights) + self.eps)
        return min(0.85, raw_conf * meta_conf)