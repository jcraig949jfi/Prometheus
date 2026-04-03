import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Multi-Armed Bandit + NAS + Metamorphic Testing reasoning tool.
    
    Maintains a population of parsing strategies (arms) that extract structural
    relations. Each arm consists of (pattern_set, weight_vector). Uses UCB to
    select arms, evaluates via metamorphic relation violations, and mutates
    poor performers. Prioritizes epistemic honesty on ambiguous questions.
    """
    
    def __init__(self):
        # Initialize bandit arms: (pattern_set_id, weight_vector)
        self.arms = []
        self.arm_stats = []  # (sum_reward, n_pulls)
        self.total_pulls = 0
        self.c_ucb = 1.0
        
        # Pattern sets for NAS
        self.pattern_templates = [
            ('neg', r'\b(not|no|never|n\'t)\s+(\w+)'),
            ('comp_gt', r'(\w+)\s+(>|greater|more|larger|higher)\s+than\s+(\w+)'),
            ('comp_lt', r'(\w+)\s+(<|less|fewer|smaller|lower)\s+than\s+(\w+)'),
            ('conditional', r'\b(if|when)\s+(.+?)\s+then\s+(.+)'),
            ('numeric', r'\b(\d+\.?\d*)\b'),
            ('causal', r'(\w+)\s+(because|leads to|causes)\s+(\w+)'),
            ('order', r'(\w+)\s+(before|after|first|last)\s+(\w+)'),
        ]
        
        # Initialize 3 arms with different pattern combinations
        for i in range(3):
            patterns = self.pattern_templates[i::3] if i < 3 else self.pattern_templates[:4]
            weights = np.random.randn(len(patterns)) * 0.1 + 1.0
            self.arms.append((patterns, weights))
            self.arm_stats.append([0.0, 0])
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability - FIRST line of defense."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X did a Y"
        if re.search(r'\bevery\s+\w+.*\b(a|an)\s+\w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|they|it)\s+', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.2
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\s+\w+\s+or\s+\w+', p_lower):
            return 0.25
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|criteria|metric)\b', p_lower):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'\b(insufficient|not enough|missing|unknown)\s+(information|data)', p_lower):
            return 0.2
        
        return 1.0  # No ambiguity detected
    
    def _extract_relations(self, text: str, patterns: List[Tuple]) -> List[Tuple]:
        """Extract structural relations using pattern set."""
        relations = []
        for ptype, regex in patterns:
            for match in re.finditer(regex, text, re.IGNORECASE):
                relations.append((ptype, match.groups()))
        return relations
    
    def _generate_metamorphic_relations(self, prompt_rels: List[Tuple]) -> List[Tuple]:
        """Generate MRs from prompt relations."""
        mrs = []
        for ptype, groups in prompt_rels:
            if ptype == 'neg':
                mrs.append(('neg_flip', groups))
            elif ptype in ['comp_gt', 'comp_lt']:
                mrs.append(('comp_preserve', groups))
            elif ptype == 'numeric':
                mrs.append(('numeric_scale', groups))
            elif ptype == 'conditional':
                mrs.append(('cond_preserve', groups))
        return mrs
    
    def _check_violations(self, prompt_rels: List[Tuple], answer_rels: List[Tuple], 
                          mrs: List[Tuple], weights: np.ndarray) -> float:
        """Compute weighted violation score."""
        if not mrs:
            return 0.5
        
        violations = 0
        for i, (mr_type, mr_data) in enumerate(mrs):
            w = weights[min(i, len(weights)-1)]
            
            if mr_type == 'neg_flip':
                # Check if negation is handled
                has_neg = any(r[0] == 'neg' for r in answer_rels)
                if not has_neg:
                    violations += abs(w)
            
            elif mr_type == 'numeric_scale':
                # Extract numbers and check ordering preserved
                p_nums = [float(g[0]) for t, g in prompt_rels if t == 'numeric']
                a_nums = [float(g[0]) for t, g in answer_rels if t == 'numeric']
                if p_nums and not a_nums:
                    violations += abs(w)
        
        return 1.0 - min(1.0, violations / (len(mrs) + 1))
    
    def _ucb_score(self, arm_idx: int) -> float:
        """Compute UCB score for arm."""
        if self.arm_stats[arm_idx][1] == 0:
            return float('inf')
        
        mean_reward = self.arm_stats[arm_idx][0] / self.arm_stats[arm_idx][1]
        exploration = self.c_ucb * np.sqrt(np.log(self.total_pulls + 1) / self.arm_stats[arm_idx][1])
        return mean_reward + exploration
    
    def _mutate_arm(self, arm_idx: int):
        """NAS-style mutation of worst arm."""
        patterns, weights = self.arms[arm_idx]
        
        if np.random.rand() < 0.5 and len(patterns) < len(self.pattern_templates):
            # Add pattern
            new_pat = self.pattern_templates[len(patterns) % len(self.pattern_templates)]
            patterns = list(patterns) + [new_pat]
            weights = np.append(weights, np.random.randn() * 0.1 + 1.0)
        else:
            # Perturb weights
            weights = weights + np.random.randn(len(weights)) * 0.2
        
        self.arms[arm_idx] = (patterns, weights)
    
    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Evaluate single candidate using bandit."""
        # Select arm via UCB
        ucb_scores = [self._ucb_score(i) for i in range(len(self.arms))]
        arm_idx = int(np.argmax(ucb_scores))
        
        patterns, weights = self.arms[arm_idx]
        
        # Extract relations
        p_rels = self._extract_relations(prompt, patterns)
        a_rels = self._extract_relations(candidate, patterns)
        
        # Generate MRs and compute violations
        mrs = self._generate_metamorphic_relations(p_rels)
        reward = self._check_violations(p_rels, a_rels, mrs, weights)
        
        # Numeric computation component (>=20%)
        numeric_score = self._numeric_eval(prompt, candidate)
        
        # NCD component (<=15%)
        ncd = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd
        
        # Combine: structural 65%, numeric 25%, NCD 10%
        final_score = 0.65 * reward + 0.25 * numeric_score + 0.10 * ncd_score
        
        # Update bandit stats
        self.arm_stats[arm_idx][0] += reward
        self.arm_stats[arm_idx][1] += 1
        self.total_pulls += 1
        
        # Mutate worst arm every 20 pulls
        if self.total_pulls % 20 == 0:
            worst = min(range(len(self.arms)), 
                       key=lambda i: self.arm_stats[i][0]/(self.arm_stats[i][1]+1))
            self._mutate_arm(worst)
        
        reasoning = f"Arm{arm_idx} reward={reward:.2f}, numeric={numeric_score:.2f}, NCD={ncd_score:.2f}"
        return final_score, reasoning
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Constructive numeric computation."""
        # Extract all numbers
        p_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', candidate)]
        
        if not p_nums:
            return 0.5
        
        # Check comparison consistency
        if re.search(r'(\d+\.?\d*)\s*(<|>|less|greater|more)\s*(\d+\.?\d*)', prompt):
            match = re.search(r'(\d+\.?\d*)\s*(<|>|less|greater|more)\s*(\d+\.?\d*)', prompt)
            n1, op, n2 = float(match.group(1)), match.group(2), float(match.group(3))
            
            correct = (('<' in op or 'less' in op) and n1 < n2) or \
                     (('>' in op or 'greater' in op or 'more' in op) and n1 > n2)
            
            # Check if candidate reflects this
            if c_nums:
                return 1.0 if correct else 0.3
        
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by score."""
        results = []
        for cand in candidates:
            score, reasoning = self._evaluate_candidate(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1. PRIORITIZES epistemic honesty."""
        # FIRST: Check if question itself is problematic
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate answer quality
        score, _ = self._evaluate_candidate(prompt, answer)
        
        # Cap confidence - never overconfident unless constructive proof
        base_conf = min(0.85, score)
        
        # Further cap by meta-confidence
        return min(base_conf, meta_conf)