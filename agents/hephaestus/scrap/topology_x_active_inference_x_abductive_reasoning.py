import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining Topological parsing, Active Inference, 
    and Abductive hitting-set logic using only NumPy and regex.
    
    Mechanism:
    1. Structural Parsing: Extracts predicates (S-R-O) and constraints (negation, comparison).
    2. Topology: Builds adjacency matrix A. Uses rank of Laplacian for connected components (beta0).
       Note: Per safety guidelines, topology is restricted to structural confidence, not direct scoring.
    3. Active Inference: Computes Expected Free Energy (G) based on constraint violations (surprisal)
       and missing edge entropy. Score = exp(-G).
    4. Abduction: Greedy hitting-set to resolve contradictions. Score based on hypothesis simplicity.
    5. Final Score: Weighted sum where structural consistency dominates, NCD is tiebreaker.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|unless)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|else|when|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|results in)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'triple': re.compile(r'(\w+)\s+(is|has|does|leads to|greater|less)\s+(\w+)', re.IGNORECASE)
        }
        # Weights
        self.lambdas = [0.4, 0.3, 0.3] # Topo, Inf, Abd

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features and predicate triples."""
        features = {
            'negations': len(self.patterns['negation'].findall(text)),
            'comparatives': len(self.patterns['comparative'].findall(text)),
            'conditionals': len(self.patterns['conditional'].findall(text)),
            'causals': len(self.patterns['causal'].findall(text)),
            'numbers': [float(n) for n in self.patterns['number'].findall(text)],
            'triples': self.patterns['triple'].findall(text),
            'length': len(text.split())
        }
        return features

    def _build_graph(self, triples: List[Tuple]) -> Tuple[np.ndarray, List[str]]:
        """Build adjacency matrix from triples. Nodes are unique terms."""
        if not triples:
            return np.zeros((1, 1)), ["root"]
        
        nodes = list(set([t[0] for t in triples] + [t[2] for t in triples]))
        node_map = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        A = np.zeros((n, n))
        
        for subj, rel, obj in triples:
            i, j = node_map[subj], node_map[obj]
            A[i, j] = 1.0 # Confidence 1.0 for explicit extraction
            
        return A, nodes

    def _compute_topo_score(self, A: np.ndarray) -> float:
        """
        Compute topological coherence. 
        Restricted to confidence wrapper per safety guidelines.
        Returns exp(-alpha * beta0).
        """
        if A.shape[0] == 0:
            return 1.0
        
        # Symmetrize for undirected component analysis
        A_sym = np.logical_or(A, A.T).astype(float)
        D = np.diag(A_sym.sum(axis=1))
        L = D - A_sym
        
        # Rank via SVD (numpy only)
        try:
            rank = np.linalg.matrix_rank(L, tol=1e-5)
        except:
            rank = 0
            
        # Beta0 = N - Rank(L) for connected components in Laplacian context
        # Actually, for Laplacian, nullity = components. 
        # But rank(L) = N - components. So components = N - rank.
        n_nodes = A.shape[0]
        beta0 = max(0, n_nodes - rank)
        
        # Coherence: penalize fragmentation
        return float(np.exp(-0.5 * beta0))

    def _compute_inference_score(self, A: np.ndarray, features: Dict) -> float:
        """
        Active Inference: Minimize Expected Free Energy G.
        G = Surprisal (violations) - Epistemic Value (entropy of missing info).
        """
        # Surprisal: Check for logical holes (simplified as cycle detection in 'greater' chains)
        # If A has cycles where relation implies order, it's a violation.
        # Simplified: Count cycles in A+
        A_plus = A.copy()
        for _ in range(A.shape[0]):
            A_plus = np.logical_or(A_plus, np.dot(A_plus, A)).astype(float)
            
        # Cycles indicate logical holes in strict ordering
        cycles = np.trace(A_plus) # Diagonal elements in transitive closure
        surprisal = cycles * features['negations'] # Amplify by negation complexity
        
        # Epistemic value: Entropy of missing edges
        total_possible = A.shape[0] * (A.shape[0] - 1)
        existing = np.count_nonzero(A)
        missing = max(1, total_possible - existing)
        entropy = np.log2(missing + 1)
        
        G = surprisal - entropy
        return float(np.exp(-G))

    def _compute_abduction_score(self, features: Dict) -> float:
        """
        Abductive Reasoning: Hitting set for constraints.
        Score = Simplicity * Coverage.
        """
        # Hypotheses needed to resolve conflicts (simulated)
        # If negations exist without conditionals, we need more hypotheses to reconcile
        conflict_potential = features['negations'] + features['comparatives']
        resolution_power = features['conditionals'] + features['causals'] + 1
        
        # Minimal set H size approximation
        h_size = max(1, conflict_potential - resolution_power)
        simplicity = 1.0 / (h_size + 1)
        
        # Coverage: how much of the text is explained by structural cues
        total_cues = sum([features['negations'], features['comparatives'], 
                          features['conditionals'], features['causals']])
        coverage = 1.0 if total_cues == 0 else min(1.0, resolution_power / (total_cues + 1))
        
        return simplicity * coverage

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        def l(s): return len(zlib.compress(s.encode()))
        if not s1 or not s2: return 1.0
        return (l(s1 + s2) - min(l(s1), l(s2))) / max(l(s1), l(s2), 1)

    def confidence(self, prompt: str, answer: str) -> float:
        """Evaluate single candidate confidence."""
        features = self._extract_features(answer)
        A, _ = self._build_graph(features['triples'])
        
        # 1. Topological Confidence (Structural integrity)
        topo_score = self._compute_topo_score(A)
        
        # 2. Active Inference Score
        inf_score = self._compute_inference_score(A, features)
        
        # 3. Abductive Score
        abd_score = self._compute_abduction_score(features)
        
        # Weighted combination
        # Topology is restricted to confidence wrapper role (multiplier)
        base_score = (self.lambdas[1] * inf_score + self.lambdas[2] * abd_score)
        final_score = topo_score * base_score
        
        # Normalize roughly to 0-1
        return min(1.0, max(0.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Primary scoring via structural logic
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Topo:{self._compute_topo_score(self._build_graph(self._extract_features(cand)['triples'])[0]):.2f}, Inf:{self._compute_inference_score(self._build_graph(self._extract_features(cand)['triples'])[0], self._extract_features(cand)):.2f}"
            })
            scores.append(score)
        
        # Handle ties with NCD (Tiebreaker only)
        # If scores are close, prefer candidate with lower NCD to prompt (higher similarity/context fit)
        final_results = []
        for i, res in enumerate(results):
            # Add NCD as minor perturbation for tie-breaking
            ncd = self._ncd_score(prompt, res['candidate'])
            # Invert NCD so lower distance = higher score addition
            ncd_bonus = (1.0 - ncd) * 0.001 
            res['score'] += ncd_bonus
            final_results.append(res)
            
        # Sort descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results