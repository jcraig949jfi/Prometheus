class ReasoningTool:
    """
    Belief-Bandit Evaluator integrating Gene Regulatory Networks (GRN), 
    Active Inference (Free Energy), and Multi-Armed Bandits (Thompson Sampling).
    
    Mechanism:
    1. Parsing: Extracts propositions and relations (negation, comparative, causal) into an adjacency matrix.
    2. GRN Propagation: Iteratively updates belief states using sigmoidal message passing to enforce logical consistency.
    3. Active Inference: Computes Expected Free Energy (G) as a coherence score (lower G = better).
    4. Bandit Allocation: Uses Thompson Sampling on Beta posteriors to rank candidates, balancing exploration/exploitation.
    5. Epistemic Honesty: Meta-analysis of prompt structure caps confidence for ambiguous/unanswerable queries.
    """

    def __init__(self):
        # Relation types: negation=-1, comparative=0/1, conditional=2, causal=3, ordering=4
        self.relation_map = {
            'negation': -1,
            'comparative_lt': 0,
            'comparative_gt': 1,
            'conditional': 2,
            'causal': 3,
            'ordering': 4
        }
        # Beta posterior parameters for bandit (alpha, beta) initialized to prior (1, 1)
        self.bandit_state = {} 

    def _extract_props_and_relations(self, text: str) -> Tuple[List[str], List[Tuple[int, int, int]]]:
        """Extract propositions and labeled relations from text."""
        text_lower = text.lower()
        props = []
        relations = []
        
        # Simple tokenizer for propositions based on connectors
        # We treat clauses separated by connectors as potential props
        connectors = [r'\bbecause\b', r'\bif\b', r'\bthen\b', r'\bleads to\b', r'\bresults in\b', 
                      r'\bgreater than\b', r'\bless than\b', r'\bis not\b', r'\bno\b', r'\bnot\b']
        
        # Split by common delimiters but keep track of context
        # For this implementation, we extract specific structural patterns as props
        pattern_nums = r'\d+(\.\d+)?\s*(?:kg|m|s|%|units)?'
        nums = re.findall(pattern_nums, text_lower)
        
        # Extract comparative statements
        comp_patterns = [
            (r'(\w+)\s+is\s+greater\s+than\s+(\w+)', 'gt'),
            (r'(\w+)\s+is\s+less\s+than\s+(\w+)', 'lt'),
            (r'(\w+)\s+>\s+(\w+)', 'gt'),
            (r'(\w+)\s+<\s+(\w+)', 'lt'),
            (r'if\s+(\w+),\s+then\s+(\w+)', 'cond'),
            (r'(\w+)\s+leads\s+to\s+(\w+)', 'causal'),
            (r'(\w+)\s+because\s+(\w+)', 'causal'), # Reversed causal direction usually
            (r'not\s+(\w+)', 'neg'),
            (r'no\s+(\w+)', 'neg')
        ]
        
        prop_set = set()
        rel_list = []
        
        # Add raw sentences as base props if no specific structure found
        sentences = [s.strip() for s in re.split(r'[.;]', text) if len(s.strip()) > 3]
        for s in sentences:
            if s not in prop_set:
                prop_set.add(s)
                props.append(s)
        
        # Add extracted structured props
        for pat, rtype in comp_patterns:
            matches = re.findall(pat, text_lower)
            for match in matches:
                if rtype == 'neg':
                    p = f"not {match[0]}"
                    if p not in prop_set:
                        prop_set.add(p)
                        props.append(p)
                else:
                    p1, p2 = match[0], match[1]
                    if p1 not in prop_set: prop_set.add(p1); props.append(p1)
                    if p2 not in prop_set: prop_set.add(p2); props.append(p2)
                    
                    if rtype == 'gt':
                        rel_list.append((p1, p2, 1)) # p1 > p2
                    elif rtype == 'lt':
                        rel_list.append((p1, p2, 0)) # p1 < p2
                    elif rtype == 'cond':
                        rel_list.append((p1, p2, 2))
                    elif rtype == 'causal':
                        rel_list.append((p1, p2, 3))

        # Map relations to indices
        prop_to_idx = {p: i for i, p in enumerate(props)}
        final_rels = []
        for p1, p2, rtype in rel_list:
            if p1 in prop_to_idx and p2 in prop_to_idx:
                final_rels.append((prop_to_idx[p1], prop_to_idx[p2], rtype))
                
        # Add generic adjacency for sequential sentences if no specific relations (loose coherence)
        if len(final_rels) == 0 and len(props) > 1:
            for i in range(len(props)-1):
                final_rels.append((i, i+1, 4)) # Ordering

        return props, final_rels

    def _propagate_beliefs(self, n_props: int, relations: List[Tuple[int, int, int]], precision: float = 2.0) -> np.ndarray:
        """GRN-style loopy belief propagation."""
        belief = np.full(n_props, 0.5)
        if n_props == 0:
            return belief
            
        adj = np.zeros((n_props, n_props))
        for i, j, rtype in relations:
            adj[i, j] = rtype + 2 # Offset to make non-negative for storage, handle logic separately
            
        max_iter = 20
        for _ in range(max_iter):
            old_belief = belief.copy()
            for i, j, rtype in relations:
                # R_ij logic
                support = 0.0
                if rtype == -1: # Negation
                    support = 1.0 - belief[i]
                elif rtype in [0, 1]: # Comparative (simplified: if i is true, j direction holds)
                    support = belief[i] 
                elif rtype == 2: # Conditional
                    support = belief[i] 
                elif rtype == 3: # Causal
                    support = belief[i]
                elif rtype == 4: # Ordering
                    support = belief[i]
                
                # Message
                m_ij = 1.0 / (1.0 + math.exp(-precision * (support - 0.5)))
                
                # Update j (simplified sum)
                belief[j] = 1.0 / (1.0 + math.exp(-(math.log(belief[j]/(1-belief[j]+1e-9)) + (m_ij - 0.5))))
                belief[j] = np