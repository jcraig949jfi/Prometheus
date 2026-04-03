import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Thermodynamic reasoning via constraint propagation + mechanism design.
    
    Parses candidate answers into propositions, builds an entailment graph,
    minimizes energy E = sum((max(0, C_i - C_j - W[i,j]))^2) via gradient descent,
    computes VCG payments to reward consistency, and performs constructive
    computation for numeric/probabilistic/temporal reasoning.
    """
    
    def __init__(self):
        self.alpha = 0.1  # gradient descent learning rate
        self.max_iter = 100
        self.epsilon = 1e-4
    
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract propositions with negation, numeric, comparative, conditional flags."""
        props = []
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            sent = sent.strip().lower()
            if len(sent) < 3:
                continue
            
            prop = {
                'text': sent,
                'negation': bool(re.search(r'\b(not|no|never|neither|nor|n\'t)\b', sent)),
                'numeric': re.findall(r'-?\d+\.?\d*', sent),
                'comparative': bool(re.search(r'\b(more|less|greater|higher|lower|better|worse|than|<|>|=)\b', sent)),
                'conditional': bool(re.search(r'\b(if|then|when|whenever|implies)\b', sent)),
                'causal': bool(re.search(r'\b(because|since|causes|leads to|due to|results in)\b', sent)),
                'temporal': bool(re.search(r'\b(before|after|during|while|until|when)\b', sent)),
            }
            props.append(prop)
        return props
    
    def _build_constraint_graph(self, props: List[Dict]) -> np.ndarray:
        """Build entailment adjacency matrix W[i,j]=1 if i entails j."""
        n = len(props)
        W = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # Same negation polarity suggests entailment
                if props[i]['negation'] == props[j]['negation']:
                    W[i, j] += 0.3
                # Numeric consistency
                if props[i]['numeric'] and props[j]['numeric']:
                    try:
                        nums_i = [float(x) for x in props[i]['numeric']]
                        nums_j = [float(x) for x in props[j]['numeric']]
                        if set(nums_i) & set(nums_j):
                            W[i, j] += 0.4
                    except:
                        pass
                # Conditional chains
                if props[i]['conditional'] and props[j]['conditional']:
                    W[i, j] += 0.2
                # Temporal ordering
                if props[i]['temporal'] and props[j]['temporal']:
                    W[i, j] += 0.2
        return W
    
    def _minimize_energy(self, W: np.ndarray) -> Tuple[np.ndarray, float]:
        """Gradient descent to minimize E = sum((max(0, C_i - C_j - W[i,j]))^2)."""
        n = W.shape[0]
        C = np.random.rand(n) * 0.5 + 0.5  # Initialize around 0.5-1.0
        
        for _ in range(self.max_iter):
            E = 0
            grad = np.zeros(n)
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    violation = max(0, C[i] - C[j] - W[i, j])
                    E += violation ** 2
                    if violation > 0:
                        grad[i] += 2 * violation
                        grad[j] -= 2 * violation
            
            C_new = C - self.alpha * grad
            C_new = np.clip(C_new, 0, 1)
            
            if np.abs(E) < self.epsilon or np.linalg.norm(C_new - C) < self.epsilon:
                break
            C = C_new
        
        return C, E
    
    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """Constructive computation: arithmetic, comparisons, probabilities."""
        score = 0.0
        p_nums = re.findall(r'-?\d+\.?\d*', prompt.lower())
        c_nums = re.findall(r'-?\d+\.?\d*', candidate.lower())
        
        # Numeric comparison
        if re.search(r'(which|what).*(greater|larger|bigger|more)', prompt.lower()):
            try:
                nums = [float(x) for x in p_nums]
                c_vals = [float(x) for x in c_nums]
                if nums and c_vals:
                    max_val = max(nums)
                    if max_val in c_vals:
                        score += 0.5
            except:
                pass
        
        # Arithmetic expressions (PEMDAS)
        if re.search(r'[\+\-\*/]', prompt):
            try:
                expr_match = re.search(r'([\d\s\+\-\*/\(\)]+)\s*=', prompt)
                if expr_match:
                    result = eval(expr_match.group(1))
                    if c_nums and abs(float(c_nums[0]) - result) < 0.01:
                        score += 0.6
            except:
                pass
        
        # Probability/Bayesian
        if re.search(r'\b(probability|chance|likely|percent)\b', prompt.lower()):
            try:
                if c_nums:
                    prob = float(c_nums[0])
                    if 0 <= prob <= 100 or 0 <= prob <= 1:
                        score += 0.3
            except:
                pass
        
        return score
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you).*(stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is).*(fail|wrong|bad)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and '?' in p:
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bneither\b', p):
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            if not re.search(r'\b(according to|measured by|based on)\b', p):
                return 0.3
        
        # Very short or vague prompts
        if len(p.split()) < 5:
            return 0.4
        
        return 1.0  # No ambiguity detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using thermodynamic energy + mechanism design + computation."""
        results = []
        all_props = []
        cand_ranges = []
        
        # Parse all propositions
        for cand in candidates:
            props = self._parse_propositions(cand)
            cand_ranges.append((len(all_props), len(all_props) + len(props)))
            all_props.extend(props)
        
        if len(all_props) == 0:
            # Fallback to NCD only
            for cand in candidates:
                ncd_score = 1 - self._ncd(prompt, cand)
                results.append({'candidate': cand, 'score': ncd_score * 0.5, 'reasoning': 'No propositions found; NCD fallback'})
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Build graph and minimize energy
        W = self._build_constraint_graph(all_props)
        C, E_total = self._minimize_energy(W)
        
        # Score each candidate
        for idx, cand in enumerate(candidates):
            start, end = cand_ranges[idx]
            
            # Thermodynamic score (lower energy = higher score)
            energy_score = np.mean(C[start:end]) if end > start else 0.5
            
            # VCG payment (contribution to global consistency)
            contribution = np.sum(W[start:end, :]) + np.sum(W[:, start:end])
            payment = contribution / (len(all_props) * 2) if len(all_props) > 0 else 0
            
            # Constructive computation
            comp_score = self._compute_numeric_score(prompt, cand)
            
            # NCD as minor tiebreaker
            ncd_score = (1 - self._ncd(prompt, cand)) * 0.1
            
            # Weighted combination: 45% energy, 25% payment, 20% computation, 10% NCD
            final_score = 0.45 * energy_score + 0.25 * payment + 0.2 * comp_score + 0.1 * ncd_score
            
            reasoning = f'Energy={energy_score:.2f}, Payment={payment:.2f}, Comp={comp_score:.2f}'
            results.append({'candidate': cand, 'score': final_score, 'reasoning': reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        
        # Parse and compute
        props = self._parse_propositions(answer)
        if len(props) == 0:
            return min(0.3, meta_conf)
        
        # Constructive computation signal
        comp_score = self._compute_numeric_score(prompt, answer)
        
        # Energy from single answer
        W = self._build_constraint_graph(props)
        C, E = self._minimize_energy(W)
        energy_conf = np.mean(C) if len(C) > 0 else 0.5
        
        # Combine signals
        base_conf = 0.5 * energy_conf + 0.4 * comp_score + 0.1 * (1 - self._ncd(prompt, answer))
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf)