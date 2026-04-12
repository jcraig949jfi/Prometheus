from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phase Transition x Evolution x Maximum Entropy reasoning tool.
    
    Extracts binary propositions from text, computes maximum-entropy distribution
    over propositions constrained by prompt premises, evolves candidate population
    using fitness based on KL-divergence, and detects phase transition to select
    the best answer. Includes constructive computation for numeric, probabilistic,
    temporal, and causal reasoning.
    """
    
    def __init__(self):
        self.rng = np.random.RandomState(42)
    
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract binary propositions from text using regex patterns."""
        props = []
        text_lower = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none)\s+(\w+)', text_lower):
            props.append(f"NOT_{m.group(2)}")
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|greater|less|more|fewer)\s*than\s*(\w+)', text_lower):
            props.append(f"{m.group(1)}_GT_{m.group(3)}" if '>' in m.group(2) or 'greater' in m.group(2) or 'more' in m.group(2) else f"{m.group(3)}_GT_{m.group(1)}")
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.\,\;]', text_lower):
            props.append(f"IF_{m.group(1).replace(' ','_')}_THEN_{m.group(2).replace(' ','_')}")
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(because|leads to|causes)\s+(\w+)', text_lower):
            props.append(f"{m.group(1)}_CAUSES_{m.group(3)}")
        
        # Numeric with units
        for m in re.finditer(r'(\d+\.?\d*)\s*(\w+)', text):
            props.append(f"NUM_{m.group(1)}_{m.group(2)}")
        
        # Ordering
        for m in re.finditer(r'(first|second|third|before|after)\s+(\w+)', text_lower):
            props.append(f"ORDER_{m.group(1)}_{m.group(2)}")
        
        return list(set(props)) if props else [f"WORD_{w}" for w in text_lower.split()[:10]]
    
    def _build_truth_matrix(self, prompt: str, candidates: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Build N x M binary matrix where N=candidates, M=propositions."""
        all_props = set(self._extract_propositions(prompt))
        for cand in candidates:
            all_props.update(self._extract_propositions(cand))
        
        all_props = sorted(list(all_props))
        if not all_props:
            all_props = ['EMPTY']
        
        X = np.zeros((len(candidates), len(all_props)), dtype=np.float32)
        for i, cand in enumerate(candidates):
            cand_props = set(self._extract_propositions(cand))
            for j, prop in enumerate(all_props):
                X[i, j] = 1.0 if prop in cand_props else 0.0
        
        return X, all_props
    
    def _maxent_inference(self, prompt_props: List[str], all_props: List[str], max_iter: int = 10) -> np.ndarray:
        """Compute maximum entropy marginals via iterative scaling."""
        M = len(all_props)
        p = np.ones(M) * 0.5  # Uniform prior
        
        # Simplified: use prompt propositions as positive evidence
        for prop in prompt_props:
            if prop in all_props:
                idx = all_props.index(prop)
                p[idx] = 0.8  # Bias toward prompt propositions
        
        return np.clip(p, 0.01, 0.99)
    
    def _compute_fitness(self, X: np.ndarray, p: np.ndarray) -> np.ndarray:
        """Compute fitness as negative KL-divergence from maxent marginals."""
        fitness = np.zeros(X.shape[0])
        for i in range(X.shape[0]):
            kl = 0.0
            for j in range(X.shape[1]):
                x_ij = X[i, j]
                if x_ij > 0.5:
                    kl -= np.log(p[j] + 1e-9)
                else:
                    kl -= np.log(1 - p[j] + 1e-9)
            fitness[i] = -kl
        return fitness
    
    def _evolve_population(self, X: np.ndarray, fitness: np.ndarray, generations: int = 5) -> np.ndarray:
        """Evolve population using tournament selection, crossover, mutation."""
        pop_size = X.shape[0]
        for _ in range(generations):
            # Tournament selection
            idx1, idx2 = self.rng.choice(pop_size, 2, replace=False)
            parent = X[idx1] if fitness[idx1] > fitness[idx2] else X[idx2]
            
            # Mutation
            child = parent.copy()
            for j in range(len(child)):
                if self.rng.rand() < 0.05:
                    child[j] = 1 - child[j]
            
            # Replace worst
            worst_idx = np.argmin(fitness)
            X[worst_idx] = child
            fitness[worst_idx] = self._compute_fitness(X[worst_idx:worst_idx+1], fitness)[0]
        
        return fitness
    
    def _compute_answer(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Constructive computation for numeric, temporal, probabilistic reasoning."""
        score = 0.0
        reasoning = []
        
        # Numeric comparison
        prompt_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', prompt)]
        cand_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', candidate)]
        
        if prompt_nums and cand_nums:
            if any(re.search(r'(greater|more|larger|bigger)', prompt.lower())):
                if cand_nums and prompt_nums and cand_nums[0] > prompt_nums[0]:
                    score += 0.3
                    reasoning.append("numeric_greater")
            elif any(re.search(r'(less|fewer|smaller)', prompt.lower())):
                if cand_nums and prompt_nums and cand_nums[0] < prompt_nums[0]:
                    score += 0.3
                    reasoning.append("numeric_less")
        
        # Probability/Bayes
        if re.search(r'(probability|chance|likely)', prompt.lower()):
            if cand_nums and 0 <= cand_nums[0] <= 1:
                score += 0.2
                reasoning.append("valid_probability")
        
        # Temporal ordering
        temporal = re.findall(r'(before|after|first|second|then|next)', prompt.lower())
        if temporal and any(t in candidate.lower() for t in temporal):
            score += 0.2
            reasoning.append("temporal_match")
        
        return score, " ".join(reasoning)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerable questions."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did \w+ (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s+(was|is|were)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', prompt_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)', prompt_lower):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Evaluate candidates using phase-transition evolutionary maxent."""
        if not candidates:
            return []
        
        X, all_props = self._build_truth_matrix(prompt, candidates)
        prompt_props = self._extract_propositions(prompt)
        p_maxent = self._maxent_inference(prompt_props, all_props)
        
        fitness = self._compute_fitness(X, p_maxent)
        fitness = self._evolve_population(X.copy(), fitness.copy())
        
        # Phase transition detection via susceptibility
        beta_range = np.linspace(0.1, 2.0, 10)
        susceptibility = []
        for beta in beta_range:
            scaled_fitness = fitness ** beta
            susceptibility.append(np.var(scaled_fitness))
        
        critical_beta = beta_range[np.argmax(susceptibility)]
        final_fitness = fitness ** critical_beta
        
        # Constructive computation
        results = []
        for i, cand in enumerate(candidates):
            comp_score, reasoning = self._compute_answer(prompt, cand)
            
            # NCD as tiebreaker (<=15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Combine: 50% structure (fitness), 35% computation, 15% NCD
            total_score = 0.5 * (final_fitness[i] / (np.max(final_fitness) + 1e-9)) + 0.35 * comp_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"fitness={final_fitness[i]:.2f} comp={reasoning} beta={critical_beta:.2f}"
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and answer quality."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        # Constructive confidence
        comp_score, reasoning = self._compute_answer(prompt, answer)
        
        # Structural match
        prompt_props = set(self._extract_propositions(prompt))
        answer_props = set(self._extract_propositions(answer))
        overlap = len(prompt_props & answer_props) / (len(prompt_props) + 1e-9)
        
        # Base confidence on computation + structure
        base_conf = 0.4 * comp_score + 0.3 * overlap + 0.3 * (1 - self._ncd(prompt, answer))
        
        # Cap at 0.85 unless definitive computation
        if comp_score < 0.5:
            base_conf = min(base_conf, 0.7)
        
        return float(np.clip(base_conf * meta_conf, 0.0, 0.95))
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0