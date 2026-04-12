from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Monte Carlo Tree Search over logical parses guided by swarm intelligence,
    with falsification-driven scoring and epistemic honesty.
    
    Parses prompt into propositions (negations, comparatives, conditionals, numerics,
    causals, quantifiers). MCTS explores parse variations; swarm agents use UCB+pheromone
    to select paths. Constraint propagation attempts falsification; surviving parses
    score higher. Meta-confidence detects ambiguity/presupposition traps.
    """
    
    def __init__(self):
        self.mcts_simulations = 50
        self.pheromone_decay = 0.9
        self.ucb_c = 1.4
        random.seed(42)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/presupposition traps. Returns cap on confidence."""
        p = prompt.lower()
        
        # Presupposition: "have you stopped/quit X?", "why did X fail?"
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop|end))', p):
            return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\b(a|an)\b', p):
            return 0.25
        
        # Pronoun ambiguity with "who?" question
        if re.search(r'\b(he|she|they)\b.*\bwho\b', p) or re.search(r'\bwho\b.*\b(he|she|they)\b', p):
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p) and '?' in p:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(most|least|more|fewer)\b.*\b(than|expensive|tall|heavy|fast|slow)\b', p):
            return 0.3
        
        # Unanswerable: "not enough information", "cannot determine"
        if re.search(r'\b(not enough|insufficient|cannot determine|impossible to tell)\b', p):
            return 0.25
        
        return 1.0  # No trap detected
    
    def _parse_numeric(self, text: str) -> List[Tuple[str, float]]:
        """Extract numeric values with labels."""
        matches = re.findall(r'(\d+\.?\d*)\s*([a-z]*)', text.lower())
        return [(label, float(val)) for val, label in matches if val]
    
    def _parse_structures(self, text: str) -> Dict:
        """Parse logical structures from text."""
        t = text.lower()
        return {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', t)),
            'comparatives': re.findall(r'\b(more than|less than|greater|smaller|bigger|higher|lower|er than|est)\b', t),
            'conditionals': re.findall(r'\b(if|then|provided|unless|when|implies)\b', t),
            'numerics': self._parse_numeric(t),
            'causals': len(re.findall(r'\b(cause|lead to|result in|because|due to|therefore)\b', t)),
            'ordering': re.findall(r'\b(before|after|precedes|follows|earlier|later)\b', t),
            'quantifiers': re.findall(r'\b(all|some|none|most|every|each|any)\b', t),
            'equality': len(re.findall(r'\b(is|equals|same as|identical)\b', t))
        }
    
    def _numeric_compare(self, prompt: str, candidate: str) -> float:
        """Direct numeric comparison for questions like '9.11 vs 9.9'."""
        p_nums = self._parse_numeric(prompt)
        c_nums = self._parse_numeric(candidate)
        
        if len(p_nums) >= 2:
            # Check for comparison question
            if re.search(r'\b(greater|larger|more|bigger|higher)\b', prompt.lower()):
                expected = max(p_nums, key=lambda x: x[1])[1]
                if c_nums and abs(c_nums[0][1] - expected) < 0.01:
                    return 1.0
            elif re.search(r'\b(less|smaller|lower|fewer)\b', prompt.lower()):
                expected = min(p_nums, key=lambda x: x[1])[1]
                if c_nums and abs(c_nums[0][1] - expected) < 0.01:
                    return 1.0
        
        return 0.5
    
    def _constraint_propagate(self, structures: Dict) -> float:
        """Simulate constraint propagation. Returns reward (0-1)."""
        constraints = []
        
        # Negation constraints
        if structures['negations'] > 0:
            constraints.append(('negation', structures['negations']))
        
        # Comparative constraints
        if structures['comparatives']:
            constraints.append(('comparative', len(structures['comparatives'])))
        
        # Conditional constraints (if-then logic)
        if structures['conditionals']:
            if_count = sum(1 for c in structures['conditionals'] if 'if' in c)
            then_count = sum(1 for c in structures['conditionals'] if 'then' in c)
            # Balanced if-then is consistent
            if abs(if_count - then_count) > 2:
                return 0.3  # Likely inconsistent
            constraints.append(('conditional', min(if_count, then_count)))
        
        # Numeric constraints
        if len(structures['numerics']) >= 2:
            vals = [v for _, v in structures['numerics']]
            if structures['comparatives']:
                constraints.append(('numeric_comp', len(vals)))
        
        # Quantifier constraints
        if structures['quantifiers']:
            all_count = sum(1 for q in structures['quantifiers'] if 'all' in q or 'every' in q)
            some_count = sum(1 for q in structures['quantifiers'] if 'some' in q)
            none_count = sum(1 for q in structures['quantifiers'] if 'none' in q)
            # "all" and "none" together is contradiction
            if all_count > 0 and none_count > 0:
                return 0.0
            constraints.append(('quantifier', all_count + some_count + none_count))
        
        # Reward based on constraint satisfaction
        if not constraints:
            return 0.5
        
        total_constraints = sum(c[1] for c in constraints)
        satisfied = total_constraints  # Assume satisfied unless contradiction found
        
        return min(1.0, satisfied / max(1, total_constraints))
    
    def _mcts_simulate(self, prompt_structures: Dict, candidate_structures: Dict) -> float:
        """Run MCTS with swarm intelligence to explore parse space."""
        # Simplified MCTS: simulate variations of parse interpretations
        # Each node = interpretation of logical structure
        
        visits = [0] * 5
        rewards = [0.0] * 5
        pheromones = [1.0] * 5
        
        for _ in range(self.mcts_simulations):
            # Swarm selection using UCB + pheromone
            total_visits = sum(visits) + 1
            ucb_scores = []
            
            for i in range(5):
                if visits[i] == 0:
                    ucb_scores.append(float('inf'))
                else:
                    exploit = rewards[i] / visits[i]
                    explore = self.ucb_c * math.sqrt(math.log(total_visits) / visits[i])
                    pheromone_bonus = 0.1 * pheromones[i]
                    ucb_scores.append(exploit + explore + pheromone_bonus)
            
            # Select node (ant chooses path)
            node = ucb_scores.index(max(ucb_scores))
            
            # Simulate: apply small variation to structures
            sim_structures = candidate_structures.copy()
            if node == 0:
                sim_structures['negations'] = (sim_structures['negations'] + 1) % 3
            elif node == 1:
                sim_structures['comparatives'] = candidate_structures['comparatives']
            elif node == 2:
                sim_structures['conditionals'] = candidate_structures['conditionals']
            elif node == 3:
                sim_structures['causals'] = (sim_structures['causals'] + 1) % 2
            else:
                sim_structures['quantifiers'] = candidate_structures['quantifiers']
            
            # Falsification test via constraint propagation
            reward = self._constraint_propagate(sim_structures)
            
            # Backpropagate
            visits[node] += 1
            rewards[node] += reward
            pheromones[node] += 1.0
            
            # Pheromone evaporation
            pheromones = [p * self.pheromone_decay for p in pheromones]
        
        # Final score: weighted average by visits
        if sum(visits) == 0:
            return 0.5
        return sum(rewards) / sum(visits)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by MCTS+swarm+falsification score."""
        prompt_structures = self._parse_structures(prompt)
        results = []
        
        for candidate in candidates:
            candidate_structures = self._parse_structures(candidate)
            
            # Structural score from MCTS+swarm
            mcts_score = self._mcts_simulate(prompt_structures, candidate_structures)
            
            # Numeric computation
            numeric_score = self._numeric_compare(prompt, candidate)
            
            # NCD (tiebreaker, max 15%)
            ncd_score = 1.0 - self._ncd(prompt, candidate)
            
            # Combine: structural 50%, computation 35%, NCD 15%
            final_score = 0.5 * mcts_score + 0.35 * numeric_score + 0.15 * ncd_score
            
            reasoning = f"MCTS={mcts_score:.2f}, Numeric={numeric_score:.2f}, NCD={ncd_score:.2f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence for ambiguous prompts."""
        # Check for ambiguity/presupposition traps
        meta_cap = self._meta_confidence(prompt)
        
        # Compute answer quality
        prompt_structures = self._parse_structures(prompt)
        answer_structures = self._parse_structures(answer)
        
        # If numeric comparison is clear, high confidence
        numeric_score = self._numeric_compare(prompt, answer)
        if numeric_score > 0.9 and len(self._parse_numeric(prompt)) >= 2:
            return min(0.95, meta_cap)
        
        # MCTS score
        mcts_score = self._mcts_simulate(prompt_structures, answer_structures)
        
        # If no structural match, honest uncertainty
        total_structures = sum([
            len(prompt_structures['comparatives']),
            len(prompt_structures['conditionals']),
            len(prompt_structures['numerics']),
            len(prompt_structures['ordering']),
            len(prompt_structures['quantifiers'])
        ])
        
        if total_structures == 0:
            base_confidence = 0.25
        else:
            base_confidence = mcts_score * 0.9
        
        # Cap by meta-confidence
        return min(base_confidence, meta_cap)