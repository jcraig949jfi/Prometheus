import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Evolution x Epigenetics x Sparse Coding reasoning tool.
    
    Mechanism:
    1. Parse propositions (negation, comparative, conditional, causal, numeric, etc.) from text
    2. Represent as sparse coded array with epigenetic weights (context-dependent)
    3. Use evolutionary optimization to find most consistent, sparse proposition set
    4. Compute fitness as -(violations + sparsity_penalty)
    5. Return meta-confidence-adjusted scores based on logical consistency
    """
    
    def __init__(self):
        self.lambda_sparse = 0.1
        self.pop_size = 20
        self.generations = 5
        
    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Extract logical propositions as (type, polarity, subj, obj, value, modality)"""
        props = []
        text_lower = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|neither)\s+(\w+)', text_lower):
            props.append(('negation', -1, m.group(2), '', 0, 'none'))
        
        # Comparatives with numbers
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|greater|less)\s*(\d+\.?\d*)', text_lower):
            props.append(('comparative', 1, m.group(1), m.group(3), float(m.group(1)), m.group(2)))
        
        # Conditionals
        for m in re.finditer(r'if\s+(\w+).*?then\s+(\w+)', text_lower):
            props.append(('conditional', 1, m.group(1), m.group(2), 0, 'if-then'))
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|leads to|results in|causes)\s+(\w+)', text_lower):
            props.append(('causal', 1, m.group(1), m.group(3), 0, m.group(2)))
        
        # Numeric values
        for m in re.finditer(r'\b(\d+\.?\d*)\s*([a-z%]+)?', text_lower):
            props.append(('numeric', 1, m.group(1), m.group(2) or '', float(m.group(1)), 'value'))
        
        # Modals
        for m in re.finditer(r'\b(must|might|could|should|may)\s+(\w+)', text_lower):
            props.append(('modal', 1, m.group(2), '', 0, m.group(1)))
        
        return props
    
    def _epigenetic_weights(self, props: List[Tuple], text: str) -> np.ndarray:
        """Apply context-dependent weights to propositions"""
        w = np.ones(len(props))
        text_lower = text.lower()
        
        for i, (ptype, pol, subj, obj, val, mod) in enumerate(props):
            if ptype == 'negation':
                w[i] *= -1
            if ptype == 'causal' or 'because' in text_lower:
                w[i] *= 1.5
            if mod in ['might', 'could', 'may']:
                w[i] *= 0.5
            if ptype == 'modal' and mod in ['might', 'could']:
                w[i] *= 0.5
        
        return w
    
    def _constraint_violations(self, props: List[Tuple], active: np.ndarray) -> int:
        """Count logical inconsistencies in active propositions"""
        violations = 0
        active_props = [p for i, p in enumerate(props) if active[i]]
        
        # Check numeric comparatives
        nums = {}
        for ptype, pol, subj, obj, val, mod in active_props:
            if ptype == 'numeric':
                nums[subj] = val
        
        for ptype, pol, subj, obj, val, mod in active_props:
            if ptype == 'comparative':
                v1 = nums.get(subj, val)
                v2 = nums.get(obj, float(obj) if obj.replace('.','').isdigit() else 0)
                if '>' in mod or 'greater' in mod:
                    if not v1 > v2:
                        violations += 1
                elif '<' in mod or 'less' in mod:
                    if not v1 < v2:
                        violations += 1
        
        # Check conditionals (modus ponens)
        for i, (pt1, pol1, s1, o1, v1, m1) in enumerate(active_props):
            if pt1 == 'conditional':
                antecedent_active = any(s1 in p[2] for p in active_props)
                consequent_active = any(o1 in p[2] for p in active_props)
                if antecedent_active and not consequent_active:
                    violations += 1
        
        return violations
    
    def _compute_numeric_answer(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Constructive computation for numeric questions"""
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if not cand_nums:
            return False, 0.0
        
        # Detect comparison questions
        if re.search(r'(greater|less|more|fewer|larger|smaller)', prompt.lower()):
            if len(prompt_nums) >= 2:
                p1, p2 = prompt_nums[0], prompt_nums[1]
                if 'greater' in prompt.lower() or 'more' in prompt.lower() or 'larger' in prompt.lower():
                    correct = max(p1, p2)
                else:
                    correct = min(p1, p2)
                if cand_nums and abs(cand_nums[0] - correct) < 0.01:
                    return True, 1.0
                else:
                    return True, 0.0
        
        return False, 0.5
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable questions and cap confidence"""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did.*fail|why did.*stop)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who\?', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either.*or', prompt_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', prompt_lower):
            return 0.35
        
        # Unanswerability markers
        if re.search(r'(cannot be determined|insufficient|not enough information)', prompt_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def _evolutionary_fitness(self, prompt: str, candidate: str) -> float:
        """Run genetic algorithm to find best sparse consistent explanation"""
        props_p = self._parse_propositions(prompt)
        props_c = self._parse_propositions(candidate)
        all_props = props_p + props_c
        
        if not all_props:
            return 0.0
        
        weights = self._epigenetic_weights(all_props, prompt + " " + candidate)
        n = len(all_props)
        
        # Seed RNG deterministically
        seed = hash(prompt + candidate) % (2**32)
        rng = np.random.RandomState(seed)
        
        # Initialize population
        population = [rng.random(n) > 0.5 for _ in range(self.pop_size)]
        
        best_fitness = -float('inf')
        
        for gen in range(self.generations):
            fitnesses = []
            for active in population:
                violations = self._constraint_violations(all_props, active)
                sparsity = self.lambda_sparse * np.sum(active)
                fitness = -(violations + sparsity)
                fitnesses.append(fitness)
            
            best_fitness = max(best_fitness, max(fitnesses))
            
            # Selection (top 20%)
            sorted_idx = np.argsort(fitnesses)[::-1]
            survivors = [population[i] for i in sorted_idx[:self.pop_size // 5]]
            
            # Generate next generation
            new_pop = survivors[:]
            while len(new_pop) < self.pop_size:
                parent = survivors[rng.randint(len(survivors))]
                child = parent.copy()
                # Mutation
                if rng.random() < 0.3:
                    flip_idx = rng.randint(n)
                    child[flip_idx] = not child[flip_idx]
                new_pop.append(child)
            
            population = new_pop
        
        return best_fitness
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (minimal use)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by evolutionary fitness + computation + minimal NCD"""
        results = []
        
        for cand in candidates:
            # Constructive computation (40%)
            computed, comp_score = self._compute_numeric_answer(prompt, cand)
            
            # Evolutionary fitness (50%)
            evo_score = self._evolutionary_fitness(prompt, cand)
            evo_normalized = 1.0 / (1.0 + np.exp(-evo_score))  # Sigmoid
            
            # NCD tiebreaker (10%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combine
            if computed:
                score = 0.5 * comp_score + 0.4 * evo_normalized + 0.1 * ncd_score
            else:
                score = 0.6 * evo_normalized + 0.4 * ncd_score
            
            # Extract reasoning summary
            n_props = len(self._parse_propositions(cand))
            reasoning = f"Props:{n_props} Evo:{evo_normalized:.2f} Comp:{comp_score:.2f if computed else 0:.2f}"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence"""
        # Meta-confidence check (epistemic honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # Compute structural confidence
        computed, comp_score = self._compute_numeric_answer(prompt, answer)
        if computed:
            base_conf = comp_score
        else:
            evo_score = self._evolutionary_fitness(prompt, answer)
            base_conf = 1.0 / (1.0 + np.exp(-evo_score))
        
        # Apply meta-cap
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 unless definitive computation
        if not computed or comp_score < 1.0:
            final_conf = min(final_conf, 0.85)
        
        return float(np.clip(final_conf, 0.0, 1.0))