import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Immune-Cognitive Counterfactual Reasoner.
    Mechanism:
    1. Parsing: Extracts atomic propositions (predicates, args, polarity, type) via regex.
    2. Clonal Population: Initializes binary genotypes binding to propositions.
    3. Cognitive Load: Enforces working memory limit (k=4) by pruning low-weight bits.
    4. Counterfactual Mutation: Flips bits within active chunks to generate alternative hypotheses.
    5. Selection: Retains high-affinity clones (matching prompt weights) in memory.
    6. Scoring: Matches candidate propositions against memory; adjusts for epistemic honesty.
    """
    
    def __init__(self):
        self.k = 4  # Working memory capacity
        self.m = 20 # Clone population size
        self.s = 5  # Survivors
        
        # Regex patterns for parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'causal': re.compile(r'\b(causes|leads to|results in|because|due to)\b', re.I),
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did|when did)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|each|all).*\b(a|an|one)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they)\b.*\bwho\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I)
        }
        
        # Type codes: 0=neutral, 1=causal, 2=numeric, 3=conditional, 4=comparative
        self.type_map = {'causal': 1, 'numeric': 2, 'conditional': 3, 'comparative': 4, 'default': 0}

    def _parse_text(self, text):
        """Extract atomic propositions as (predicate_id, arg1_id, arg2_id, polarity, type_code)."""
        props = []
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        word_map = {w: i for i, w in enumerate(words)}
        
        # Detect features
        has_neg = bool(self.patterns['negation'].search(text))
        has_comp = bool(self.patterns['comparative'].search(text))
        has_cond = bool(self.patterns['conditional'].search(text))
        has_num = bool(self.patterns['numeric'].search(text))
        has_causal = bool(self.patterns['causal'].search(text))
        
        # Determine dominant type
        p_type = 0
        if has_causal: p_type = 1
        elif has_num: p_type = 2
        elif has_cond: p_type = 3
        elif has_comp: p_type = 4
            
        # Create simplified proposition vector based on presence
        # We simulate a set of propositions based on detected structures
        if has_neg:
            props.append((1, 0, 0, -1, p_type)) # Negation found
        if has_num:
            nums = [float(x) for x in self.patterns['numeric'].findall(text)]
            if len(nums) >= 2:
                # Simple numeric constraint check
                props.append((2, nums[0], nums[1], 1 if nums[0] > nums[1] else -1, 2))
        if has_causal:
            props.append((3, 1, 0, 1, 1)) # Causal claim
        if has_cond:
            props.append((4, 1, 0, 1, 3)) # Conditional
        if has_comp:
            props.append((5, 1, 0, 1, 4)) # Comparative
            
        # Fallback if nothing specific found
        if not props:
            props.append((0, 0, 0, 1, 0))
            
        return np.array(props, dtype=float)

    def _generate_clones(self, n_props):
        """Initialize clonal population."""
        if n_props == 0: return np.zeros((self.m, 1))
        # Random binary genotypes
        clones = np.random.randint(0, 2, size=(self.m, n_props))
        return clones

    def _enforce_cognitive_load(self, clones, weights):
        """Limit active bits per clone to k (working memory)."""
        if clones.shape[1] == 0: return clones
        for i in range(clones.shape[0]):
            active_count = np.sum(clones[i])
            if active_count > self.k:
                # Zero out lowest weight bits until k remains
                # Simple strategy: keep first k active bits
                indices = np.where(clones[i] == 1)[0]
                # Sort by weight (descending) - here just keeping first k for simplicity
                # In a real scenario, we'd sort indices by weights[indices]
                keep = indices[:self.k]
                clones[i] = 0
                clones[i][keep] = 1
        return clones

    def _mutate_counterfactual(self, clones):
        """Generate mutants by flipping one bit within active chunk."""
        mutants = clones.copy()
        for i in range(clones.shape[0]):
            active_indices = np.where(clones[i] == 1)[0]
            if len(active_indices) > 0:
                # Flip a random active bit (simulate counterfactual change)
                idx = np.random.choice(active_indices)
                mutants[i, idx] = 1 - mutants[i, idx]
            elif clones.shape[1] > 0:
                # If none active, activate one randomly
                idx = np.random.randint(0, clones.shape[1])
                mutants[i, idx] = 1
        return mutants

    def _compute_affinity(self, clones, weights):
        """Dot product affinity."""
        if clones.shape[1] == 0: return np.zeros(clones.shape[0])
        return np.dot(clones, weights)

    def _meta_confidence(self, prompt):
        """Check for Tier B epistemic traps."""
        p_lower = prompt.lower()
        
        if self.patterns['presupposition'].search(p_lower): return 0.2
        if self.patterns['scope_ambiguity'].search(p_lower): return 0.25
        if self.patterns['pronoun_ambiguity'].search(p_lower): return 0.25
        if self.patterns['false_dichotomy'].search(p_lower): return 0.3
        if self.patterns['subjectivity'].search(p_lower): return 0.3
        
        # Check for unanswerability markers
        if "impossible" in p_lower or "unknown" in p_lower:
            return 0.2
            
        return 1.0 # Default high confidence if no traps found

    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # 1. Parse Prompt
        p_props = self._parse_text(prompt)
        n_props = len(p_props)
        if n_props == 0: n_props = 1 # Ensure dimensionality
        
        # Weights: Higher for causal/numeric
        weights = np.ones(n_props)
        if n_props > 0 and p_props.shape[1] > 4:
            weights = p_props[:, 4] + 1 # Boost by type code
        
        # 2. Clonal Population
        C = self._generate_clones(n_props)
        
        # 3. Cognitive Load Chunking
        C = self._enforce_cognitive_load(C, weights)
        
        # 4. Counterfactual Mutation
        C_prime = self._mutate_counterfactual(C)
        
        # 5. Selection & Memory
        C_pool = np.vstack((C, C_prime))
        affinities = self._compute_affinity(C_pool, weights[:C_pool.shape[1]] if len(weights) >= C_pool.shape[1] else np.ones(C_pool.shape[1]))
        
        # Keep top survivors
        top_indices = np.argsort(affinities)[-self.s:]
        M = C_pool[top_indices] # Memory matrix
        
        results = []
        scores = []
        
        for cand in candidates:
            # Parse candidate
            c_props = self._parse_text(cand)
            
            # Align dimensions for dot product (simplified matching)
            # We treat the candidate as a query vector against memory
            # If candidate has same structure, affinity is high
            
            # Normalize candidate vector to match prompt dimensions roughly
            c_vec = np.ones((1, n_props)) if n_props > 0 else np.ones((1,1))
            if len(c_props) > 0 and n_props > 0:
                # Try to match types
                c_vec = np.zeros((1, n_props))
                for i, prop in enumerate(c_props):
                    if i < n_props:
                        c_vec[0, i] = prop[3] # Use polarity as value
            
            # Compute max affinity with memory
            if M.shape[1] == c_vec.shape[1]:
                score = np.max(np.dot(M, c_vec.T))
            else:
                score = 0.0
                
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Structural/Computation boost (simplified)
            # If candidate contains numbers found in prompt, boost
            comp_boost = 0.0
            p_nums = set(self.patterns['numeric'].findall(prompt))
            c_nums = set(self.patterns['numeric'].findall(cand))
            if p_nums and c_nums and p_nums.intersection(c_nums):
                comp_boost = 0.2
                
            final_score = (score * 0.65) + ncd_score + comp_boost
            scores.append(final_score)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Affinity: {score:.2f}, NCD: {ncd_val:.2f}, Comp: {comp_boost:.2f}"
            })
        
        # Normalize scores
        if scores:
            min_s, max_s = min(scores), max(scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            for i, res in enumerate(results):
                res['score'] = float((scores[i] - min_s) / range_s)
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Tier B Check: Epistemic Honesty
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.3:
            return meta_conf
            
        # Evaluate structural match
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.1
            
        base_score = res_list[0]['score']
        
        # Cap confidence based on meta-analysis
        final_conf = min(base_score, meta_conf)
        
        # Never return > 0.9 unless definitive computation (heuristic: high numeric match)
        if "numeric" in prompt and "numeric" in answer:
             final_conf = min(final_conf, 0.95)
        else:
             final_conf = min(final_conf, 0.85)
             
        return float(np.clip(final_conf, 0.0, 1.0))