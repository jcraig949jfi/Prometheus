import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Predictive Coding x Self-Organized Criticality x Mechanism Design
    
    Builds hierarchical propositional network with belief propagation.
    Errors undergo sandpile toppling (SOC). Scoring combines prediction
    error with constraint satisfaction (mechanism design). Confidence
    tracks trajectory stability across premise orderings.
    """
    
    def __init__(self):
        self.alpha = 0.1  # belief update rate
        self.theta = 0.2  # toppling threshold
        self.lambda_vcg = 0.01  # mechanism design weight
        np.random.seed(42)
    
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract structural propositions from text."""
        props = []
        text_lower = text.lower()
        
        # Numeric comparisons
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text):
            a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
            props.append({'type': 'compare', 'vals': (a, op, b), 'text': m.group()})
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|isn\'?t|aren\'?t|wasn\'?t)\s+(\w+)', text_lower):
            props.append({'type': 'negation', 'target': m.group(2), 'text': m.group()})
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text_lower):
            props.append({'type': 'conditional', 'ante': m.group(1), 'cons': m.group(2), 'text': m.group()})
        
        # Comparatives (ordering)
        for m in re.finditer(r'(\w+)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', text_lower):
            props.append({'type': 'order', 'left': m.group(1), 'op': m.group(2), 'right': m.group(3), 'text': m.group()})
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|since|leads to|causes)\s+(\w+)', text_lower):
            props.append({'type': 'causal', 'cause': m.group(1), 'effect': m.group(3), 'text': m.group()})
        
        return props if props else [{'type': 'atomic', 'text': text[:50]}]
    
    def _build_network(self, props: List[Dict], n_layers: int = 3) -> Tuple:
        """Build hierarchical network from propositions."""
        n = max(len(props), 3)
        beliefs = np.random.uniform(0.4, 0.6, n)
        
        # Layer assignment: bottom 40% primitives, middle 40% compounds, top 20% root
        layers = np.zeros(n, dtype=int)
        layers[:int(0.4*n)] = 0
        layers[int(0.4*n):int(0.8*n)] = 1
        layers[int(0.8*n):] = 2
        
        # Adjacency: each node connects to 2-3 in next layer
        adj = [[] for _ in range(n)]
        for i in range(n):
            if layers[i] < 2:
                targets = np.where(layers == layers[i] + 1)[0]
                if len(targets) > 0:
                    adj[i] = list(np.random.choice(targets, min(2, len(targets)), replace=False))
        
        # Weights for prediction
        W = np.random.randn(n, n) * 0.1
        
        return beliefs, W, adj, layers
    
    def _predictive_coding_step(self, beliefs, W, adj, layers):
        """One step of hierarchical predictive coding."""
        predictions = np.zeros_like(beliefs)
        
        for i in range(len(beliefs)):
            if adj[i]:
                child_beliefs = beliefs[adj[i]]
                predictions[i] = 1.0 / (1.0 + np.exp(-np.sum(W[i, adj[i]] * child_beliefs)))
            else:
                predictions[i] = beliefs[i]
        
        errors = beliefs - predictions
        
        # Upward pass: parents receive sum of child errors
        for i in range(len(beliefs)):
            for child in adj[i]:
                errors[i] += errors[child] * 0.3
        
        return errors, predictions
    
    def _soc_toppling(self, errors):
        """Self-organized criticality: topple high errors to neighbors."""
        n = len(errors)
        active = np.abs(errors) > self.theta
        iterations = 0
        
        while np.any(active) and iterations < 20:
            for i in np.where(active)[0]:
                excess = errors[i] - np.sign(errors[i]) * self.theta
                # Distribute to circular neighbors
                neighbors = [(i-1) % n, (i+1) % n]
                for nb in neighbors:
                    errors[nb] += excess / len(neighbors)
                errors[i] = np.sign(errors[i]) * self.theta
            
            active = np.abs(errors) > self.theta
            iterations += 1
        
        return errors
    
    def _constraint_satisfaction(self, props: List[Dict], candidate: str) -> int:
        """Count hard constraints satisfied by candidate."""
        count = 0
        cand_lower = candidate.lower()
        
        for p in props:
            if p['type'] == 'compare':
                a, op, b = p['vals']
                result = eval(f"{a} {op} {b}")
                if (result and 'true' in cand_lower) or (not result and 'false' in cand_lower):
                    count += 1
            elif p['type'] == 'negation':
                if p['target'] not in cand_lower:
                    count += 1
            elif p['type'] == 'order':
                # Check transitivity hints
                if p['left'] in cand_lower or p['right'] in cand_lower:
                    count += 1
        
        return count
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability markers."""
        lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you)\s+(stop|quit|cease)', lower):
            return 0.2
        if re.search(r'why (did|does|is)\s+\w+\s+(fail|stop|end)', lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every\s+\w+.*\ba\b\s+\w+', lower):
            return 0.3
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|it|they)\s+\w+.*who', lower):
            return 0.3
        
        # False dichotomy
        if re.search(r'either\s+\w+\s+or\s+\w+', lower) and 'only' not in lower:
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)', lower):
            return 0.4
        
        # Unanswerable markers
        if re.search(r'(impossible|cannot|unknowable|insufficient)', lower):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _trajectory_stability(self, prompt: str, candidate: str, props: List[Dict]) -> float:
        """Measure convergence stability across premise orderings."""
        if len(props) < 2:
            return 0.7
        
        scores = []
        for _ in range(3):  # Try 3 random orderings
            perm_props = np.random.permutation(props).tolist()
            beliefs, W, adj, layers = self._build_network(perm_props)
            
            for _ in range(5):
                errors, predictions = self._predictive_coding_step(beliefs, W, adj, layers)
                errors = self._soc_toppling(errors)
                beliefs = beliefs - self.alpha * errors
                beliefs = np.clip(beliefs, 0, 1)
            
            score = -np.linalg.norm(errors) + self.lambda_vcg * self._constraint_satisfaction(props, candidate)
            scores.append(score)
        
        # Stability = inverse of variance
        variance = np.var(scores) if len(scores) > 1 else 0.1
        stability = 1.0 / (1.0 + variance)
        return stability
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using predictive coding + SOC + mechanism design."""
        props = self._parse_propositions(prompt)
        results = []
        
        for cand in candidates:
            combined_props = self._parse_propositions(prompt + " " + cand)
            beliefs, W, adj, layers = self._build_network(combined_props)
            
            # Run predictive coding with SOC
            for iteration in range(10):
                errors, predictions = self._predictive_coding_step(beliefs, W, adj, layers)
                errors = self._soc_toppling(errors)
                beliefs = beliefs - self.alpha * errors
                beliefs = np.clip(beliefs, 0, 1)
            
            # Mechanism design scoring
            error_term = -np.linalg.norm(errors)
            constraint_term = self._constraint_satisfaction(props, cand)
            ncd_term = -self._ncd(prompt, cand)
            
            score = 0.5 * error_term + 0.35 * constraint_term + 0.15 * ncd_term
            
            reasoning = f"Error: {error_term:.3f}, Constraints: {constraint_term}, NCD: {ncd_term:.3f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on trajectory stability and meta-checks."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        props = self._parse_propositions(prompt)
        
        # No structural match
        if len(props) <= 1 and props[0]['type'] == 'atomic':
            return 0.25
        
        # Trajectory stability
        stability = self._trajectory_stability(prompt, answer, props)
        
        # Constraint satisfaction signal
        constraints = self._constraint_satisfaction(props, answer)
        constraint_conf = min(1.0, constraints / max(1, len(props) * 0.5))
        
        # Combined confidence (capped at 0.85 for epistemic honesty)
        conf = 0.4 * stability + 0.3 * constraint_conf + 0.3 * meta_conf
        return min(0.85, max(0.1, conf))