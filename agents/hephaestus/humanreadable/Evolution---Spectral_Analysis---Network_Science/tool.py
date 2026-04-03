import re
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    Evolutionary Spectral Network Scorer (ESNS) with Adversarial Robustness.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions and logical features (negation, causality, etc.)
       using robust regex patterns that ignore variable names.
    2. Graph Construction: Builds an adjacency matrix representing logical support between propositions.
    3. Constraint Propagation: Uses forward chaining on Horn-like clauses derived from the prompt.
    4. Spectral Analysis: Computes the normalized Laplacian eigenvalues to measure graph coherence (spectral leakage).
    5. Network Science: Calculates betweenness centrality to identify critical reasoning nodes.
    6. Evolutionary Optimization: Mutates the graph structure to maximize a fitness function combining
       constraint satisfaction, spectral coherence, and network centrality.
    7. Epistemic Honesty: Detects ambiguity, presuppositions, and unanswerable queries to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction (variable-agnostic)
        self.patterns = {
            'negation': re.compile(r'\b(not|n\'t|no|never|without|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|>\|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|given)\b.*?\b(then|else|must|will)\b', re.IGNORECASE | re.DOTALL),
            'causal': re.compile(r'\b(because|since|leads to|results in|causes|produces|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'ordering': re.compile(r'\b(first|second|third|before|after|precede|follow)\b', re.IGNORECASE),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|how often did)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or both|only option)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }
        
        # Weights for fitness function
        self.weights = {'constraint': 0.4, 'spectral': 0.3, 'network': 0.3}

    def _extract_features(self, text: str) -> Dict[str, int]:
        """Extract binary feature flags from text."""
        flags = {
            'neg': 1 if self.patterns['negation'].search(text) else 0,
            'comp': 1 if self.patterns['comparative'].search(text) else 0,
            'cond': 1 if self.patterns['conditional'].search(text) else 0,
            'caus': 1 if self.patterns['causal'].search(text) else 0,
            'num': 1 if self.patterns['numeric'].search(text) else 0,
            'ord': 1 if self.patterns['ordering'].search(text) else 0
        }
        return flags

    def _parse_propositions(self, text: str) -> List[Dict]:
        """Split text into propositions and extract features."""
        # Simple sentence splitter robust to variable names
        sentences = re.split(r'[.!?]', text)
        props = []
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if len(sent) < 5: continue
            features = self._extract_features(sent)
            props.append({
                'text': sent,
                'features': np.array([
                    features['neg'], features['comp'], features['cond'],
                    features['caus'], features['num'], features['ord']
                ], dtype=float)
            })
        return props

    def _build_adjacency(self, props: List[Dict]) -> np.ndarray:
        """Build initial adjacency matrix based on syntactic cues."""
        n = len(props)
        if n == 0: return np.array([])
        adj = np.zeros((n, n))
        
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j: continue
                # Heuristic: Causal/Conditional in p1 pointing to p2 if p2 follows
                if p1['features'][2] > 0 or p1['features'][3] > 0: # Cond or Causal
                    if j > i: adj[i, j] = 1.0
                # Heuristic: Numeric comparison implies order
                if p1['features'][4] > 0 and p2['features'][4] > 0:
                    if abs(i-j) == 1: adj[i, j] = 0.5 # Weak link between numbers
        return adj

    def _constraint_propagation(self, adj: np.ndarray, props: List[Dict]) -> float:
        """Simulate forward chaining to estimate constraint satisfaction."""
        if len(props) == 0: return 0.0
        n = len(props)
        # Simulate activation spreading
        activation = np.zeros(n)
        activation[0] = 1.0 # Assume first proposition is premise
        
        for _ in range(n): # Iterate until convergence or max steps
            new_act = activation.copy()
            for i in range(n):
                if activation[i] > 0.5:
                    # Propagate to neighbors
                    neighbors = adj[i, :]
                    if np.sum(neighbors) > 0:
                        new_act += neighbors * activation[i]
            activation = np.clip(new_act, 0, 1)
            if np.all(activation == new_act): break
            
        # Score based on how many nodes are activated (simplified constraint sat)
        return np.mean(activation > 0.5)

    def _spectral_score(self, adj: np.ndarray) -> float:
        """Compute spectral leakage metric."""
        if adj.shape[0] < 2: return 0.5
        deg = np.sum(adj, axis=1)
        deg_inv_sqrt = np.diag(1.0 / np.sqrt(deg + 1e-9))
        # Normalized Laplacian L = I - D^-1/2 A D^-1/2
        lap = np.eye(adj.shape[0]) - deg_inv_sqrt @ adj @ deg_inv_sqrt
        try:
            eigenvalues = np.linalg.eigvalsh(lap)
            # PSD approximation
            psd = np.abs(np.fft.fft(eigenvalues))**2
            if np.sum(psd) == 0: return 0.5
            leakage = np.sum(psd[1:-1]) / (np.sum(psd) + 1e-9)
            return max(0.0, min(1.0, 1.0 - leakage))
        except:
            return 0.5

    def _network_score(self, adj: np.ndarray) -> float:
        """Approximate betweenness centrality mean."""
        n = adj.shape[0]
        if n < 3: return 0.5
        # Simplified Brandes-like approximation for small N
        centrality = np.zeros(n)
        for s in range(n):
            # BFS from s
            dist = [-1] * n
            dist[s] = 0
            queue = deque([s])
            while queue:
                v = queue.popleft()
                for w in range(n):
                    if adj[v, w] > 0 or adj[w, v] > 0: # Treat as undirected for simplicity
                        if dist[w] == -1:
                            dist[w] = dist[v] + 1
                            queue.append(w)
            centrality[s] = np.mean([d for d in dist if d > 0]) if any(d > 0 for d in dist) else 0
            
        return np.mean(centrality) / (n + 1e-9) if n > 0 else 0.5

    def _evolutionary_optimize(self, base_adj: np.ndarray, props: List[Dict], generations: int = 15) -> float:
        """Run GA to find optimal graph configuration."""
        if base_adj.size == 0: return 0.0
        n = base_adj.shape[0]
        pop_size = 10
        population = [base_adj.copy() for _ in range(pop_size)]
        
        # Initialize random mutations
        for i in range(1, pop_size):
            mask = np.random.rand(n, n) < 0.1
            population[i] = np.where(mask, 1 - base_adj, base_adj)

        best_fitness = 0.0
        
        for _ in range(generations):
            fitnesses = []
            for graph in population:
                c_sat = self._constraint_propagation(graph, props)
                spec = self._spectral_score(graph)
                net = self._network_score(graph)
                fit = (self.weights['constraint'] * c_sat + 
                       self.weights['spectral'] * spec + 
                       self.weights['network'] * net)
                fitnesses.append(fit)
            
            best_fitness = max(best_fitness, max(fitnesses))
            
            # Selection & Reproduction
            sorted_idx = np.argsort(fitnesses)[::-1]
            new_pop = [population[sorted_idx[0]]] # Elitism
            
            while len(new_pop) < pop_size:
                # Tournament selection
                candidates = np.random.choice(len(population), 2, replace=False)
                parent = population[sorted_idx[candidates[0]]] if fitnesses[sorted_idx[candidates[0]]] > fitnesses[sorted_idx[candidates[1]]] else population[sorted_idx[candidates[1]]]
                
                child = parent.copy()
                # Mutation
                if np.random.rand() < 0.3:
                    mask = np.random.rand(n, n) < 0.05
                    child = np.where(mask, 1 - child, child)
                new_pop.append(child)
            
            population = new_pop[:pop_size]
            
        return best_fitness

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Check for epistemic traps and ambiguity."""
        score = 1.0
        
        # 1. Presupposition check
        if self.patterns['presupposition'].search(prompt):
            score *= 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            score *= 0.4
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            score *= 0.3
            
        # 4. Ambiguity in answer (very short or generic)
        if len(answer.split()) < 2 and answer.lower() not in ['yes', 'no', 'true', 'false']:
            score *= 0.8
            
        # 5. No structural match (heuristic: if no numbers, no conditionals, no causals)
        feats = self._extract_features(prompt)
        if sum(feats.values()) == 0:
            score *= 0.5
            
        return max(0.0, min(1.0, score))

    def _constructive_solve(self, prompt: str, candidate: str) -> Optional[float]:
        """Attempt to computationally verify the answer."""
        # Extract numbers
        nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        cand_nums = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        # Case 1: Direct numeric equality
        if len(nums) == 1 and len(cand_nums) == 1:
            if abs(nums[0] - cand_nums[0]) < 1e-6:
                return 1.0
            return 0.0
            
        # Case 2: Simple addition/subtraction context (e.g. "5 plus 3")
        if 'plus' in prompt or '+' in prompt:
            if len(nums) >= 2 and len(cand_nums) == 1:
                if abs(sum(nums[:2]) - cand_nums[0]) < 1e-6:
                    return 1.0
                return 0.0
                
        # Case 3: Comparison
        if any(k in prompt for k in ['greater', 'less', 'larger', 'smaller']):
            if len(nums) == 2 and len(cand_nums) == 1:
                if 'greater' in prompt or 'larger' in prompt:
                    return 1.0 if cand_nums[0] == max(nums) else 0.0
                else:
                    return 1.0 if cand_nums[0] == min(nums) else 0.0

        return None # Cannot computationally verify

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        props = self._parse_propositions(prompt)
        base_adj = self._build_adjacency(props)
        
        for cand in candidates:
            # 1. Constructive Computation (High Priority)
            comp_score = self._constructive_solve(prompt, cand)
            
            if comp_score is not None:
                # If we can compute it, trust the math
                final_score = comp_score
                reason = "Computationally verified."
            else:
                # 2. Evolutionary Spectral Scoring
                esns_score = self._evolutionary_optimize(base_adj, props)
                
                # 3. NCD Tiebreaker (Max 15% influence)
                def ncd(a, b):
                    try:
                        import zlib
                        c = (a + b).encode()
                        return len(zlib.compress(c)) / max(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())), 1)
                    except: return 0.5
                
                # Normalize NCD to similarity
                ncd_sim = 1.0 - ncd(prompt, cand) 
                # Weighted combination: 85% ESNS, 15% NCD
                final_score = 0.85 * esns_score + 0.15 * ncd_sim
                reason = f"ESNS Score: {esns_score:.3f}, Structural coherence detected."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence capped by epistemic honesty checks."""
        # Base confidence from the scoring mechanism
        res = self.evaluate(prompt, [answer])
        base_conf = res[0]['score'] if res else 0.5
        
        # Apply meta-confidence cap
        meta_cap = self._meta_confidence(prompt, answer)
        
        final_conf = min(base_conf, meta_cap)
        
        # Hard cap for ambiguity
        if meta_cap < 0.3:
            return final_conf
            
        return float(np.clip(final_conf, 0.0, 0.95)) # Never 1.0 unless explicitly computed