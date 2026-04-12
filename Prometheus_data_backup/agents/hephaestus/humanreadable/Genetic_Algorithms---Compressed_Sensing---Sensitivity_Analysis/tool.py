from typing import Dict, Tuple

"""
Evolutionary Sparse Constraint Scorer (ESCS)
Combines Genetic Algorithms, Compressed Sensing, and Sensitivity Analysis
with state evolution dynamics tracking for reasoning evaluation.
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)
        self.M = 128  # Feature dimension
        self.K = 32   # Compressed dimension
        self.Phi = np.random.choice([-1, 1], size=(self.K, self.M))
        self.N_pop = 20
        self.N_gen = 15
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        score, _ = self._score_candidate(prompt, answer)
        structural_coverage = self._structural_coverage(prompt, answer)
        if structural_coverage < 0.2:
            return min(0.25, score / 2)
        comp_result = self._compute_if_numeric(prompt, answer)
        if comp_result is not None:
            return 0.92 if comp_result else 0.08
        return min(0.75, 0.3 + score * 0.5)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p_lower):
            return 0.15
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            return 0.22
        # False dichotomy
        if re.search(r'\b(either .+ or)\b', p_lower):
            return 0.25
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.28
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', p_lower):
            return 0.26
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        p_tokens = self._extract_tokens(prompt)
        c_tokens = self._extract_tokens(candidate)
        combined = p_tokens + c_tokens
        
        # Numeric computation
        num_score = self._numeric_eval(prompt, candidate)
        if num_score is not None:
            return num_score, "numeric_computation"
        
        # State evolution dynamics
        dyn_score = self._dynamics_score(prompt, candidate)
        
        # GA-based sparse constraint scoring
        x = self._vectorize(combined)
        constraints = self._build_constraints(p_tokens, c_tokens)
        s = self._sensitivity(x, constraints)
        
        pop = self._init_population(x)
        for gen in range(self.N_gen):
            fitness = self._fitness(pop, s, constraints)
            pop = self._evolve(pop, fitness, s)
        
        final_fitness = self._fitness(pop, s, constraints)
        best_idx = np.argmax(final_fitness)
        ga_score = final_fitness[best_idx]
        
        # NCD (max 15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        # Combine: dynamics 40%, GA 35%, structural 10%, NCD 15%
        final = 0.4 * dyn_score + 0.35 * ga_score + 0.15 * ncd_score + 0.1 * self._structural_score(p_tokens, c_tokens)
        reasoning = f"dyn={dyn_score:.2f} ga={ga_score:.2f} ncd={ncd_score:.2f}"
        return final, reasoning
    
    def _extract_tokens(self, text: str) -> List[str]:
        tokens = []
        t_lower = text.lower()
        # Negations
        tokens.extend(re.findall(r'\b(not|no|never|neither|nor)\b', t_lower))
        # Comparatives
        tokens.extend(re.findall(r'\b(greater|less|more|fewer|larger|smaller|than|above|below)\b', t_lower))
        # Conditionals
        tokens.extend(re.findall(r'\b(if|then|unless|provided|when|whenever)\b', t_lower))
        # Causals
        tokens.extend(re.findall(r'\b(because|since|therefore|thus|hence|leads to|causes)\b', t_lower))
        # Orderings
        tokens.extend(re.findall(r'\b(first|second|before|after|next|last|prior)\b', t_lower))
        # Quantifiers
        tokens.extend(re.findall(r'\b(all|some|every|each|any|none)\b', t_lower))
        # Numbers
        tokens.extend(re.findall(r'\b\d+\.?\d*\b', t_lower))
        return tokens
    
    def _vectorize(self, tokens: List[str]) -> np.ndarray:
        x = np.zeros(self.M)
        for i, tok in enumerate(tokens[:self.M]):
            x[i] = 1.0
        return x
    
    def _build_constraints(self, p_tokens: List[str], c_tokens: List[str]) -> np.ndarray:
        A = np.zeros((10, self.M))
        for i in range(min(10, len(p_tokens))):
            if i < len(p_tokens):
                A[i, i % self.M] = 1.0
        return A
    
    def _sensitivity(self, x: np.ndarray, A: np.ndarray) -> np.ndarray:
        s = np.zeros(self.M)
        baseline = np.linalg.norm(A @ x)
        for j in range(self.M):
            x_flip = x.copy()
            x_flip[j] = 1.0 - x_flip[j]
            flipped = np.linalg.norm(A @ x_flip)
            s[j] = abs(flipped - baseline)
        return s / (np.max(s) + 1e-9)
    
    def _init_population(self, x: np.ndarray) -> np.ndarray:
        pop = np.zeros((self.N_pop, self.M))
        pop[0] = x
        for i in range(1, self.N_pop):
            pop[i] = np.random.binomial(1, 0.3, self.M)
        return pop
    
    def _fitness(self, pop: np.ndarray, s: np.ndarray, A: np.ndarray) -> np.ndarray:
        fit = np.zeros(self.N_pop)
        for i in range(self.N_pop):
            y = self.Phi @ pop[i]
            cs_term = np.linalg.norm(y) ** 2 / (self.K + 1)
            l1_term = np.sum(pop[i])
            sens_term = s @ pop[i]
            fit[i] = cs_term - 0.01 * l1_term + 0.5 * sens_term
        return fit / (np.max(fit) + 1e-9)
    
    def _evolve(self, pop: np.ndarray, fitness: np.ndarray, s: np.ndarray) -> np.ndarray:
        new_pop = np.zeros_like(pop)
        # Elitism
        best_idx = np.argmax(fitness)
        new_pop[0] = pop[best_idx]
        
        for i in range(1, self.N_pop):
            # Tournament selection
            idx1, idx2 = np.random.choice(self.N_pop, 2, replace=False)
            parent = pop[idx1] if fitness[idx1] > fitness[idx2] else pop[idx2]
            child = parent.copy()
            # Sensitivity-guided mutation
            for j in range(self.M):
                if np.random.rand() < 0.1 * (s[j] + 0.1):
                    child[j] = 1.0 - child[j]
            new_pop[i] = child
        return new_pop
    
    def _dynamics_score(self, prompt: str, candidate: str) -> float:
        sentences = re.split(r'[.!?;]', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5
        
        # State vector evolves as we process premises
        state = np.zeros(16)
        trajectory = []
        
        for sent in sentences:
            tokens = self._extract_tokens(sent)
            for tok in tokens[:16]:
                idx = hash(tok) % 16
                state[idx] = 0.7 * state[idx] + 0.3
            trajectory.append(state.copy())
        
        # Candidate influence
        c_tokens = self._extract_tokens(candidate)
        for tok in c_tokens[:16]:
            idx = hash(tok) % 16
            state[idx] = 0.7 * state[idx] + 0.3
        final_state = state.copy()
        
        # Convergence: measure Lyapunov stability
        if len(trajectory) < 2:
            return 0.5
        
        deltas = [np.linalg.norm(trajectory[i+1] - trajectory[i]) for i in range(len(trajectory)-1)]
        convergence = 1.0 / (1.0 + np.mean(deltas))
        
        # Basin stability: how much does final state differ from mean trajectory
        mean_traj = np.mean(trajectory, axis=0)
        stability = 1.0 / (1.0 + np.linalg.norm(final_state - mean_traj))
        
        return 0.6 * convergence + 0.4 * stability
    
    def _structural_score(self, p_tokens: List[str], c_tokens: List[str]) -> float:
        if not p_tokens:
            return 0.0
        overlap = len(set(p_tokens) & set(c_tokens))
        return overlap / len(p_tokens)
    
    def _structural_coverage(self, prompt: str, answer: str) -> float:
        p_tok = self._extract_tokens(prompt)
        a_tok = self._extract_tokens(answer)
        if not p_tok:
            return 0.0
        return len(set(p_tok) & set(a_tok)) / len(p_tok)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        
        if len(nums_p) >= 2 and len(nums_c) >= 1:
            # Comparison detection
            if re.search(r'\b(greater|larger|more|bigger)\b', prompt.lower()):
                try:
                    a, b = float(nums_p[0]), float(nums_p[1])
                    ans = float(nums_c[0])
                    if a > b and abs(ans - a) < 0.01:
                        return 0.95
                    elif b > a and abs(ans - b) < 0.01:
                        return 0.95
                except:
                    pass
            elif re.search(r'\b(less|smaller|fewer)\b', prompt.lower()):
                try:
                    a, b = float(nums_p[0]), float(nums_p[1])
                    ans = float(nums_c[0])
                    if a < b and abs(ans - a) < 0.01:
                        return 0.95
                    elif b < a and abs(ans - b) < 0.01:
                        return 0.95
                except:
                    pass
        return None
    
    def _compute_if_numeric(self, prompt: str, answer: str) -> bool:
        result = self._numeric_eval(prompt, answer)
        if result is not None:
            return result > 0.5
        return None