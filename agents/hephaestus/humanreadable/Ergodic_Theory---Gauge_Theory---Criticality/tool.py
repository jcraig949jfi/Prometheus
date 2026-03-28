import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator fusing Ergodic Theory and Criticality.
    Mechanism:
    1. Parses text into a proposition graph (nodes=propositions, edges=logic).
    2. Ergodic Walk: Traverses the graph to compute time-averaged feature states.
    3. Criticality: Measures feature dispersion (susceptibility) across the graph.
    4. Scoring: Maximizes ergodic stability (time avg ~ space avg) and minimizes 
       susceptibility (low variance indicates robust logic). 
    Gauge Theory is restricted to the confidence wrapper as per historical constraints.
    """
    
    def __init__(self):
        self.operators = {'if': 'implies', 'then': 'implies', 'causes': 'causes', 
                          'leads to': 'causes', 'before': 'orders', 'after': 'orders',
                          'all': 'forall', 'some': 'exists', 'none': 'none'}
        self.comparators = ['>', '<', '>=', '<=', '=', '==']
        
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions and features."""
        props = []
        sentences = re.split(r'[.!?]', text.lower())
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # Features
            has_neg = 1 if re.search(r'\b(not|no|never|none)\b', sent) else 0
            nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', sent)]
            norm_num = (nums[0] / 100.0) if nums else 0.0  # Simple normalization
            
            # Relation type
            rel_type = 0
            for key, val in self.operators.items():
                if key in sent:
                    rel_type = hash(val) % 1000 / 1000.0
                    break
            
            # Conditional depth (rough estimate)
            cond_depth = sent.count('if') + sent.count('then')
            
            props.append({
                'text': sent,
                'features': np.array([has_neg, norm_num, rel_type, cond_depth])
            })
        return props

    def _build_graph(self, props: List[Dict]) -> Tuple[np.ndarray, List[List[int]]]:
        """Build feature matrix and adjacency list."""
        if not props:
            return np.zeros((0, 4)), []
        
        F = np.vstack([p['features'] for p in props])
        n = len(props)
        adj = [[] for _ in range(n)]
        
        # Connect sequential propositions (temporal/logical flow)
        for i in range(n - 1):
            adj[i].append(i + 1)
            # Add reverse for ergodic mixing
            if i > 0: adj[i].append(i-1) 
            
        return F, adj

    def _ergodic_walk(self, F: np.ndarray, adj: List[List[int]], steps: int = 50) -> np.ndarray:
        """Perform deterministic ergodic walk to compute time-averaged features."""
        if F.shape[0] == 0:
            return np.zeros(4)
        
        n = F.shape[0]
        current = 0
        time_avg = np.zeros(F.shape[1])
        
        # Deterministic walk: follow edges, restart if stuck
        for t in range(steps):
            time_avg += F[current]
            neighbors = adj[current]
            if neighbors:
                # Move to next neighbor (cyclic deterministic)
                current = neighbors[t % len(neighbors)]
            else:
                current = (current + 1) % n # Restart logic
                
        return time_avg / steps

    def _compute_criticality(self, F: np.ndarray) -> float:
        """Compute susceptibility (trace of covariance matrix)."""
        if F.shape[0] < 2:
            return 0.0
        mu = np.mean(F, axis=0)
        diff = F - mu
        cov = np.dot(diff.T, diff) / F.shape[0]
        return float(np.trace(cov))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_props = self._parse_propositions(prompt)
        prompt_F, prompt_adj = self._build_graph(prompt_props)
        
        # Global space average from prompt (reference)
        if prompt_F.shape[0] > 0:
            mu_space = np.mean(prompt_F, axis=0)
        else:
            mu_space = np.zeros(4)

        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            cand_F, cand_adj = self._build_graph(cand_props)
            
            score = 0.0
            reasoning = "Structural analysis failed."
            
            if cand_F.shape[0] == 0:
                # Fallback for empty parses
                score = -10.0
                reasoning = "No logical structure detected."
            else:
                # 1. Ergodic Average of candidate
                g_avg = self._ergodic_walk(cand_F, cand_adj)
                
                # 2. Criticality (Susceptibility) of candidate
                susceptibility = self._compute_criticality(cand_F)
                
                # 3. Stability Score: Minimize distance between ergodic time-average 
                #    and the prompt's spatial mean (consistency check)
                #    Also penalize high susceptibility (criticality)
                dist = np.linalg.norm(g_avg - mu_space[:4]) # Truncate if needed
                
                # Scoring function: Higher is better
                # - Distance penalty (consistency)
                # - Susceptibility penalty (stability)
                # - Bonus for matching numeric constraints if present
                numeric_bonus = 0.0
                if len(cand_props) > 0 and len(prompt_props) > 0:
                     # Simple heuristic: if numbers exist, check order preservation roughly
                     p_nums = [p['features'][1] for p in prompt_props if p['features'][1] != 0]
                     c_nums = [p['features'][1] for p in cand_props if p['features'][1] != 0]
                     if p_nums and c_nums:
                         # Check if relative order is preserved (simplified)
                         if (p_nums[0] > p_nums[-1]) == (c_nums[0] > c_nums[-1]):
                             numeric_bonus = 0.5

                score = -dist - 0.5 * susceptibility + numeric_bonus
                reasoning = f"Ergodic stability: {-dist:.2f}, Susceptibility: {-susceptibility:.2f}"

            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Gauge-theoretic confidence wrapper.
        Estimates confidence based on structural density and lack of contradiction.
        Returns 0.0 to 1.0.
        """
        props = self._parse_propositions(f"{prompt} {answer}")
        if not props:
            return 0.1
        
        # Gauge factor: Density of logical operators (connection strength)
        n_props = len(props)
        if n_props == 0: return 0.0
        
        # Count connections (gauge links)
        links = 0
        for p in props:
            txt = p['text']
            for k in self.operators:
                if k in txt: links += 1
        
        # Normalized link density
        density = links / max(1, n_props)
        
        # Penalty for negation loops (simple proxy for curvature/contradiction)
        neg_count = sum(1 for p in props if p['features'][0] == 1)
        curvature_penalty = min(1.0, neg_count / max(1, n_props)) * 0.5
        
        # Base confidence from density, reduced by curvature
        conf = (0.5 + 0.5 * density) - curvature_penalty
        return float(np.clip(conf, 0.0, 1.0))