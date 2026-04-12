from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines measure-theoretic proposition weighting, particle swarm optimization
    with neural oscillation modulation, and constraint propagation.
    
    Parses structural features (negations, comparatives, conditionals, numerics,
    causals, ordering), builds a measure space over propositions, optimizes weights
    via PSO with gamma/theta oscillations, and scores via constraint satisfaction.
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        self.swarm_size = 20
        self.max_iter = 100
        self.omega = 0.5
        self.phi1 = 1.5
        self.phi2 = 1.5
        self.alpha = 0.3
        self.beta = 0.2
        self.f_gamma = 40.0
        self.f_theta = 5.0
    
    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Extract atomic propositions as (type, polarity, content) tuples."""
        props = []
        text_lower = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none)\s+(\w+)', text_lower):
            props.append(('neg', -1, m.group(2)))
        
        # Comparatives with numbers
        for m in re.finditer(r'(\d+\.?\d*)\s*(greater|less|more|fewer|higher|lower)\s*than\s*(\d+\.?\d*)', text_lower):
            props.append(('comp', 1, m.group(1), m.group(2), m.group(3)))
        
        # Conditionals
        for m in re.finditer(r'if\s+([\w\s]+?)\s+then\s+([\w\s]+)', text_lower):
            props.append(('cond', 1, m.group(1).strip(), m.group(2).strip()))
        
        # Numeric values
        for m in re.finditer(r'\b(\d+\.?\d*)\s*(%|percent|dollars|meters|kg|years?|days?|hours?|minutes?)', text_lower):
            props.append(('num', 1, m.group(1), m.group(2)))
        
        # Causals
        for m in re.finditer(r'(because|due\s+to|leads\s+to|results?\s+in|causes?)\s+([\w\s]+)', text_lower):
            props.append(('cause', 1, m.group(1), m.group(2).strip()))
        
        # Ordering
        for m in re.finditer(r'(before|after|first|last|precedes?|follows?)\s+([\w\s]+)', text_lower):
            props.append(('ord', 1, m.group(1), m.group(2).strip()))
        
        # Fallback: extract key content words
        words = re.findall(r'\b\w{4,}\b', text_lower)
        for w in words[:10]:
            props.append(('word', 1, w))
        
        return props
    
    def _build_measure_space(self, all_props: List[List[Tuple]]) -> Tuple[List[Tuple], np.ndarray]:
        """Build sigma-algebra and measure from all propositions."""
        prop_set = set()
        for props in all_props:
            prop_set.update(props)
        
        unique_props = list(prop_set)
        n = len(unique_props)
        
        # Compute frequencies
        freq = {}
        total = sum(len(p) for p in all_props)
        for p in unique_props:
            count = sum(1 for props in all_props for prop in props if prop == p)
            freq[p] = count / max(total, 1)
        
        # IDF-based measure
        mu = np.array([-np.log(freq[p] + self.epsilon) for p in unique_props])
        mu = mu / (mu.sum() + self.epsilon)
        
        return unique_props, mu
    
    def _build_constraint_matrix(self, props: List[Tuple]) -> np.ndarray:
        """Build entailment matrix from proposition rules."""
        n = len(props)
        C = np.eye(n)
        
        # Simple transitivity and logical rules
        for i, pi in enumerate(props):
            for j, pj in enumerate(props):
                # If same type and compatible content, add weak entailment
                if i != j and pi[0] == pj[0]:
                    C[i, j] = 0.3
                
                # Numeric comparisons
                if pi[0] == 'comp' and pj[0] == 'comp' and len(pi) >= 5 and len(pj) >= 5:
                    try:
                        v1, op1, v2 = float(pi[2]), pi[3], float(pi[4])
                        v3, op2, v4 = float(pj[2]), pj[3], float(pj[4])
                        if v1 == v3 and op1 == op2:
                            C[i, j] = 0.7
                    except:
                        pass
        
        return C
    
    def _compute_fitness(self, weights: np.ndarray, C: np.ndarray, ref_truth: np.ndarray) -> float:
        """Constraint propagation fitness."""
        t = 1.0 / (1.0 + np.exp(-C @ weights))
        return 1.0 / (np.linalg.norm(t - ref_truth) + self.epsilon)
    
    def _pso_optimize(self, mu: np.ndarray, C: np.ndarray, ref_truth: np.ndarray) -> np.ndarray:
        """Particle swarm with oscillatory modulation."""
        n = len(mu)
        X = np.random.rand(self.swarm_size, n) * 0.5 + 0.25
        V = np.random.randn(self.swarm_size, n) * 0.1
        pbest = X.copy()
        pbest_fit = np.array([self._compute_fitness(X[k], C, ref_truth) for k in range(self.swarm_size)])
        gbest = pbest[np.argmax(pbest_fit)].copy()
        
        for t in range(self.max_iter):
            for k in range(self.swarm_size):
                fit = self._compute_fitness(X[k], C, ref_truth)
                if fit > pbest_fit[k]:
                    pbest[k] = X[k].copy()
                    pbest_fit[k] = fit
                if fit > pbest_fit.max():
                    gbest = X[k].copy()
            
            r1, r2 = np.random.rand(self.swarm_size, n), np.random.rand(self.swarm_size, n)
            osc_gamma = self.alpha * np.sin(2 * np.pi * self.f_gamma * t / self.max_iter)
            osc_theta = self.beta * np.sin(2 * np.pi * self.f_theta * t / self.max_iter)
            
            V = (self.omega * V + 
                 self.phi1 * r1 * (pbest - X) + 
                 self.phi2 * r2 * (gbest - X) +
                 osc_theta * (gbest - X))
            X = np.clip(X + V, 0, 1)
        
        return gbest
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for epistemic hazards in the prompt."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity + who question
        if re.search(r'\b(he|she|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)', prompt_lower):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by measure-theoretic PSO fitness."""
        prompt_props = self._parse_propositions(prompt)
        cand_props = [self._parse_propositions(c) for c in candidates]
        
        all_props = [prompt_props] + cand_props
        unique_props, mu = self._build_measure_space(all_props)
        
        C = self._build_constraint_matrix(unique_props)
        ref_truth = np.ones(len(unique_props)) * 0.5
        
        results = []
        for idx, cand in enumerate(candidates):
            # Measure-theoretic overlap
            cand_weight = np.zeros(len(unique_props))
            for i, p in enumerate(unique_props):
                if p in cand_props[idx]:
                    cand_weight[i] = mu[i]
            
            # PSO optimization
            opt_weight = self._pso_optimize(mu, C, ref_truth)
            fitness = self._compute_fitness(opt_weight, C, ref_truth)
            overlap = np.minimum(cand_weight, opt_weight).sum()
            
            # Numeric computation bonus
            num_bonus = 0.0
            for m in re.finditer(r'(\d+\.?\d*)', cand):
                num_bonus += 0.05
            
            # NCD tiebreaker (max 15%)
            ncd = len(zlib.compress((prompt + cand).encode())) / max(
                len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())), 1)
            ncd_score = 1.0 - ncd
            
            # Weighted score
            score = 0.5 * overlap + 0.25 * fitness + 0.15 * num_bonus + 0.1 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"overlap={overlap:.3f} fitness={fitness:.3f} ncd={ncd_score:.3f}"
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty."""
        meta_cap = self._meta_confidence(prompt)
        
        results = self.evaluate(prompt, [answer])
        raw_score = results[0]["score"]
        
        # Numeric computation check
        has_numbers = bool(re.search(r'\d+\.?\d*', answer))
        if has_numbers:
            raw_score = min(raw_score * 1.2, 0.85)
        
        # Cap by meta-confidence
        final_conf = min(raw_score, meta_cap, 0.9)
        
        # Never too confident without strong structural match
        if final_conf > 0.7 and not has_numbers:
            final_conf = 0.7
        
        return max(0.0, min(1.0, final_conf))