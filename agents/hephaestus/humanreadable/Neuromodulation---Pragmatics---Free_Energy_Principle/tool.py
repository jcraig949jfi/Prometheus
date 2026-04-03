import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Predictive-Error-Modulated Belief Scoring (PEMBS)
    
    Combines Free Energy Principle, neuromodulation, and pragmatic parsing.
    Extracts propositions, builds constraint graph, updates beliefs via
    gradient descent with gain modulation, scores by final free energy.
    Tracks dynamics (convergence rate, stability) for confidence.
    """
    
    def __init__(self):
        self.theta = 1.0  # precision (inverse variance)
        self.eta = 0.1    # learning rate
        self.alpha = 0.05 # gain modulation strength
        self.max_iter = 10
        self.convergence_threshold = 1e-4
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract propositions with polarity and arguments."""
        text_lower = text.lower()
        props = []
        
        # Numeric comparisons
        for match in re.finditer(r'(\w+)\s*(>|<|>=|<=|=|equals?|greater|less)\s*(\d+\.?\d*)', text_lower):
            props.append({
                'type': 'comparison',
                'subject': match.group(1),
                'relation': match.group(2),
                'object': match.group(3),
                'polarity': 1,
                'value': float(match.group(3))
            })
        
        # Negations
        neg_count = len(re.findall(r'\b(not|no|never|none|neither)\b', text_lower))
        
        # Conditionals (if-then)
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$|,)', text_lower):
            props.append({'type': 'conditional', 'antecedent': match.group(1), 
                         'consequent': match.group(2), 'polarity': 1})
        
        # Causal relations
        for match in re.finditer(r'(.+?)\s+(because|leads to|causes|due to)\s+(.+?)(?:\.|$|,)', text_lower):
            props.append({'type': 'causal', 'cause': match.group(1), 
                         'effect': match.group(3), 'polarity': 1})
        
        # Ordering
        for match in re.finditer(r'(\w+)\s+(before|after|precedes|follows)\s+(\w+)', text_lower):
            props.append({'type': 'order', 'first': match.group(1), 
                         'second': match.group(3), 'relation': match.group(2), 'polarity': 1})
        
        # Word tokens as basic propositions
        tokens = re.findall(r'\b\w+\b', text_lower)
        for tok in tokens[:20]:  # limit to avoid explosion
            if len(tok) > 2:
                props.append({'type': 'token', 'word': tok, 'polarity': 1 if neg_count % 2 == 0 else -1})
        
        return props
    
    def _build_constraint_graph(self, props: List[Dict]) -> np.ndarray:
        """Build adjacency matrix encoding logical constraints."""
        n = len(props)
        if n == 0:
            return np.zeros((0, 0))
        
        G = np.zeros((n, n))
        
        # Transitivity for comparisons
        for i, pi in enumerate(props):
            for j, pj in enumerate(props):
                if i == j:
                    continue
                
                # Same subject/object creates edge
                if pi.get('type') == 'comparison' and pj.get('type') == 'comparison':
                    if pi.get('subject') == pj.get('subject'):
                        G[i, j] = 0.5
                
                # Conditional: antecedent -> consequent
                if pi.get('type') == 'conditional':
                    # Simple heuristic: if words overlap, create edge
                    if pj.get('type') == 'token' and pj.get('word') in pi.get('consequent', ''):
                        G[i, j] = 0.8
                
                # Token overlap
                if pi.get('type') == 'token' and pj.get('type') == 'token':
                    if pi['word'] == pj['word']:
                        G[i, j] = 1.0
        
        return G
    
    def _run_pembs(self, props: List[Dict], G: np.ndarray) -> Tuple[np.ndarray, List[float], float]:
        """Run free-energy minimization with gain modulation."""
        n = len(props)
        if n == 0:
            return np.array([]), [], 0.0
        
        b = np.full(n, 0.5)  # belief vector
        g = np.ones(n)       # gain vector
        history = [0.5]      # track convergence
        
        for iteration in range(self.max_iter):
            # Prediction from constraints
            pred = 1.0 / (1.0 + np.exp(-G @ b))  # sigmoid
            
            # Prediction error
            e = b - pred
            
            # Free energy
            F = 0.5 * self.theta * (e ** 2).sum() + 0.5 * ((b - 0.5) ** 2).sum()
            
            # Update beliefs
            b_old = b.copy()
            b -= self.eta * g * (self.theta * e - (b - 0.5))
            b = np.clip(b, 0.01, 0.99)
            
            # Neuromodulatory gain update
            g = np.clip(g + self.alpha * np.abs(e), 0.1, 3.0)
            
            # Track convergence
            delta = np.abs(b - b_old).max()
            history.append(delta)
            
            if delta < self.convergence_threshold:
                break
        
        # Final free energy
        pred = 1.0 / (1.0 + np.exp(-G @ b))
        e = b - pred
        F_final = 0.5 * self.theta * (e ** 2).sum() + 0.5 * ((b - 0.5) ** 2).sum()
        
        return b, history, F_final
    
    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons directly."""
        score = 0.0
        
        # Extract numbers from prompt and candidate
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        # Check if candidate contains correct numeric answer
        if prompt_nums and cand_nums:
            # Simple heuristic: if prompt asks "which is larger" and candidate has max
            if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                if cand_nums and max(prompt_nums) in cand_nums:
                    score += 0.3
            elif 'smaller' in prompt.lower() or 'less' in prompt.lower():
                if cand_nums and min(prompt_nums) in cand_nums:
                    score += 0.3
        
        return score
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B reasoning traps (ambiguity, presupposition)."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if 'who' in prompt_lower and re.search(r'\b(he|she|they|it)\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|most interesting)\b', prompt_lower):
            return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(impossible|cannot determine|insufficient|not enough)\b', prompt_lower):
            return 0.2
        
        return 1.0  # No traps detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free energy and dynamics."""
        results = []
        
        # Extract prompt propositions
        prompt_props = self._extract_propositions(prompt)
        
        for cand in candidates:
            # Combine prompt + candidate
            combined = prompt + " " + cand
            props = self._extract_propositions(combined)
            
            # Build constraint graph
            G = self._build_constraint_graph(props)
            
            # Run PEMBS
            b, history, F = self._run_pembs(props, G)
            
            # Dynamics score: faster convergence = better
            convergence_rate = 1.0 / (1.0 + len(history)) if history else 0.0
            stability = 1.0 - (np.std(history) if len(history) > 1 else 1.0)
            dynamics_score = convergence_rate + stability
            
            # Structural score: number of parsed propositions
            structural_score = len(props) / 30.0  # normalize
            
            # Numeric computation
            numeric_score = self._compute_numeric_score(prompt, cand)
            
            # NCD (tiebreaker)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combined score (dynamics 45%, structural 35%, NCD 15%, numeric 5%)
            final_score = (-F * 0.45 + dynamics_score * 0.35 + 
                          ncd_score * 0.15 + numeric_score * 0.05)
            
            results.append({
                'candidate': cand,
                'score': float(final_score),
                'reasoning': f"FE={F:.3f}, conv={convergence_rate:.3f}, props={len(props)}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and computation."""
        # Check meta-level traps first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Run evaluation
        combined = prompt + " " + answer
        props = self._extract_propositions(combined)
        
        if len(props) == 0:
            return 0.2  # No structure parsed
        
        G = self._build_constraint_graph(props)
        b, history, F = self._run_pembs(props, G)
        
        # Confidence from dynamics
        if len(history) > 1:
            convergence_rate = 1.0 / len(history)
            stability = 1.0 - min(np.std(history), 1.0)
        else:
            convergence_rate = 0.5
            stability = 0.5
        
        # Confidence from free energy (lower is better)
        fe_conf = 1.0 / (1.0 + F)
        
        # Combined confidence (capped by meta)
        base_conf = (convergence_rate * 0.4 + stability * 0.3 + fe_conf * 0.3)
        final_conf = min(base_conf, meta_conf)
        
        # Never exceed 0.9 unless very strong signal
        return min(final_conf * 0.85, 0.9)