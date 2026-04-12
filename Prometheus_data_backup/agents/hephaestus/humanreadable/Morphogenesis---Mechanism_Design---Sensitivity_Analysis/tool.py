from typing import Dict, Tuple

"""
Morphogenesis x Mechanism Design x Sensitivity Analysis Reasoning Tool

Builds a belief graph from extracted propositions, runs reaction-diffusion dynamics
with mechanism-design penalties for inconsistencies, and scores by sensitivity analysis.
Includes meta-confidence to detect ambiguous/unanswerable questions (Tier B).
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib


class ReasoningTool:
    def __init__(self):
        self.alpha = 0.2  # diffusion strength
        self.beta = 0.3   # reaction penalty strength
        self.lambda_penalty = 0.5  # inconsistency penalty
        self.tau = 0.1    # tolerance threshold
        self.T = 20       # max iterations
        self.epsilon = 0.01  # convergence threshold
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates using belief-graph morphogenesis + sensitivity."""
        meta_conf = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            # Build belief graph from prompt + candidate
            graph = self._build_graph(prompt, cand)
            if graph['nodes'] == 0:
                # No structure found, use NCD fallback
                score = 0.3 * (1 - self._ncd(prompt, cand))
                results.append({
                    'candidate': cand,
                    'score': score,
                    'reasoning': 'No structural features; NCD fallback'
                })
                continue
            
            # Run reaction-diffusion
            beliefs = self._evolve_beliefs(graph)
            
            # Sensitivity analysis
            sensitivity = self._compute_sensitivity(graph, beliefs)
            robustness = 1.0 / (1.0 + sensitivity)
            
            # Structural score from final beliefs
            struct_score = np.mean(beliefs)
            
            # Computation score (numeric evaluation)
            comp_score = self._compute_score(prompt, cand)
            
            # NCD tiebreaker
            ncd_score = 1 - self._ncd(prompt, cand)
            
            # Weighted combination
            final_score = 0.5 * struct_score + 0.25 * robustness + 0.15 * comp_score + 0.1 * ncd_score
            
            # Cap score if meta-confidence is low
            if meta_conf < 0.3:
                final_score = min(final_score, 0.4)
            
            results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f'Struct:{struct_score:.2f} Robust:{robustness:.2f} Comp:{comp_score:.2f}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        # If question is ambiguous/unanswerable, cap at 0.25
        if meta_conf < 0.3:
            return 0.25
        
        graph = self._build_graph(prompt, answer)
        if graph['nodes'] == 0:
            return 0.3  # Uncertain without structure
        
        beliefs = self._evolve_beliefs(graph)
        consistency = 1.0 - graph['inconsistency']
        
        conf = 0.6 * np.mean(beliefs) + 0.4 * consistency
        return min(conf, 0.85)  # Never exceed 0.85 unless definitive computation
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable questions (Tier B)."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or\b', p) and not re.search(r'\b(only|must)\b', p):
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|criteria)\b', p):
            return 0.25
        
        # Insufficient information markers
        if re.search(r'\b(cannot be determined|not enough|insufficient)\b', p):
            return 0.2
        
        return 1.0  # High meta-confidence (question is answerable)
    
    def _build_graph(self, prompt: str, candidate: str) -> Dict:
        """Extract propositions and build weighted directed graph."""
        text = prompt + ' ' + candidate
        props = []
        edges = []
        weights = []
        
        # Extract propositions (simple sentence splitting)
        sentences = re.split(r'[.!?;]', text)
        props = [s.strip() for s in sentences if len(s.strip()) > 3]
        
        if not props:
            return {'nodes': 0, 'edges': [], 'weights': [], 'inconsistency': 0}
        
        n = len(props)
        
        # Extract relations
        for i, p in enumerate(props):
            pl = p.lower()
            
            # Negation (self-loop)
            if re.search(r'\b(not|no|never|n\'t)\b', pl):
                edges.append((i, i))
                weights.append(-0.5)
            
            # Implication (if-then)
            if re.search(r'\bif .+ then\b', pl):
                for j in range(n):
                    if i != j:
                        edges.append((i, j))
                        weights.append(1.0)
            
            # Causal
            if re.search(r'\b(cause|lead|result|because)\b', pl):
                for j in range(i+1, n):
                    edges.append((i, j))
                    weights.append(1.0)
            
            # Comparative
            if re.search(r'\b(greater|less|more|fewer|higher|lower|<|>)\b', pl):
                for j in range(i+1, n):
                    edges.append((i, j))
                    weights.append(0.8)
        
        # Detect inconsistency
        inconsistency = self._detect_inconsistency(props)
        
        return {'nodes': n, 'edges': edges, 'weights': weights, 'inconsistency': inconsistency}
    
    def _detect_inconsistency(self, props: List[str]) -> float:
        """Check for contradictions."""
        count = 0
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i >= j:
                    continue
                # Simple negation check
                if ('not' in p1.lower() and p2.lower().replace('not', '').strip() in p1.lower()) or \
                   ('not' in p2.lower() and p1.lower().replace('not', '').strip() in p2.lower()):
                    count += 1
        return min(count * 0.3, 1.0)
    
    def _evolve_beliefs(self, graph: Dict) -> np.ndarray:
        """Run reaction-diffusion on belief graph."""
        n = graph['nodes']
        s = np.ones(n) * 0.5  # Initial beliefs
        
        # Build adjacency matrix
        W = np.zeros((n, n))
        for (i, j), w in zip(graph['edges'], graph['weights']):
            W[i, j] = w
        
        # Laplacian
        D = np.diag(W.sum(axis=1))
        L = D - W
        
        # Iterate
        for t in range(self.T):
            s_old = s.copy()
            
            # Diffusion term
            diffusion = -self.alpha * (L @ s)
            
            # Reaction term (penalty for inconsistency)
            reaction = self.beta * self.lambda_penalty * max(0, graph['inconsistency'] - self.tau) * s
            
            s = s + diffusion - reaction
            s = np.clip(s, 0, 1)
            
            if np.linalg.norm(s - s_old, 1) < self.epsilon:
                break
        
        return s
    
    def _compute_sensitivity(self, graph: Dict, beliefs: np.ndarray) -> float:
        """Perturb edge weights and measure belief change."""
        if not graph['edges']:
            return 0.0
        
        delta_w = 0.01
        n = graph['nodes']
        total_sensitivity = 0.0
        
        for idx in range(min(3, len(graph['edges']))):  # Sample a few edges
            # Perturb
            graph_perturbed = graph.copy()
            graph_perturbed['weights'] = graph['weights'].copy()
            graph_perturbed['weights'][idx] += delta_w
            
            # Re-evolve
            beliefs_perturbed = self._evolve_beliefs(graph_perturbed)
            
            # Measure change
            sensitivity = np.abs(beliefs_perturbed - beliefs).sum() / n
            total_sensitivity += sensitivity / delta_w
        
        return total_sensitivity / min(3, len(graph['edges']))
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Computational reasoning: numeric comparison, arithmetic."""
        score = 0.0
        
        # Numeric comparison
        nums_prompt = re.findall(r'\d+\.?\d*', prompt)
        nums_cand = re.findall(r'\d+\.?\d*', candidate)
        
        if len(nums_prompt) >= 2 and nums_cand:
            try:
                a, b = float(nums_prompt[0]), float(nums_prompt[1])
                if re.search(r'\b(greater|more|larger|higher)\b', prompt.lower()):
                    if nums_cand and float(nums_cand[0]) == max(a, b):
                        score += 0.5
                elif re.search(r'\b(less|fewer|smaller|lower)\b', prompt.lower()):
                    if nums_cand and float(nums_cand[0]) == min(a, b):
                        score += 0.5
            except:
                pass
        
        # Arithmetic expression evaluation
        if '+' in prompt or '-' in prompt or '*' in prompt:
            try:
                expr = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', prompt)
                if expr:
                    a, op, b = int(expr.group(1)), expr.group(2), int(expr.group(3))
                    result = eval(f'{a}{op}{b}')
                    if nums_cand and abs(float(nums_cand[0]) - result) < 0.01:
                        score += 0.5
            except:
                pass
        
        return min(score, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0